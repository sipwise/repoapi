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
import logging
import os
import re
import urllib
import uuid
from pathlib import Path

from django.conf import settings
from yaml import load
from yaml import Loader

from . import exceptions as err
from repoapi.utils import openurl

logger = logging.getLogger(__name__)

project_url = (
    "{base}/job/{job}/buildWithParameters?"
    "token={token}&cause={cause}&branch={branch}&"
    "tag={tag}&release={release}&"
    "distribution={distribution}&uuid={uuid}&"
    "release_uuid={release_uuid}"
)

re_release = re.compile(r"release-(mr[0-9]+\.[0-9]+(\.[0-9]+)?)$")


def get_simple_release(version):
    match = re_release.search(version)
    if match:
        return match.group(1)
    if version.startswith("release-trunk-"):
        return "trunk"


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
        logger.info("Debug mode, would trigger: %s", url)
    else:
        openurl(url)
    return "{base}/job/{job}/".format(**params)


class ReleaseConfig(object):
    class WannaBuild:
        def __init__(self, config, step=1):
            self.config = config
            self.no_deps = []
            self.deps = []
            self.step = step
            build_deps = self.config.build_deps
            for name in build_deps.keys():
                flag = False
                for prj, values in build_deps.items():
                    if name in values:
                        flag = True
                        self.deps.append(name)
                        break
                if not flag:
                    self.no_deps.append(name)

        def __iter__(self):
            return self

        def __next__(self):
            if self.step == 0:
                list_prj = self.no_deps
            else:
                list_prj = self.deps

            if len(list_prj) > 0:
                return list_prj.pop(0)
            raise StopIteration

    @classmethod
    def supported_releases(cls):
        skip_files = ["{}.yml".format(x) for x in settings.RELEASES_SKIP]
        res = []
        for root, dirs, files in os.walk(settings.REPOS_SCRIPTS_CONFIG_DIR):
            for name in files:
                if name not in skip_files:
                    res.append(Path(name).stem)
        return res.sort()

    def __init__(self, name):
        filename = get_simple_release(name)
        if filename is None:
            filename = name
        self.config_file = "{}.yml".format(filename)
        self.config_path = os.path.join(
            settings.REPOS_SCRIPTS_CONFIG_DIR, self.config_file
        )
        try:
            with open(self.config_path) as f:
                self.config = load(f, Loader=Loader)
        except IOError:
            msg = "could not read configuration file '{}'"
            raise err.NoConfigReleaseFile(msg.format(self.config_path))
        try:
            self.jenkins_jobs = self.config["jenkins-jobs"]
        except KeyError:
            msg = "{} has no 'jenkins-jobs' info"
            raise err.NoJenkinsJobsInfo(msg.format(self.config_file))
        try:
            if self.release is None:
                raise err.NoReleaseInfo()
        except KeyError:
            msg = "{} has no 'distris' info"
            raise err.NoDistrisInfo(msg.format(self.config_file))

    @property
    def build_deps(self):
        return self.jenkins_jobs.get("build_deps", dict())

    def wanna_build_deps(self, step=0):
        return ReleaseConfig.WannaBuild(self, step)

    @property
    def branch(self):
        release = self.release
        if release.startswith("release-trunk-"):
            return "master"
        release_count = release.count(".")
        if release_count in [1, 2]:
            return get_simple_release(release)

    @property
    def tag(self):
        release = self.release
        release_count = release.count(".")
        if release_count == 2:
            return "{}.1".format(get_simple_release(release))

    @property
    def release(self):
        for dist in self.config["distris"]:
            if dist.startswith("release-"):
                return dist

    @property
    def debian_release(self):
        return self.config["debian_release"]

    @property
    def projects(self):
        return self.jenkins_jobs["projects"]
