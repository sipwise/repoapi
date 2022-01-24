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
import structlog
from celery import shared_task
from django.apps import apps

from .utils import process_hotfix

logger = structlog.get_logger(__name__)


@shared_task(ignore_result=True)
def hotfix_released(jbi_id, path):
    JenkinsBuildInfo = apps.get_model("repoapi", "JenkinsBuildInfo")
    jbi = JenkinsBuildInfo.objects.get(pk=jbi_id)
    process_hotfix(str(jbi), jbi.projectname, path)
