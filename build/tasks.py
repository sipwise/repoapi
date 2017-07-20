# Copyright (C) 2017 The Sipwise Team - http://sipwise.com

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
from build.utils import trigger_build
from build.models.br import BuildRelease

logger = logging.getLogger(__name__)


@shared_task(ignore_result=True)
def build_release(uuid):
    instance = BuildRelease.objects.get(uuid=uuid)
    if instance.tag:
        branch_or_tag = "tag/%s" % instance.tag
    else:
        branch_or_tag = "branch/%s" % instance.branch
    for project in instance.projects_list:
        url = trigger_build(project, instance.uuid, instance.release,
                            trigger_branch_or_tag=branch_or_tag,
                            trigger_distribution=instance.distribution)
        logger.debug("%s triggered" % url)