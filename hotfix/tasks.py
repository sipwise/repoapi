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

import logging
from celery import shared_task
from django.conf import settings
from .utils import parse_changelog, create_note
from repoapi.models import JenkinsBuildInfo

logger = logging.getLogger(__name__)


@shared_task(ignore_result=True)
def hotfix_released(jbi_id, path):
    jbi = JenkinsBuildInfo.objects.get(pk=jbi_id)
    logger.info('hotfix_released[%s] %s', jbi, path)
    wids, changelog = parse_changelog(path)
    for wid in wids:
        create_note(wid, jbi.projectname, changelog.full_version)
