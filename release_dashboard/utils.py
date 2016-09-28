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
import uuid
import urllib
import requests
from requests.auth import HTTPDigestAuth
from django.conf import settings
from repoapi.utils import openurl
from release_dashboard.models import Project

logger = logging.getLogger(__name__)

project_url = ("{base}/job/{job}/buildWithParameters?"
               "token={token}&cause={cause}&branch={branch}&"
               "tag={tag}&release={release}&"
               "distribution={distribution}&uuid={uuid}")

hotfix_url = ("{base}/job/release-tools-runner/buildWithParameters?"
              "token={token}&action={action}&branch={branch}&"
              "PROJECTNAME={project}&repository={project}&"
              "push={push}&uuid={uuid}")


def get_response(url):
    auth = HTTPDigestAuth(
        settings.GERRIT_REST_HTTP_USER,
        settings.GERRIT_REST_HTTP_PASSWD)
    response = requests.get(url, auth=auth)
    return response


def trigger_hotfix(project, branch, push="yes"):
    flow_uuid = uuid.uuid4()
    params = {
        "base": settings.JENKINS_URL,
        'token': urllib.quote(settings.JENKINS_TOKEN),
        'action': urllib.quote("--hotfix"),
        'branch': urllib.quote(branch),
        'project': urllib.quote(project),
        'push': urllib.quote(push),
        'uuid': flow_uuid,
    }

    url = hotfix_url.format(**params)
    if settings.DEBUG:
        logger.debug("Debug mode, would trigger: %s", url)
        # raise Exception("debug error")
    else:
        openurl(url)
    return "%s/job/release-tools-runner/" % settings.JENKINS_URL


def trigger_build(project, trigger_release=None,
                  trigger_branch_or_tag=None,
                  trigger_distribution=None):
    flow_uuid = uuid.uuid4()
    if trigger_branch_or_tag == "ignore":
        logger.debug("ignoring request to trigger project %s due"
                     " to request of version 'ignore'", project)
        return
    params = {
        'base': settings.JENKINS_URL,
        'job': project,
        'token': urllib.quote(settings.JENKINS_TOKEN),
        'cause': urllib.quote(trigger_release),
        'branch': 'none',
        'tag': 'none',
        'release': urllib.quote(trigger_release),
        'distribution': urllib.quote(trigger_distribution),
        'uuid': flow_uuid,
    }
    if trigger_branch_or_tag.startswith("tag/"):
        tag = trigger_branch_or_tag.split("tag/")[1]
        params['tag'] = urllib.quote(tag)
    elif trigger_branch_or_tag.startswith("branch/"):
        branch = trigger_branch_or_tag.split("branch/")[1]
        params['branch'] = urllib.quote(branch)
    else:
        params['branch'] = urllib.quote(trigger_branch_or_tag)

    url = project_url.format(**params)
    if settings.DEBUG:
        logger.debug("Debug mode, would trigger: %s", url)
    else:
        openurl(url)
    return "{base}/job/{job}/".format(**params)


def get_gerrit_info(url):
    if settings.DEBUG:
        logger.debug("Debug mode, would trigger: %s", url)
        return r")]}'\n[]"
    else:
        response = get_response(url)
        response.raise_for_status()
        return response.text


def get_tags(projectname, regex=None):
    project, _ = Project.objects.get_or_create(name=projectname)
    return project.filter_tags(regex)


def get_branches(projectname, regex=None):
    project, _ = Project.objects.get_or_create(name=projectname)
    return project.filter_branches(regex)


def get_gerrit_tags(project, regex=None):
    url = settings.GERRIT_URL.format("a/projects/%s/tags/" % project)
    return get_gerrit_info(url)


def get_gerrit_branches(project, regex=None):
    url = settings.GERRIT_URL.format("a/projects/%s/branches/" % project)
    return get_gerrit_info(url)
