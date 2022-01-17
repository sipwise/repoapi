# Copyright (C) 2022 The Sipwise Team - http://sipwise.com
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
from django.db.models.signals import post_save
from django.dispatch import receiver

from . import utils
from .models import GerritRepoInfo
from .models import JenkinsBuildInfo
from .models import WorkfrontNoteInfo
from .models.wni import workfront_re_branch
from .tasks import get_jbi_files
from .tasks import jenkins_remove_project
from release_dashboard.utils.build import is_ngcp_project

logger = structlog.get_logger(__name__)


@receiver(post_save, sender=JenkinsBuildInfo, dispatch_uid="jbi_manage")
def jbi_manage(sender, **kwargs):
    if kwargs["created"]:
        instance = kwargs["instance"]
        if instance.is_job_url_allowed():
            get_jbi_files.delay(
                instance.pk, instance.jobname, instance.buildnumber
            )


def gerrit_repo_add(instance):
    log = logger.bind(
        instance=str(instance),
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
        log.debug("ppa created", ppa=str(ppa))
    elif ppa.projectname == "unknown":
        ppa.projectname = instance.projectname
        ppa.save()
        log.info("ppa projectname updated")


def gerrit_repo_del(instance):
    log = logger.bind(
        instance=str(instance),
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
        log.debug("removed ppa", ppa=str(ppa))
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


@receiver(
    post_save, sender=JenkinsBuildInfo, dispatch_uid="gerrit_repo_manage"
)
def gerrit_repo_manage(sender, **kwargs):
    if kwargs["created"]:
        instance = kwargs["instance"]
        log = logger.bind(
            instance=str(instance),
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
            log.debug("we need to count this")
            gerrit_repo_del(instance)


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
    from django.conf import settings

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
