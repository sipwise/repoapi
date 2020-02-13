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

from django.conf import settings

from build.models.br import BuildRelease
from build.utils import ReleaseConfig
from build.utils import trigger_build
from repoapi.celery import app

logger = logging.getLogger(__name__)


@app.task(bind=True)
def build_release(self, pk):
    br = BuildRelease.objects
    if settings.DEBUG:
        logger.info("pk:%s count:%d", pk, br.count())
    try:
        instance = br.get(id=pk)
    except BuildRelease.DoesNotExist as exc:
        raise self.retry(countdown=60 * 5, exc=exc)
    if instance.tag:
        branch_or_tag = "tag/%s" % instance.tag
    else:
        branch_or_tag = "branch/%s" % instance.branch
    rc = ReleaseConfig(instance.release)
    for project in rc.wanna_build_deps(1):
        url = trigger_build(
            project,
            instance.uuid,
            instance.release,
            trigger_branch_or_tag=branch_or_tag,
            trigger_distribution=instance.distribution,
        )
        logger.debug("%s triggered" % url)
