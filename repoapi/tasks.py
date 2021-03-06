# Copyright (C) 2016-2020 The Sipwise Team - http://sipwise.com
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
from pathlib import Path

import structlog
from celery import shared_task
from django.apps import apps

from .celery import app
from .celery import jbi_parse_hotfix
from .conf import settings
from .utils import is_download_artifacts
from .utils import jenkins_get_artifact
from .utils import jenkins_get_build
from .utils import jenkins_get_console
from .utils import jenkins_get_env
from .utils import jenkins_remove_project_ppa

logger = structlog.get_logger(__name__)


@app.task(bind=True)
def jenkins_remove_project(self, jbi_id):
    JenkinsBuildInfo = apps.get_model("repoapi", "JenkinsBuildInfo")
    jbi = JenkinsBuildInfo.objects.get(id=jbi_id)
    log = logger.bind(
        jbi=str(jbi),
    )
    if (
        jbi.jobname.endswith("-repos")
        and jbi.result == "SUCCESS"
        and jbi.gerrit_eventtype == "change-merged"
    ):
        try:
            jenkins_remove_project_ppa(jbi.param_ppa, jbi.source)
        except FileNotFoundError as exc:
            log.warn("source is not there yet, try again in 60 secs")
            raise self.retry(exc=exc, countdown=60)


@shared_task(ignore_result=True)
def jbi_get_artifact(jbi_id, jobname, buildnumber, artifact_info):
    path = Path(jenkins_get_artifact(jobname, buildnumber, artifact_info))
    if path.name == settings.HOTFIX_ARTIFACT:
        jbi_parse_hotfix.delay(jbi_id, str(path))


@shared_task(ignore_result=True)
def get_jbi_files(jbi_id, jobname, buildnumber):
    log = logger.bind(
        jbi_id=jbi_id,
        jobname=jobname,
        buildnumber=buildnumber,
    )
    jenkins_get_console(jobname, buildnumber)
    path_envVars = jenkins_get_env(jobname, buildnumber)
    path_build = jenkins_get_build(jobname, buildnumber)
    if is_download_artifacts(jobname):
        with open(path_build) as data_file:
            data = json.load(data_file)
        log.debug("job_info", data=data)
        for artifact in data["artifacts"]:
            jbi_get_artifact.delay(jbi_id, jobname, buildnumber, artifact)
    else:
        log.debug("skip artifacts download")
    if jobname in settings.RELEASE_CHANGED_JOBS:
        app.send_task(
            "release_changed.tasks.process_result", args=[jbi_id, path_envVars]
        )


@shared_task(ignore_result=True)
def jbi_purge(release, weeks):
    JenkinsBuildInfo = apps.get_model("repoapi", "JenkinsBuildInfo")
    JenkinsBuildInfo.objects.purge_release(release, timedelta(weeks=weeks))
    logger.info("purged release %s jbi older than %s weeks" % (release, weeks))
