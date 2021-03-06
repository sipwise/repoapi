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
import logging
import re

from django.db import models

from release_dashboard.utils.build import is_ngcp_project
from repoapi import utils
from repoapi.conf import settings

logger = logging.getLogger(__name__)
workfront_re = re.compile(r"TT#(\d+)")
workfront_re_branch = re.compile(r"^mr[0-9]+\.[0-9]+\.[0-9]+$")
commit_re = re.compile(r"^(\w{7}) ")


class WorkfrontNoteInfo(models.Model):
    workfront_id = models.CharField(max_length=50, null=False)
    gerrit_change = models.CharField(max_length=50, null=False)
    eventtype = models.CharField(max_length=50, null=False)

    class Meta:
        unique_together = ["workfront_id", "gerrit_change", "eventtype"]

    @staticmethod
    def getIds(git_comment):
        """
        parses git_commit_msg searching for Workfront TT# occurrences
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


def workfront_release_target(instance, wid):
    if not is_ngcp_project(instance.projectname):
        logger.info(
            "%s not a NGCP project, skip release_target", instance.projectname
        )
        return
    branch = instance.param_branch
    if workfront_re_branch.search(branch):
        release = branch
    else:
        release = utils.get_next_release(branch)
    if release:
        utils.workfront_set_release_target(wid, release)


def workfront_note_add(instance, message, release_target=False):
    wni = WorkfrontNoteInfo.objects
    workfront_ids = WorkfrontNoteInfo.getIds(instance.git_commit_msg)

    for wid in workfront_ids:
        if not instance.gerrit_eventtype:
            change = WorkfrontNoteInfo.getCommit(instance.git_commit_msg)
            url = settings.GITWEB_URL.format(instance.projectname, change)
            eventtype = "git-commit"
        else:
            change = instance.gerrit_change
            url = settings.GERRIT_URL.format(instance.gerrit_change)
            eventtype = instance.gerrit_eventtype
        note, created = wni.get_or_create(
            workfront_id=wid, gerrit_change=change, eventtype=eventtype
        )
        if created:
            if not utils.workfront_note_send(wid, "%s %s " % (message, url)):
                logger.error("remove related WorkfrontNoteInfo")
                note.delete()
            if release_target:
                workfront_release_target(instance, wid)


def workfront_note_manage(sender, **kwargs):
    """
    <name>-get-code job is the first in the flow that has the proper
    GIT_CHANGE_SUBJECT envVar set, so git_commit_msg is fine
    """
    if kwargs["created"]:
        instance = kwargs["instance"]
        if instance.result != "SUCCESS":
            return
        if instance.jobname.endswith("-get-code"):
            set_release_target = True
            if instance.gerrit_eventtype == "change-merged":
                msg = "%s.git[%s] review merged"
            elif instance.gerrit_eventtype == "patchset-created":
                msg = "%s.git[%s] review created"
                set_release_target = False
            else:
                msg = "%s.git[%s] commit created"
            workfront_note_add(
                instance,
                msg % (instance.projectname, instance.param_branch),
                set_release_target,
            )
