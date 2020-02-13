# Copyright (C) 2017 The Sipwise Team - http://sipwise.com

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

import os
import logging
import urllib
import uuid
from yaml import load, Loader
from django.conf import settings
from repoapi.utils import openurl
from . import exceptions as err

logger = logging.getLogger(__name__)

project_url = (
    "{base}/job/{job}/buildWithParameters?"
    "token={token}&cause={cause}&branch={branch}&"
    "tag={tag}&release={release}&"
    "distribution={distribution}&uuid={uuid}&"
    "release_uuid={release_uuid}"
)


def trigger_build(
    project,
    release_uuid,
    trigger_release=None,
    trigger_branch_or_tag=None,
    trigger_distribution=None,
):
    params = {
        "base": settings.JENKINS_URL,
        "job": project,
        "token": urllib.parse.quote(settings.JENKINS_TOKEN),
        "cause": urllib.parse.quote(trigger_release),
        "branch": "none",
        "tag": "none",
        "release": urllib.parse.quote(trigger_release),
        "distribution": urllib.parse.quote(trigger_distribution),
        "uuid": uuid.uuid4(),
        "release_uuid": release_uuid,
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


class ReleaseConfig(object):
    def __init__(self, name):
        self.config_file = "{}.yml".format(name)
        self.config_path = os.path.join(
            settings.REPOS_SCRIPTS_CONFIG_DIR, self.config_file
        )
        try:
            with open(self.config_path) as f:
                self.config = load(f, Loader=Loader)
                self.jenkins_jobs = self.config["jenkins-jobs"]
        except IOError:
            msg = "could not read configuration file '{}'"
            raise err.NoConfigReleaseFile(msg.format(self.config_path))
        except KeyError:
            msg = "{} has no 'jenkins-jobs' info"
            raise err.NoJenkinsJobsInfo(msg.format(self.config_file))

    @property
    def build_deps(self):
        return self.jenkins_jobs.get("build_deps", dict())
