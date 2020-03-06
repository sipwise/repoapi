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

from .conf import settings
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
    if instance.release == "trunk":
        release = "release-trunk-{}".format(instance.distribution)
    else:
        release = instance.release
    url = trigger_copy_deps(
        release=release, internal=True, release_uuid=instance.uuid,
    )
    logger.info("%s triggered" % url)


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
    br.pool_size += 1
    logger.info("%s triggered" % url)


@shared_task(ignore_result=True)
def build_resume(pk):
    try:
        br = BuildRelease.objects.get(id=pk)
    except BuildRelease.DoesNotExist:
        logger.error("can't resume on unknown release with id:%s", pk)
        return
    params = {
        "release_uuid": br.uuid,
        "trigger_release": br.release,
        "trigger_branch_or_tag": br.branch_or_tag,
        "trigger_distribution": br.distribution,
    }
    size = settings.BUILD_POOL - br.pool_size
    if size <= 0:
        logger.info(
            "BuildRelease:%s No more room for new builds,"
            " wait for next slot",
            br,
        )
    for step in range(size):
        prj = br.next
        if prj:
            params["project"] = "{}-get-code".format(prj)
            logger.debug(
                "trigger:%s for BuildRelease:%s", params["project"], br
            )
            trigger_build(**params)
            br.append_triggered(prj)
        else:
            logger.debug("BuildRelease:%s has no next", br)
            break
