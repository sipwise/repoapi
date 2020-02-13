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
import logging

from django.db.models import signals

from .br import BuildRelease
from build.tasks import build_release
from build.utils import trigger_build
from repoapi.models import JenkinsBuildInfo

logger = logging.getLogger(__name__)


def br_manage(sender, **kwargs):
    if kwargs["created"]:
        instance = kwargs["instance"]
        build_release.delay(instance.pk)
        logger.debug("build_release for %d triggered", instance.pk)


def jbi_manage(sender, **kwargs):
    if kwargs["created"]:
        instance = kwargs["instance"]
        if not instance.is_job_url_allowed():
            return
        if (
            instance.param_release == "none"
            or instance.param_release_uuid is None
        ):
            return
        try:
            br = BuildRelease.objects.get(
                release=instance.param_release,
                uuid=instance.param_release_uuid,
            )
            br.append_built(instance)
            prj = br.next
            if prj:
                logger.debug("trigger:%s for BuildRelease:%s", prj, br)
                trigger_build(
                    prj,
                    br.uuid,
                    br.release,
                    br.uuid,
                    br.trigger_branch_or_tag,
                    br.distribution,
                )
        except BuildRelease.DoesNotExist:
            logger.error(
                "BuildRelease:%s[%s] not found",
                instance.param_release,
                instance.param_release_uuid,
            )


post_save = signals.post_save.connect
post_save(br_manage, sender=BuildRelease)
post_save(jbi_manage, sender=JenkinsBuildInfo)
