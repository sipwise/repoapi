# Copyright (C) 2017-2022 The Sipwise Team - http://sipwise.com
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
import re
import urllib
from os import walk
from pathlib import Path
from uuid import uuid4

import structlog
from natsort import humansorted
from yaml import load
from yaml import Loader

from . import exceptions as err
from .conf import settings
from repoapi.utils import open_jenkins_url

logger = structlog.get_logger(__name__)

_url = "{base}/job/{job}/buildWithParameters?" "token={token}&cause={cause}"
base_url = _url + "&uuid={uuid}&release_uuid={release_uuid}"
project_url = (
    base_url + "&branch={branch}&tag={tag}&release={release}&"
    "distribution={distribution}"
)
build_matrix_url = _url
copy_deps_url = base_url + "&release={release}&internal={internal}"
re_release = re.compile(r"^release-(mr[0-9]+\.[0-9]+(\.[0-9]+)?)$")
re_release_common = re.compile(r"^(release-)?(mr[0-9]+\.[0-9]+)(\.[0-9]+)?$")
re_release_trunk = re.compile(r"^release-trunk-(\w+)$")


def remove_from_textlist(br, orig, value):
    _list = getattr(br, f"{orig}_list")
    if value in _list:
        _list.remove(value)
        tl = ",".join(_list)
        if len(tl) > 0:
            setattr(br, orig, tl)
        else:
            setattr(br, orig, None)
        br.save()


def is_release_trunk(version):
    match = re_release_trunk.search(version)
    if match:
        value = match.group(1)
        if value != "weekly":
            return (True, value)
    return (False, None)


def get_simple_release(version):
    match = re_release.search(version.replace("-update", ""))
    if match:
        return match.group(1)
    if version == "release-trunk-weekly":
        return "trunk-weekly"
    elif version.startswith("release-trunk-"):
        return "trunk"


def get_common_release(version):
    match = re_release_common.search(version)
    if match:
        return match.group(2)
    if version.startswith("release-trunk-") or version in (
        "trunk",
        "trunk-weekly",
    ):
        return "master"


def trigger_build_matrix(br):
    params = {
        "base": settings.JENKINS_URL,
        "token": urllib.parse.quote(settings.JENKINS_TOKEN),
        "job": "weekly-build-matrix-trunk-weekly",
        "cause": "repoapi finished to build trunk-weekly",
    }
    url = _url.format(**params)
    if not br.append_triggered_job(params["job"]):
        logger.info("{} already triggered, skip".format(params["job"]))
        return
    if settings.DEBUG:
        logger.info(f"Debug mode, would trigger: {url}")
    else:
        open_jenkins_url(url)
    return "{base}/job/{job}/".format(**params)


def trigger_copy_deps(release, internal, release_uuid, uuid=None):
    if release.startswith("release-trunk-"):
        simple = release
    else:
        simple = get_simple_release(release)
    if uuid is None:
        uuid = uuid4()
    params = {
        "base": settings.JENKINS_URL,
        "token": urllib.parse.quote(settings.JENKINS_TOKEN),
        "job": "release-copy-debs-yml",
        "cause": release,
        "release": simple,
        "internal": str(internal).lower(),
        "uuid": uuid,
        "release_uuid": release_uuid,
    }
    url = copy_deps_url.format(**params)
    if settings.DEBUG:
        logger.info(f"Debug mode, would trigger: {url}")
    else:
        open_jenkins_url(url)
    return "{base}/job/{job}/".format(**params)


