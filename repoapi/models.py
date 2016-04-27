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

from django.db import models
from django.db.models import signals
from repoapi import utils
import logging

logger = logging.getLogger(__name__)


class JenkinsBuildInfoManager(models.Manager):

    def releases(self, flat=True):
        res = self.get_queryset().values('param_release').distinct()
        if flat:
            return res.values_list('param_release', flat=True)
        else:
            return res.values('param_release')

    def release_projects(self, release, flat=True):
        res = self.get_queryset().filter(
            param_release=release).values('projectname').distinct()
        if flat:
            return res.values_list('projectname', flat=True)
        else:
            return res.values('projectname')

    def release_project_uuids(self, release, project, flat=True):
        res = self.get_queryset().filter(
            param_release=release, projectname=project).distinct()
        if flat:
            return res.order_by('projectname', '-date').values_list('tag', 'date', flat=True)
        else:
            return res.order_by('projectname', '-date').values('tag', 'date')

    def jobs_by_uuid(self, release, project, uuid, flat=True):
        res = self.get_queryset().filter(tag=uuid, param_release=release,
                                         projectname=project).order_by('date')
        if flat:
            return res.values_list('jobname', flat=True)
        else:
            return res.values('jobname')


class JenkinsBuildInfo(models.Model):
    tag = models.CharField(max_length=64, null=True)
    projectname = models.CharField(max_length=100)
    jobname = models.CharField(max_length=100)
    buildnumber = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    result = models.CharField(max_length=50)
    job_url = models.URLField()

    gerrit_patchset = models.CharField(max_length=50, null=True)
    gerrit_change = models.CharField(max_length=50, null=True)
    gerrit_eventtype = models.CharField(max_length=50, null=True)

    param_tag = models.CharField(max_length=50, null=True)
    param_branch = models.CharField(max_length=50, null=True)
    param_release = models.CharField(max_length=50, null=True,
                                     db_index=True)
    param_distribution = models.CharField(max_length=50, null=True)
    param_ppa = models.CharField(max_length=50, null=True)

    repo_name = models.CharField(max_length=50, null=True)

    objects = JenkinsBuildInfoManager()

    class Meta:
        index_together = [
            ["param_release", "projectname"],
            ["param_release", "projectname", "tag"],
        ]

    def __str__(self):
        return "%s:%d[%s]" % (self.jobname,
                              self.buildnumber, self.tag)


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
        logging.info("%s created" % ppa)


def gerrit_repo_del(instance):
    if instance.param_ppa == '$ppa':
        logger.warn("ppa unset, skip removal")
        return
    gri = GerritRepoInfo.objects
    try:
        ppa = gri.get(param_ppa=instance.param_ppa,
                      gerrit_change=instance.gerrit_change)
        ppa.delete()
        logger.info("removed %s" % ppa)
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

signals.post_save.connect(gerrit_repo_manage, sender=JenkinsBuildInfo)
