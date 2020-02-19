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

from django.conf import settings
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
        logger.debug("BuildRelease:%s triggered", instance)


def jbi_manage(sender, **kwargs):
    if not kwargs["created"]:
        return
    jbi = kwargs["instance"]
    if not jbi.is_job_url_allowed():
        return
    if jbi.param_release_uuid is None:
        return
    release = jbi.param_release
    if jbi.jobname == "release-copy-debs-yml":
        if not release.startswith("release-"):
            release = "release-{}".format(jbi.param_release)
    if jbi.param_release == "none":
        logger.debug(
            "jbi release:%s release_uuid:%s, no ReleaseBuild link, skip",
            jbi.param_release,
            jbi.param_release_uuid,
        )
        return
    try:
        br = BuildRelease.objects.get(
            release=release, uuid=jbi.param_release_uuid,
        )
    except BuildRelease.DoesNotExist:
        logger.error(
            "BuildRelease:%s[%s] not found",
            jbi.param_release,
            jbi.param_release_uuid,
        )
        return
    br.append_built(jbi)
    for step in range(settings.BUILD_POOL):
        prj = br.next
        if prj:
            jenkins_project = "{}-get-code".format(prj)
            logger.debug("trigger:%s for BuildRelease:%s", jenkins_project, br)
            trigger_build(
                jenkins_project,
                br.uuid,
                br.release,
                br.uuid,
                br.branch_or_tag,
                br.distribution,
            )


post_save = signals.post_save.connect
post_save(br_manage, sender=BuildRelease)
post_save(jbi_manage, sender=JenkinsBuildInfo)
