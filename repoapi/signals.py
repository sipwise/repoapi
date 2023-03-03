# Copyright (C) 2022-2023 The Sipwise Team - http://sipwise.com
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
from django.apps import apps
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models.wni import NoteInfo
from .tasks import get_jbi_files
from .utils import get_next_release
from .utils import regex_mrXXX
from release_dashboard.utils.build import is_ngcp_project

logger = structlog.get_logger(__name__)


@receiver(
    post_save, sender="repoapi.JenkinsBuildInfo", dispatch_uid="jbi_manage"
)
def jbi_manage(sender, **kwargs):
    if kwargs["created"]:
        instance = kwargs["instance"]
        if instance.is_job_url_allowed():
            get_jbi_files.delay(
                instance.pk, instance.jobname, instance.buildnumber
            )


def gerrit_repo_add(instance):
    if instance.param_ppa == "$ppa":
        logger.warn("ppa unset, skip removal")
        return
    GerritRepoInfo = apps.get_model("repoapi", "GerritRepoInfo")
    gri = GerritRepoInfo.objects
    ppa, created = gri.get_or_create(
        param_ppa=instance.param_ppa,
        gerrit_change=instance.gerrit_change,
        defaults={"projectname": instance.projectname},
    )
    structlog.contextvars.bind_contextvars(
        instance=str(instance),
        branch=instance.param_branch,
        ppa=str(ppa),
        last_activity=ppa.modified,
        gerrit_change=instance.gerrit_change,
    )
    if created:
        logger.info("ppa created")
    elif ppa.projectname == "unknown":
        ppa.projectname = instance.projectname
        ppa.save()
        logger.info("ppa projectname updated")
    else:
        ppa.save()
        logger.info("ppa last activity datetime saved")


def gerrit_repo_del(instance):
    if instance.param_ppa == "$ppa":
        logger.warn("ppa unset, skip removal")
        return
    GerritRepoInfo = apps.get_model("repoapi", "GerritRepoInfo")
    GerritRepoInfo.objects.review_removed(
        instance.param_ppa,
        instance.gerrit_change,
        instance.projectname,
        instance.id,
    )


@receiver(
    post_save,
    sender="repoapi.JenkinsBuildInfo",
    dispatch_uid="gerrit_repo_manage",
)
def gerrit_repo_manage(sender, **kwargs):
    if kwargs["created"]:
        instance = kwargs["instance"]
        structlog.contextvars.bind_contextvars(
            instance=str(instance),
            branch=instance.param_branch,
            ppa=instance.param_ppa,
        )
        if instance.param_ppa == "$ppa":
            logger.warn("ppa unset, skip")
            return
        if (
            instance.jobname.endswith("-repos")
            and instance.result == "SUCCESS"
        ):
            logger.info("we need to count this")
            if instance.gerrit_eventtype == "patchset-created":
                gerrit_repo_add(instance)
            elif instance.gerrit_eventtype == "change-merged":
                gerrit_repo_del(instance)
        elif (
            instance.jobname.endswith("-cleanup")
            and instance.result == "SUCCESS"
            and instance.gerrit_eventtype == "change-abandoned"
        ):
            logger.info("we need to count this")
            gerrit_repo_del(instance)
        elif (
            instance.jobname.endswith("-gerrit")
            and instance.result == "SUCCESS"
            and instance.gerrit_eventtype == "change-merged"
            and regex_mrXXX.match(instance.param_branch)
        ):
            logger.info("we need to count this")
            gerrit_repo_del(instance)


def tracker_release_target(instance, note: NoteInfo):
    if not is_ngcp_project(instance.projectname):
        logger.info(
            "{instance.projectname} not a NGCP project, skip release_target"
        )
        return
    branch = instance.param_branch
    if regex_mrXXX.search(branch):
        release = branch
    else:
        release = get_next_release(branch)
    if release:
        note.set_target_release(release)


def tracker_note_add(instance, message, release_target=False):
    model = NoteInfo.get_model()
    ids = model.getIds(instance.git_commit_msg)
    from django.conf import settings

    for id in ids:
        if not instance.gerrit_eventtype:
            change = model.getCommit(instance.git_commit_msg)
            url = settings.GITWEB_URL.format(instance.projectname, change)
            eventtype = "git-commit"
        else:
            change = instance.gerrit_change
            url = settings.GERRIT_URL.format(instance.gerrit_change)
            eventtype = instance.gerrit_eventtype
        note, created = NoteInfo.get_or_create(
            field_id=id, gerrit_change=change, eventtype=eventtype
        )
        if created:
            if not note.send(f"{message} {url} "):
                logger.error("remove related NoteInfo")
                note.delete()
            if release_target:
                tracker_release_target(instance, note)


def note_manager(sender, **kwargs):
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
                logger.info("build not triggered by gerrit, skip notes")
                return
            tracker_note_add(
                instance,
                msg % (instance.projectname, instance.param_branch),
                set_release_target,
            )
