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
import re

from django.db import models
from django.db.models import signals
from django.conf import settings
from repoapi import utils
from .tasks import get_jbi_files

logger = logging.getLogger(__name__)
workfront_re = re.compile(r"TT#(\d+)")
commit_re = re.compile(r"^(\w{7}) ")


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

    def release_project_uuids_set(self, release, project):
        res = self.get_queryset().filter(
            param_release=release, projectname=project).distinct()
        return res.order_by('projectname')

    def release_project_uuids(self, release, project, flat=True):
        res = self.get_queryset().filter(
            param_release=release, projectname=project).distinct()
        if flat:
            return res.order_by('projectname').values_list('tag', flat=True)
        else:
            return res.order_by('projectname').values('tag')

    def jobs_by_uuid(self, release, project, uuid):
        return self.get_queryset().filter(tag=uuid, param_release=release,
                                          projectname=project).order_by('date')

    def latest_uuid(self, release, project):
        qs = self.get_queryset()
        latest_uuid = qs.filter(
            param_release=release, projectname=project).latest('date')
        return {'tag': latest_uuid.tag, 'date': latest_uuid.date}


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
    git_commit_msg = models.TextField(null=True)

    objects = JenkinsBuildInfoManager()

    class Meta:
        index_together = [
            ["param_release", "projectname"],
            ["param_release", "projectname", "tag"],
        ]

    def __str__(self):
        return "%s:%d[%s]" % (self.jobname,
                              self.buildnumber, self.tag)

def jbi_manage(sender, **kwargs):
    if kwargs["created"]:
        instance = kwargs["instance"]
        get_jbi_files.delay(instance.jobname, instance.buildnumber)

signals.post_save.connect(jbi_manage, sender=JenkinsBuildInfo)

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

signals.post_save.connect(gerrit_repo_manage, sender=JenkinsBuildInfo)


class WorkfrontNoteInfo(models.Model):
    workfront_id = models.CharField(max_length=50, null=False)
    gerrit_change = models.CharField(max_length=50, null=False)
    eventtype = models.CharField(max_length=50, null=False)

    class Meta:
        unique_together = ["workfront_id", "gerrit_change", "eventtype"]

    @staticmethod
    def getIds(git_comment):
        """
        parses git_commit_msg searching for Workfront TT# ocurrences
        returns a list of IDs
        """
        if git_comment:
            res = workfront_re.findall(git_comment)
            return set(res)
        else:
            return set()

    @staticmethod
    def getCommit(git_comment):
        """
        parses git_commit_msg searching for short GIT_COMMIT
        """
        if git_comment:
            res = commit_re.search(git_comment)
            if res:
                return res.group(1)

    def __str__(self):
        return "%s:%s" % (self.workfront_id, self.gerrit_change)


def workfront_note_add(instance, message):
    wni = WorkfrontNoteInfo.objects
    workfront_ids = WorkfrontNoteInfo.getIds(instance.git_commit_msg)

    for wid in workfront_ids:
        if not instance.gerrit_eventtype:
            change = WorkfrontNoteInfo.getCommit(instance.git_commit_msg)
            url = settings.GITWEB_URL.format(instance.projectname, change)
            eventtype = 'git-commit'
        else:
            change = instance.gerrit_change
            url = settings.GERRIT_URL.format(instance.gerrit_change)
            eventtype = instance.gerrit_eventtype
        note, created = wni.get_or_create(
            workfront_id=wid,
            gerrit_change=change,
            eventtype=eventtype)
        if created:
            if not utils.workfront_note_send(wid, "%s %s" % (message, url)):
                logger.error("remove releated WorkfrontNoteInfo")
                note.delete()


def workfront_note_manage(sender, **kwargs):
    """
    <name>-get-code job is the first in the flow that has the proper
    GIT_CHANGE_SUBJECT envVar set, so git_commit_msg is fine
    """
    if kwargs["created"]:
        instance = kwargs["instance"]
        if instance.jobname.endswith("-get-code") and \
                instance.result == "SUCCESS":
            if instance.gerrit_eventtype == 'change-merged':
                msg = "review merged"
            elif instance.gerrit_eventtype == 'patchset-created':
                msg = "review created"
            else:
                msg = "commit created"
            workfront_note_add(instance, msg)


signals.post_save.connect(workfront_note_manage, sender=JenkinsBuildInfo)
