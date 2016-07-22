# Copyright (C) 2015 The Sipwise Team - http://sipwise.com

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

from django.db import models
from repoapi import utils

logger = logging.getLogger(__name__)


class GerritRepoInfo(models.Model):
    param_ppa = models.CharField(max_length=50, null=False)
    gerrit_change = models.CharField(max_length=50, null=False)

    class Meta:
        unique_together = ["param_ppa", "gerrit_change"]

    def __str__(self):
        return "%s:%s" % (self.param_ppa, self.gerrit_change)


def gerrit_repo_add(instance):
    gri = GerritRepoInfo.objects
    ppa, created = gri.get_or_create(
        param_ppa=instance.param_ppa,
        gerrit_change=instance.gerrit_change)
    if created:
        logging.info("%s created", ppa)


def gerrit_repo_del(instance):
    if instance.param_ppa == '$ppa':
        logger.warn("ppa unset, skip removal")
        return
    gri = GerritRepoInfo.objects
    try:
        ppa = gri.get(param_ppa=instance.param_ppa,
                      gerrit_change=instance.gerrit_change)
        ppa.delete()
        logger.info("removed %s", ppa)
    except GerritRepoInfo.DoesNotExist:
        pass
    if gri.filter(param_ppa=instance.param_ppa).count() == 0:
        utils.jenkins_remove_ppa(instance.param_ppa)


def gerrit_repo_manage(sender, **kwargs):
    if kwargs["created"]:
        instance = kwargs["instance"]
        if instance.jobname.endswith("-repos") and \
                instance.result == "SUCCESS":
            logger.info("we need to count this %s", instance.param_ppa)
            if instance.gerrit_eventtype == "patchset-created":
                gerrit_repo_add(instance)
            elif instance.gerrit_eventtype == "change-merged":
                gerrit_repo_del(instance)
        elif instance.jobname.endswith("-cleanup") and \
                instance.result == "SUCCESS" and \
                instance.gerrit_eventtype == "change-abandoned":
            logger.info("we need to count this %s", instance.param_ppa)
            gerrit_repo_del(instance)
