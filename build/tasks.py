# Copyright (C) 2017-2024 The Sipwise Team - http://sipwise.com
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

from .conf import settings
from .utils import trigger_build
from .utils import trigger_build_matrix
from .utils import trigger_copy_deps

logger = structlog.get_logger(__name__)


@shared_task(bind=True)
def build_release(self, pk):
    BuildRelease = apps.get_model("build", "BuildRelease")
    br = BuildRelease.objects
    try:
        instance = br.get(id=pk)
    except BuildRelease.DoesNotExist as exc:
        logger.warn("BuildRelease not found")
        raise self.retry(countdown=60 * 5, exc=exc)
    if instance.release in ["trunk", "trunk-next"]:
        release = "release-trunk-{}".format(instance.distribution)
    else:
        release = instance.release
    url = trigger_copy_deps(
        release=release, internal=True, release_uuid=instance.uuid
    )
    logger.info(
        "BuildRelease copy_deps triggered", instance=str(instance), url=url
    )


@shared_task(ignore_result=True)
def build_project(pk, project):
    BuildRelease = apps.get_model("build", "BuildRelease")
    try:
        br = BuildRelease.objects.get(id=pk)
    except BuildRelease.DoesNotExist:
        logger.error("can't trigger project on unknown release")
        return
    url = trigger_build(
        "{}-get-code".format(project),
        br.uuid,
        br.build_release,
        trigger_branch_or_tag=br.branch_or_tag,
        trigger_distribution=br.distribution,
    )
    br.pool_size += 1
    logger.info("project triggered", url=url, pool_size=br.pool_size)


@shared_task(ignore_result=True)
def build_resume(pk):
    BuildRelease = apps.get_model("build", "BuildRelease")
    try:
        br = BuildRelease.objects.get(id=pk)
    except BuildRelease.DoesNotExist:
        logger.error("can't resume on unknown release")
        return
    params = {
        "release_uuid": br.uuid,
        "trigger_release": br.build_release,
        "trigger_branch_or_tag": br.branch_or_tag,
        "trigger_distribution": br.distribution,
    }
    size = settings.BUILD_POOL - br.pool_size
    structlog.contextvars.bind_contextvars(
        size=size, pool_size=br.pool_size, br=str(br)
    )
    if size <= 0:
        logger.info("No more room for new builds, wait for next slot")
    for step in range(size):
        prj = br.next
        if prj:
            params["project"] = "{}-get-code".format(prj)
            logger.debug("trigger project", params=params)
            trigger_build(**params)
            br.append_triggered(prj)
        else:
            logger.debug("BuildRelease has no next")
            if not br.done:
                logger.debug("not done yet")
                continue
            if br.release == "release-trunk-weekly":
                url = trigger_build_matrix(br)
                if url is not None:
                    logger.info(
                        "build_matrix triggered", instance=str(br), url=url
                    )
            break
