# Copyright (C) 2015-2023 The Sipwise Team - http://sipwise.com
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
from django.db import models
from django_extensions.db.fields import CreationDateTimeField
from django_extensions.db.fields import ModificationDateTimeField

from ..tasks import jenkins_remove_project
from ..utils import jenkins_remove_ppa
from gerrit.utils import get_gerrit_change_url

logger = structlog.get_logger(__name__)


class GerritRepoInfoManager(models.Manager):
    def review_removed(self, ppa, gerrit_change, projectname, jbi_id=None):
        qs = self.get_queryset().filter(param_ppa=ppa)
        structlog.contextvars.bind_contextvars(
            ppa=ppa,
            gerrit_change=gerrit_change,
        )
        try:
            gri = qs.get(gerrit_change=gerrit_change)
            gri.delete()
            logger.info("removed gri")
        except GerritRepoInfo.DoesNotExist:
            logger.info("gri already gone")
            pass
        ppa_count = qs.count()
        project_ppa_count = qs.filter(projectname=projectname).count()
        if ppa_count == 0:
            logger.info("trigger ppa removal")
            jenkins_remove_ppa(ppa)
        elif project_ppa_count == 0 and jbi_id is not None:
            logger.info("remove source+packages from ppa")
            jenkins_remove_project.delay(jbi_id)
        else:
            logger.info(
                "nothing to do here",
                ppa_count=ppa_count,
                project_ppa_count=project_ppa_count,
            )


class GerritRepoInfo(models.Model):
    param_ppa = models.CharField(max_length=50, null=False)
    gerrit_change = models.CharField(max_length=50, null=False)
    projectname = models.CharField(max_length=100)
    created = CreationDateTimeField()
    modified = ModificationDateTimeField()
    objects = GerritRepoInfoManager()

    class Meta:
        unique_together = ["param_ppa", "gerrit_change"]

    @property
    def gerrit_url(self):
        return get_gerrit_change_url(self.gerrit_change, self.projectname)

    def __str__(self):
        return "{}:{}:{}".format(
            self.param_ppa, self.gerrit_change, self.projectname
        )
