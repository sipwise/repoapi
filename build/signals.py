# Copyright (C) 2022 The Sipwise Team - http://sipwise.com
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
from datetime import timedelta

import structlog
from django.apps import apps
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .conf import settings
from .tasks import build_release
from .tasks import build_resume

logger = structlog.get_logger(__name__)


@receiver(
    post_save, sender="build.BuildRelease", dispatch_uid="build_br_manage"
)
def br_manage(sender, **kwargs):
    if kwargs["created"]:
        instance = kwargs["instance"]
        if instance.release.endswith("-update"):
            build_resume.delay(instance.pk)
            logger.debug("BuildRelease:%s triggered", instance)
        elif timezone.now() > instance.start_date + timedelta(minutes=15):
            logger.debug(
                "BuildRelease:%s not triggered, is from the past:%s",
                instance,
                instance.start_date,
            )
        else:
            build_release.delay(instance.pk)
            logger.debug("BuildRelease:%s triggered", instance)


@receiver(
    post_save,
    sender="repoapi.JenkinsBuildInfo",
    dispatch_uid="build_jbi_manage",
)
def jbi_manage(sender, **kwargs):
    BuildRelease = apps.get_model("build", "BuildRelease")
    if not kwargs["created"]:
        return
    jbi = kwargs["instance"]
    if not jbi.is_job_url_allowed():
        return
    if jbi.param_release_uuid is None:
        return
    release = jbi.param_release
    log = logger.bind(
        release_uuid=jbi.param_release_uuid, release=jbi.param_release
    )
    if jbi.jobname in settings.BUILD_RELEASE_JOBS:
        if not release.startswith("release-"):
            release = "release-{}".format(jbi.param_release)
    if jbi.param_release_uuid in [None, "none", "", "$release_uuid"]:
        log.debug("no ReleaseBuild link, skip")
        return
    try:
        br = BuildRelease.objects.get(
            uuid=jbi.param_release_uuid,
        )
    except BuildRelease.DoesNotExist:
        log.error("BuildRelease not found")
        return
    if not br.append_built(jbi):
        log.debug("BuildRelease:%s jbi:%s skip", br, jbi)
        return
    br.remove_triggered(jbi)
    build_resume.delay(br.id)
