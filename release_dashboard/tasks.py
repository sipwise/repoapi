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
from release_dashboard.models import Project
from django.conf import settings
from .utils import get_gerrit_tags, get_gerrit_branches

logger = logging.getLogger(__name__)
rd_settings = settings.RELEASE_DASHBOARD_SETTINGS


@shared_task(ignore_result=True)
def gerrit_fetch_info(projectname):
    project, _ = Project.objects.get_or_create(name=projectname)
    project.tags = get_gerrit_tags(projectname)
    project.branches = get_gerrit_branches(projectname)
    project.save()


@shared_task(ignore_result=True)
def gerrit_fetch_all():
    for project in rd_settings['projects']:
        gerrit_fetch_info.delay(project)