def trigger_build(
    project,
    release_uuid,
    trigger_release,
    trigger_branch_or_tag,
    trigger_distribution,
    uuid=None,
):
    if uuid is None:
        uuid = uuid4()
    params = {
        "base": settings.JENKINS_URL,
        "job": project,
        "token": urllib.parse.quote(settings.JENKINS_TOKEN),
        "cause": urllib.parse.quote(trigger_release),
        "branch": "none",
        "tag": "none",
        "release": urllib.parse.quote(trigger_release),
        "distribution": urllib.parse.quote(trigger_distribution),
        "uuid": uuid,
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
        logger.info(f"Debug mode, would trigger: {url}")
    else:
        open_jenkins_url(url)
    return "{base}/job/{job}/".format(**params)


class ReleaseConfig(object):
    class WannaBuild:
        def _step_deps(self, level):
            no_deps = dict()
            deps = dict()
            if level == 0:
                search_map = self.build_deps
            else:
                search_map = self.deps[level - 1]
            for name in search_map:
                flag = False
                for prj, values in search_map.items():
                    if name in values:
                        flag = True
                        deps[name] = search_map[name]
                        logger.debug(f"{name} has dependency on {prj}")
                        break
                if not flag:
                    no_deps[name] = search_map[name]
                    logger.debug(f"** {name} has NO dependency")
            self.deps.append(deps)
            self.list_deps.append(humansorted(deps.keys()))
            self.no_deps.append(no_deps)
            self.list_no_deps.append(humansorted(no_deps.keys()))

        def __init__(self, config, step):
            self.config = config
            self.list_no_deps = []
            self.list_deps = []
            self.no_deps = []
            self.deps = []
            self.step = step
            self.build_deps = self.config.build_deps
            level = 0
            while self.step - level >= 0:
                logger.debug(f"--- level:{level} ---")
                self._step_deps(level)
                level = level + 1

        def __iter__(self):
            return self

        def __next__(self):
            try:
                list_prj = self.list_no_deps[self.step]
            except IndexError:
                raise StopIteration

            if len(list_prj) > 0:
                return list_prj.pop(0)
            raise StopIteration

    def check_circular_dependencies(self):
        levels = self.levels_build_deps
        builds = list(self.build_deps.keys())
        logger.debug(f"builds:{builds} levels:{levels}")
        for vals in levels:
            for prj in vals:
                builds.remove(prj)
        if len(builds) > 0:
            raise err.CircularBuildDependencies(
                f"problems detected with {builds}"
            )

    @classmethod
    def load_config(cls, config_path):
        try:
            with open(config_path) as f:
                return load(f, Loader=Loader)
        except IOError:
            msg = "could not read configuration file '{}'"
            raise err.NoConfigReleaseFile(msg.format(config_path))

    @classmethod
    def supported_releases(cls):
        skip_files = ["{}.yml".format(x) for x in settings.BUILD_RELEASES_SKIP]
        res = []
        for root, dirs, files in walk(settings.BUILD_REPOS_SCRIPTS_CONFIG_DIR):
            if "trunk.yml" in files:
                files.remove("trunk.yml")
                cfg = cls.load_config(
                    settings.BUILD_REPOS_SCRIPTS_CONFIG_DIR / "trunk.yml"
                )
                for dist in cfg["distris"]:
                    res.append(dist)
            for name in files:
                path_name = Path(name)
                if path_name.suffix != ".yml":
                    continue
                if name not in skip_files:
                    res.append(path_name.stem)
        return humansorted(res, reverse=True)

    @classmethod
    def supported_releases_dict(cls):
        sr = cls.supported_releases()
        res = [
            {
                "release": version,
                "base": get_common_release(version),
            }
            for version in sr
        ]
        return humansorted(res, lambda x: x["release"], reverse=True)

    def _get_config(self, name, distribution=None):
        ok, self.distribution = is_release_trunk(name)
        if not ok and name == "trunk":
            self.distribution = distribution
        filename = get_simple_release(name)
        if filename is None:
            filename = name
        self.config_file = "{}.yml".format(filename)
        self.config_path = (
            settings.BUILD_REPOS_SCRIPTS_CONFIG_DIR / self.config_file
        )
        self.config = self.load_config(self.config_path)

    def __init__(self, name, distribution=None, config=None):
        if config is None:
            self._get_config(name, distribution)
        else:
            self.config_file = "fake.yml"
            self.config_path = "/dev/null"
            self.config = config
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
        self.check_circular_dependencies()

    def is_build_dep(self, prj: str) -> bool:
        return prj in self.build_deps.keys()

    @property
    def build_deps(self) -> dict:
        return self.jenkins_jobs.get("build_deps", dict())

    def wanna_build_deps(self, step=0):
        return ReleaseConfig.WannaBuild(self, step)

    @property
    def levels_build_deps(self) -> list:
        if getattr(self, "_levels_build_deps", None) is None:
            self._levels_build_deps = []
            step = 0
            deps = list(self.wanna_build_deps(step))
            while len(deps) > 0:
                self._levels_build_deps.append(deps)
                step = step + 1
                deps = list(self.wanna_build_deps(step))
        return self._levels_build_deps

    @property
    def branch(self):
        release = self.release
        if release in ("trunk", "release-trunk-weekly"):
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
            if dist == "release-trunk-weekly":
                return dist
            if dist.startswith("release-trunk-"):
                return "trunk"
            elif dist.startswith("release-"):
                return dist

    @property
    def debian_release(self):
        if self.distribution:
            return self.distribution
        return self.config["debian_release"]

    @property
    def projects(self):
        return self.jenkins_jobs["projects"]
