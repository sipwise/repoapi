# Copyright (C) 2015-2022 The Sipwise Team - http://sipwise.com
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
import urllib
import uuid

import structlog

from ..conf import settings
from ..models import Project
from gerrit.utils import get_gerrit_branches
from gerrit.utils import get_gerrit_tags
from repoapi.utils import open_jenkins_url

logger = structlog.get_logger(__name__)

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
    "push={push}&release_empty_hotfix={empty}&"
    "uuid={uuid}&remote_user={user}"
)


def trigger_hotfix(project, branch, user, push="yes", empty=False):
    flow_uuid = uuid.uuid4()
    if empty:
        empty_val = "true"
    else:
        empty_val = "false"
    params = {
        "base": settings.JENKINS_URL,
        "token": urllib.parse.quote(settings.JENKINS_TOKEN),
        "action": urllib.parse.quote("--hotfix"),
        "branch": urllib.parse.quote(branch),
        "project": urllib.parse.quote(project),
        "push": urllib.parse.quote(push),
        "empty": empty_val,
        "uuid": flow_uuid,
        "user": user.username,
    }

    url = hotfix_url.format(**params)
    if settings.DEBUG:
        logger.warn("Debug mode, would trigger: %s", url)
    else:
        open_jenkins_url(url)
    res = [
        "{}/job/release-tools-runner/".format(settings.JENKINS_URL),
        "/panel/release-{}-update/{}/latest/".format(branch, project),
    ]
    return res


def fetch_gerrit_info(projectname):
    project, _ = Project.objects.get_or_create(name=projectname)
    project.tags = get_gerrit_tags(projectname)
    project.branches = get_gerrit_branches(projectname)
    project.save()


def is_ngcp_project(projectname):
    if projectname in settings.RELEASE_DASHBOARD_PROJECTS:
        return True
    return False
