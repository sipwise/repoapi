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
from celery import shared_task
from .utils import jenkins_get_console, jenkins_get_job, jenkins_get_artifact

logger = logging.getLogger(__name__)


@shared_task(ignore_result=True)
def jbi_get_artifact(jobname, buildnumber, artifact_info):
    jenkins_get_artifact(jobname, buildnumber, artifact_info)


@shared_task(ignore_result=True)
def get_jbi_files(jobname, buildnumber):
    jenkins_get_console(jobname, buildnumber)
    path = jenkins_get_job(jobname, buildnumber)
    with open(path) as data_file:
        data = json.load(data_file)
    logger.debug("job_info:%s", data)
    for artifact in data['artifacts']:
        jbi_get_artifact.delay(jobname, buildnumber, artifact)
