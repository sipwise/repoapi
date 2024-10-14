# Copyright (C) 2015-2024 The Sipwise Team - http://sipwise.com
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
import shutil
import subprocess
from pathlib import Path

import requests
import structlog
from django.apps import apps
from django.shortcuts import get_object_or_404
from requests.auth import HTTPBasicAuth

from .conf import settings

logger = structlog.get_logger(__name__)

regex_mrXXX = re.compile(r"^mr[0-9]+\.[0-9]+\.[0-9]+$")
regex_mrXX = re.compile(r"^mr[0-9]+\.[0-9]+$")
regex_mrXX_up = re.compile(r"^release-mr[0-9]+\.[0-9]+-update$")

JBI_CONSOLE_URL = "{}/job/{}/{}/consoleText"
JBI_BUILD_URL = "{}/job/{}/{}/api/json"
JBI_ARTIFACT_URL = "{}/job/{}/{}/artifact/{}"
JBI_ENVVARS_URL = "{}/job/{}/{}/injectedEnvVars/api/json"


def executeAndReturnOutput(command, env=None):
    proc = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env
    )
    stdoutdata, stderrdata = proc.communicate()
    logger.debug("command done", stdout=stdoutdata, stderr=stderrdata)
    return proc.returncode, stdoutdata, stderrdata


def get_jenkins_response(url):
    auth = HTTPBasicAuth(
        settings.JENKINS_HTTP_USER, settings.JENKINS_HTTP_PASSWD
    )
    response = requests.get(url, auth=auth)
    response.raise_for_status()
    return response


def dlfile(url, path: Path):
    structlog.contextvars.bind_contextvars(
        url=url,
        path=str(path),
    )
    if settings.DEBUG:
        logger.info("_NOT_ calling due to DEBUG is set")
    else:
        auth = HTTPBasicAuth(
            settings.JENKINS_HTTP_USER, settings.JENKINS_HTTP_PASSWD
        )
        logger.debug("get request")
        req = requests.get(url, auth=auth)
        with open(path, "wb") as local_file:
            for chunk in req.iter_content(chunk_size=128):
                local_file.write(chunk)


def open_jenkins_url(url):
    logger.debug("Trying to retrieve")
    try:
        res = get_jenkins_response(url)
        logger.debug("OK", status_code=res.status_code)
        return True
    except requests.HTTPError as e:
        logger.error("Error HTTP", error=str(e))
    except Exception as e:
        logger.error("Fatal error retrieving:", error=str(e))

    return False


def jenkins_remove_ppa(repo):
    url = (
        "%s/job/remove-reprepro-codename/buildWithParameters?"
        "token=%s&repository=%s"
        % (settings.JENKINS_URL, settings.JENKINS_TOKEN, repo)
    )
    structlog.contextvars.bind_contextvars(
        url=url,
    )
    if settings.DEBUG:
        logger.debug("_NOT_ calling due to DEBUG is set")
    else:
        open_jenkins_url(url)


def jenkins_remove_project_ppa(repo, source):
    url = (
        "%s/job/remove-reprepro-project/buildWithParameters?"
        "token=%s&repository=%s&source=%s"
        % (settings.JENKINS_URL, settings.JENKINS_TOKEN, repo, source)
    )
    structlog.contextvars.bind_contextvars(
        url=url,
    )
    if source is None:
        raise FileNotFoundError()
    if settings.DEBUG:
        logger.debug("_NOT_ calling due to DEBUG is set")
    else:
        open_jenkins_url(url)


def _jenkins_get(url, base_path: Path, filename) -> Path:
    base_path.mkdir(parents=True, exist_ok=True)
    path = base_path.joinpath(filename)
    structlog.contextvars.bind_contextvars(
        base_path=str(base_path),
        filename=filename,
        url=url,
    )
    logger.debug("download file from jenkins")
    dlfile(url, path)
    return path


def jenkins_get_console(jobname, buildnumber):
    url = JBI_CONSOLE_URL.format(settings.JENKINS_URL, jobname, buildnumber)
    base_path = settings.JBI_BASEDIR.joinpath(jobname, str(buildnumber))
    return _jenkins_get(url, base_path, "console.txt")


def jenkins_get_build(jobname, buildnumber):
    url = JBI_BUILD_URL.format(settings.JENKINS_URL, jobname, buildnumber)
    base_path = settings.JBI_BASEDIR.joinpath(jobname, str(buildnumber))
    return _jenkins_get(url, base_path, "build.json")


def jenkins_get_env(jobname, buildnumber):
    url = JBI_ENVVARS_URL.format(settings.JENKINS_URL, jobname, buildnumber)
    base_path = settings.JBI_BASEDIR.joinpath(jobname, str(buildnumber))
    return _jenkins_get(url, base_path, "envVars.json")


def jenkins_get_artifact(jobname, buildnumber, artifact_info):
    url = JBI_ARTIFACT_URL.format(
        settings.JENKINS_URL,
        jobname,
        buildnumber,
        artifact_info["relativePath"],
    )
    base_path = settings.JBI_BASEDIR.joinpath(
        jobname, str(buildnumber), "artifact"
    )
    return _jenkins_get(url, base_path, artifact_info["fileName"])


def get_next_release(branch):
    command = ["/usr/bin/meta-release-helper", "--next-release", branch]
    res = executeAndReturnOutput(command)
    if res[0] != 0:
        logger.error(
            "can't find out next release version", stdout=res[1], stderr=res[2]
        )
        return None
    val = res[1].rstrip()
    if len(val) > 0:
        # py2 vs py3: convert to string iff it's a bytes object,
        # otherwise it should be a string object already (as with
        # py2 as well as the mocking/patching as being done in test_utils.py)
        if type(val) is bytes:
            return val.decode("utf-8")
        else:
            return val

    else:
        return None


def get_build_release(release_uuid):
    BuildRelease = apps.get_model("build", "BuildRelease")
    br = get_object_or_404(BuildRelease, uuid=release_uuid)
    return br.build_release


def is_download_artifacts(jobname):
    if jobname in settings.JBI_ARTIFACT_JOBS:
        return True
    for check in settings.REPOAPI_ARTIFACT_JOB_REGEX:
        if re.search(check, jobname) is not None:
            return True
    return False


def cleanup_build(build_path: Path, dst_path: Path):
    if not dst_path.exists():
        dst_path.mkdir(parents=True, exist_ok=True)
    if build_path.exists():
        shutil.move(build_path, dst_path)
        logger.info(f"{build_path} stored at {dst_path}")
