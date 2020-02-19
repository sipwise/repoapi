# Copyright (C) 2017 The Sipwise Team - http://sipwise.com
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
import logging

from celery import shared_task

from build.models.br import BuildRelease
from build.utils import trigger_build
from build.utils import trigger_copy_deps
from repoapi.celery import app

logger = logging.getLogger(__name__)


@app.task(bind=True)
def build_release(self, pk):
    br = BuildRelease.objects
    try:
        instance = br.get(id=pk)
    except BuildRelease.DoesNotExist as exc:
        raise self.retry(countdown=60 * 5, exc=exc)
    url = trigger_copy_deps(
        release=instance.release, internal=True, release_uuid=instance.uuid,
    )
    logger.debug("%s triggered" % url)


@shared_task(ignore_result=True)
def build_project(pk, project):
    try:
        br = BuildRelease.objects.get(id=pk)
    except BuildRelease.DoesNotExist:
        logger.error(
            "can't trigger %s on unknown release with id:%s", project, pk
        )
        return
    url = trigger_build(
        "{}-get-code".format(project),
        br.uuid,
        br.release,
        trigger_branch_or_tag=br.branch_or_tag,
        trigger_distribution=br.distribution,
    )
    logger.debug("%s triggered" % url)
