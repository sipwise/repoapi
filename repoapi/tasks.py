# Copyright (C) 2016 The Sipwise Team - http://sipwise.com

# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.

# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import absolute_import

import json
import logging
from os.path import basename
from celery import shared_task
from django.conf import settings
from .celery import jbi_parse_hotfix
from .utils import jenkins_get_console, jenkins_get_artifact
from .utils import jenkins_get_build, jenkins_get_env

logger = logging.getLogger(__name__)


@shared_task(ignore_result=True)
def jbi_get_artifact(jbi_id, jobname, buildnumber, artifact_info):
    path = jenkins_get_artifact(jobname, buildnumber, artifact_info)
    if basename(path) == settings.HOTFIX_ARTIFACT:
        jbi_parse_hotfix.delay(jbi_id, path)


@shared_task(ignore_result=True)
def get_jbi_files(jbi_id, jobname, buildnumber):
    jenkins_get_console(jobname, buildnumber)
    jenkins_get_env(jobname, buildnumber)
    path_build = jenkins_get_build(jobname, buildnumber)
    if jobname in settings.JBI_ARTIFACT_JOBS:
        with open(path_build) as data_file:
            data = json.load(data_file)
        logger.debug("job_info:%s", data)
        for artifact in data['artifacts']:
            jbi_get_artifact.delay(jbi_id, jobname, buildnumber, artifact)
    else:
        logger.debug("skip artifacts download for jobname: %s", jobname)
