# Copyright (C) 2017-2022 The Sipwise Team - http://sipwise.com
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
    log = logger.bind(pk=pk)
    br = BuildRelease.objects
    try:
        instance = br.get(id=pk)
    except BuildRelease.DoesNotExist as exc:
        log.warn("BuildRelease not found")
        raise self.retry(countdown=60 * 5, exc=exc)
    if instance.release == "trunk":
        release = "release-trunk-{}".format(instance.distribution)
    else:
        release = instance.release
    url = trigger_copy_deps(
        release=release, internal=True, release_uuid=instance.uuid
    )
    log.info(
        "BuildRelease copy_deps triggered", instance=str(instance), url=url
    )


@shared_task(ignore_result=True)
def build_project(pk, project):
    BuildRelease = apps.get_model("build", "BuildRelease")
    log = logger.bind(project=project, pk=pk)
    try:
        br = BuildRelease.objects.get(id=pk)
    except BuildRelease.DoesNotExist:
        log.error("can't trigger project on unknown release")
        return
    url = trigger_build(
        "{}-get-code".format(project),
        br.uuid,
        br.release,
        trigger_branch_or_tag=br.branch_or_tag,
        trigger_distribution=br.distribution,
    )
    br.pool_size += 1
    log.info("project triggered", url=url, pool_size=br.pool_size)


@shared_task(ignore_result=True)
def build_resume(pk):
    BuildRelease = apps.get_model("build", "BuildRelease")
    log = logger.bind(pk=pk)
    try:
        br = BuildRelease.objects.get(id=pk)
    except BuildRelease.DoesNotExist:
        log.error("can't resume on unknown release")
        return
    params = {
        "release_uuid": br.uuid,
        "trigger_release": br.release,
        "trigger_branch_or_tag": br.branch_or_tag,
        "trigger_distribution": br.distribution,
    }
    size = settings.BUILD_POOL - br.pool_size
    log.bind(size=size, pool_size=br.pool_size, br=str(br))
    if size <= 0:
        log.info("No more room for new builds, wait for next slot")
    for step in range(size):
        prj = br.next
        if prj:
            params["project"] = "{}-get-code".format(prj)
            log.debug("trigger project", project=params["project"])
            trigger_build(**params)
            br.append_triggered(prj)
        else:
            log.debug("BuildRelease has no next")
            if br.release == "release-trunk-weekly":
                url = trigger_build_matrix(br)
                if url is not None:
                    log.info(
                        "build_matrix triggered", instance=str(br), url=url
                    )
            break
