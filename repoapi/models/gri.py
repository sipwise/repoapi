# Copyright (C) 2015-2020 The Sipwise Team - http://sipwise.com
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

from repoapi import utils
from repoapi.tasks import jenkins_remove_project

logger = structlog.get_logger(__name__)


class GerritRepoInfo(models.Model):
    param_ppa = models.CharField(max_length=50, null=False)
    gerrit_change = models.CharField(max_length=50, null=False)
    projectname = models.CharField(max_length=100)

    class Meta:
        unique_together = ["param_ppa", "gerrit_change"]

    def __str__(self):
        return "{}:{}:{}".format(
            self.param_ppa, self.gerrit_change, self.projectname
        )


def gerrit_repo_add(instance):
    log = logger.bind(
        instance=instance,
    )
    if instance.param_ppa == "$ppa":
        log.warn("ppa unset, skip removal")
        return
    gri = GerritRepoInfo.objects
    ppa, created = gri.get_or_create(
        param_ppa=instance.param_ppa,
        gerrit_change=instance.gerrit_change,
        defaults={"projectname": instance.projectname},
    )
    if created:
        log.debug("ppa created", ppa=ppa)
    elif ppa.projectname == "unknown":
        ppa.projectname = instance.projectname
        ppa.save()
        log.info("ppa projectname updated")


def gerrit_repo_del(instance):
    log = logger.bind(
        instance=instance,
    )
    if instance.param_ppa == "$ppa":
        log.warn("ppa unset, skip removal")
        return
    gri = GerritRepoInfo.objects
    try:
        ppa = gri.get(
            param_ppa=instance.param_ppa, gerrit_change=instance.gerrit_change
        )
        ppa.delete()
        log.debug("removed ppa", ppa=ppa)
    except GerritRepoInfo.DoesNotExist:
        pass
    qs = gri.filter(param_ppa=instance.param_ppa)
    ppa_count = qs.count()
    project_ppa_count = qs.filter(projectname=instance.projectname).count()
    if ppa_count == 0:
        utils.jenkins_remove_ppa(instance.param_ppa)
    elif project_ppa_count == 0:
        log.debug("remove source+packages from ppa")
        jenkins_remove_project.delay(instance.id)
    else:
        log.debug(
            "nothing to do here",
            ppa_count=ppa_count,
            project_ppa_count=project_ppa_count,
        )


def gerrit_repo_manage(sender, **kwargs):
    if kwargs["created"]:
        instance = kwargs["instance"]
        log = logger.bind(
            instance=instance,
            ppa=instance.param_ppa,
        )
        if instance.param_ppa == "$ppa":
            log.warn("ppa unset, skip")
            return
        if (
            instance.jobname.endswith("-repos")
            and instance.result == "SUCCESS"
        ):
            logger.debug("we need to count this")
            if instance.gerrit_eventtype == "patchset-created":
                gerrit_repo_add(instance)
            elif instance.gerrit_eventtype == "change-merged":
                gerrit_repo_del(instance)
        elif (
            instance.jobname.endswith("-cleanup")
            and instance.result == "SUCCESS"
            and instance.gerrit_eventtype == "change-abandoned"
        ):
            logger.debug("we need to count this")
            gerrit_repo_del(instance)
