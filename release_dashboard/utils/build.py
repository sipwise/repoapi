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
import urllib
import uuid

import requests
from requests.auth import HTTPBasicAuth

from ..conf import settings
from ..models import Project
from repoapi.utils import openurl

logger = logging.getLogger(__name__)

project_url = (
    "{base}/job/{job}/buildWithParameters?"
    "token={token}&cause={cause}&branch={branch}&"
    "tag={tag}&release={release}&"
    "distribution={distribution}&uuid={uuid}"
)

hotfix_url = (
    "{base}/job/release-tools-runner/buildWithParameters?"
    "token={token}&action={action}&branch={branch}&"
    "PROJECTNAME={project}&repository={project}&"
    "push={push}&uuid={uuid}&remote_user={user}"
)


def get_response(url):
    auth = HTTPBasicAuth(
        settings.GERRIT_REST_HTTP_USER, settings.GERRIT_REST_HTTP_PASSWD
    )
    response = requests.get(url, auth=auth)
    return response


def trigger_hotfix(project, branch, user, push="yes"):
    flow_uuid = uuid.uuid4()
    params = {
        "base": settings.JENKINS_URL,
        "token": urllib.parse.quote(settings.JENKINS_TOKEN),
        "action": urllib.parse.quote("--hotfix"),
        "branch": urllib.parse.quote(branch),
        "project": urllib.parse.quote(project),
        "push": urllib.parse.quote(push),
        "uuid": flow_uuid,
        "user": user.username,
    }

    url = hotfix_url.format(**params)
    if settings.DEBUG:
        logger.warn("Debug mode, would trigger: %s", url)
    else:
        openurl(url)
    return "%s/job/release-tools-runner/" % settings.JENKINS_URL


def trigger_build(
    project,
    trigger_release=None,
    trigger_branch_or_tag=None,
    trigger_distribution=None,
    flow_uuid=uuid.uuid4(),
):
    if trigger_branch_or_tag == "ignore":
        logger.debug(
            "ignoring request to trigger project %s due"
            " to request of version 'ignore'",
            project,
        )
        return
    params = {
        "base": settings.JENKINS_URL,
        "job": project,
        "token": urllib.parse.quote(settings.JENKINS_TOKEN),
        "cause": urllib.parse.quote(trigger_release),
        "branch": "none",
        "tag": "none",
        "release": urllib.parse.quote(trigger_release),
        "distribution": urllib.parse.quote(trigger_distribution),
        "uuid": flow_uuid,
    }
    if trigger_branch_or_tag.startswith("tag/"):
        tag = trigger_branch_or_tag.split("tag/")[1]
        params["tag"] = urllib.parse.quote(tag)

        # branch is like tag but removing the last element,
        # e.g. tag=mr5.5.2.1 -> branch=mr5.5.2
        branch = ".".join(tag.split(".")[0:-1])
        params["branch"] = urllib.parse.quote(branch)
    elif trigger_branch_or_tag.startswith("branch/"):
        branch = trigger_branch_or_tag.split("branch/")[1]
        params["branch"] = urllib.parse.quote(branch)
    else:
        params["branch"] = urllib.parse.quote(trigger_branch_or_tag)

    url = project_url.format(**params)
    if settings.DEBUG:
        logger.debug("Debug mode, would trigger: %s", url)
    else:
        openurl(url)
    return "{base}/job/{job}/".format(**params)


def fetch_gerrit_info(projectname):
    project, _ = Project.objects.get_or_create(name=projectname)
    project.tags = get_gerrit_tags(projectname)
    project.branches = get_gerrit_branches(projectname)
    project.save()


def get_gerrit_info(url):
    if settings.DEBUG:
        logger.debug("Debug mode, would trigger: %s", url)
        return r")]}'\n[]"
    else:
        response = get_response(url)
        response.raise_for_status()
        return response.text


def get_gerrit_tags(project, regex=None):
    url = settings.GERRIT_URL.format("a/projects/%s/tags/" % project)
    return get_gerrit_info(url)


def get_gerrit_branches(project, regex=None):
    url = settings.GERRIT_URL.format("a/projects/%s/branches/" % project)
    return get_gerrit_info(url)


def is_ngcp_project(projectname):
    if projectname in settings.RELEASE_DASHBOARD_PROJECTS:
        return True
    return False
