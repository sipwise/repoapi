# Copyright (C) 2016-2022 The Sipwise Team - http://sipwise.com
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
import json
from datetime import timedelta

import structlog
from celery import shared_task
from django.apps import apps

from .celery import jbi_parse_buildinfo
from .celery import jbi_parse_hotfix
from .celery import process_result
from .conf import settings
from .utils import is_download_artifacts
from .utils import jenkins_get_artifact
from .utils import jenkins_get_build
from .utils import jenkins_get_console
from .utils import jenkins_get_env
from .utils import jenkins_remove_project_ppa
from tracker.conf import Tracker

logger = structlog.get_logger(__name__)


@shared_task(bind=True)
def jenkins_remove_project(self, jbi_id):
    JenkinsBuildInfo = apps.get_model("repoapi", "JenkinsBuildInfo")
    jbi = JenkinsBuildInfo.objects.get(id=jbi_id)
    structlog.contextvars.bind_contextvars(
        jbi=str(jbi),
        result=jbi.result,
        gerrit_eventtype=jbi.gerrit_eventtype,
    )
    if (
        jbi.jobname.endswith("-repos")
        and jbi.result == "SUCCESS"
        and jbi.gerrit_eventtype == "change-merged"
    ):
        try:
            jenkins_remove_project_ppa(jbi.param_ppa, jbi.source)
            logger.info("triggered job for removal")
        except FileNotFoundError as exc:
            logger.warn("source is not there yet, try again in 60 secs")
            raise self.retry(exc=exc, countdown=60)
    else:
        logger.info("skip removal")


@shared_task(ignore_result=True)
def jbi_get_artifact(jbi_id, jobname, buildnumber, artifact_info):
    path = jenkins_get_artifact(jobname, buildnumber, artifact_info)
    if path.name == settings.HOTFIX_ARTIFACT:
        if settings.TRACKER_PROVIDER == Tracker.NONE:
            logger.info("no tracker defined, skip hotfix management")
            return
        jbi_parse_hotfix.delay(jbi_id, str(path))


@shared_task(ignore_result=True)
def get_jbi_files(jbi_id, jobname, buildnumber):
    jenkins_get_console(jobname, buildnumber)
    path_envVars = jenkins_get_env(jobname, buildnumber)
    path_build = jenkins_get_build(jobname, buildnumber)
    jbi_parse_buildinfo.delay(jbi_id, str(path_build))
    if is_download_artifacts(jobname):
        with open(path_build) as data_file:
            data = json.load(data_file)
        logger.debug("job_info", data=data)
        for artifact in data["artifacts"]:
            jbi_get_artifact.delay(jbi_id, jobname, buildnumber, artifact)
    else:
        logger.debug("skip artifacts download")
    if jobname in settings.RELEASE_CHANGED_JOBS:
        process_result.delay(jbi_id, str(path_envVars))


@shared_task(ignore_result=True)
def jbi_purge(release, weeks):
    JenkinsBuildInfo = apps.get_model("repoapi", "JenkinsBuildInfo")
    JenkinsBuildInfo.objects.purge_release(release, timedelta(weeks=weeks))
    logger.info(f"purged release {release} jbi older than {weeks} weeks")
