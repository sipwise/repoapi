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
import os
import re
import shutil
import subprocess
from distutils.dir_util import mkpath

import requests
from requests.auth import HTTPBasicAuth

from .conf import settings

logger = logging.getLogger(__name__)

JBI_CONSOLE_URL = "{}/job/{}/{}/consoleText"
JBI_BUILD_URL = "{}/job/{}/{}/api/json"
JBI_ARTIFACT_URL = "{}/job/{}/{}/artifact/{}"
JBI_ENVVARS_URL = "{}/job/{}/{}/injectedEnvVars/api/json"


def executeAndReturnOutput(command, env=None):
    proc = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env
    )
    stdoutdata, stderrdata = proc.communicate()
    logger.debug("<stdout>%s</stdout>", stdoutdata)
    logger.debug("<strerr>%s</stderr>", stderrdata)
    return proc.returncode, stdoutdata, stderrdata


def get_jenkins_response(url):
    auth = HTTPBasicAuth(
        settings.JENKINS_HTTP_USER, settings.JENKINS_HTTP_PASSWD
    )
    response = requests.get(url, auth=auth)
    response.raise_for_status()
    return response


def dlfile(url, path):
    if settings.DEBUG:
        logger.info("I would call %s", url)
    else:
        auth = HTTPBasicAuth(
            settings.JENKINS_HTTP_USER, settings.JENKINS_HTTP_PASSWD
        )
        logger.debug("url:[%s]", url)
        with requests.get(url, auth=auth, stream=True) as req:
            with open(path, "wb") as local_file:
                shutil.copyfileobj(req.raw, local_file)


def open_jenkins_url(url):
    logger.debug("Trying to retrieve url: [%s]", url)
    try:
        res = get_jenkins_response(url)
        logger.debug("OK[{}] URL[{}]".format(res.status_code, url))
        return True
    except requests.HTTPError as e:
        logger.error(
            "Error[{}] retrieving URL[{}]: {}".format(res.status_code, url, e)
        )
    except Exception as e:
        logger.error("Fatal error retrieving URL[{}]: {}".format(url, e))

    return False


def jenkins_remove_ppa(repo):
    url = (
        "%s/job/remove-reprepro-codename/buildWithParameters?"
        "token=%s&repository=%s"
        % (settings.JENKINS_URL, settings.JENKINS_TOKEN, repo)
    )
    if settings.DEBUG:
        logger.debug("I would call %s", url)
    else:
        open_jenkins_url(url)


def _jenkins_get(url, base_path, filename):
    mkpath(base_path)
    path = os.path.join(base_path, filename)
    logger.debug("url:[%s] path[%s]", url, path)
    dlfile(url, path)
    return path


def jenkins_get_console(jobname, buildnumber):
    url = JBI_CONSOLE_URL.format(settings.JENKINS_URL, jobname, buildnumber)
    base_path = os.path.join(settings.JBI_BASEDIR, jobname, str(buildnumber))
    return _jenkins_get(url, base_path, "console.txt")


def jenkins_get_build(jobname, buildnumber):
    url = JBI_BUILD_URL.format(settings.JENKINS_URL, jobname, buildnumber)
    base_path = os.path.join(settings.JBI_BASEDIR, jobname, str(buildnumber))
    return _jenkins_get(url, base_path, "build.json")


def jenkins_get_env(jobname, buildnumber):
    url = JBI_ENVVARS_URL.format(settings.JENKINS_URL, jobname, buildnumber)
    base_path = os.path.join(settings.JBI_BASEDIR, jobname, str(buildnumber))
    return _jenkins_get(url, base_path, "envVars.json")


def jenkins_get_artifact(jobname, buildnumber, artifact_info):
    url = JBI_ARTIFACT_URL.format(
        settings.JENKINS_URL,
        jobname,
        buildnumber,
        artifact_info["relativePath"],
    )
    base_path = os.path.join(
        settings.JBI_BASEDIR, jobname, str(buildnumber), "artifact"
    )
    return _jenkins_get(url, base_path, artifact_info["fileName"])


def workfront_note_send(_id, message):
    command = [
        "/usr/bin/workfront-jenkins-update",
        "--credfile=%s" % settings.WORKFRONT_CREDENTIALS,
        "--taskid=%s" % _id,
        '--message="%s"' % message,
    ]
    logger.debug("workfront-jenkins-update command: %s", command)
    res = executeAndReturnOutput(command)
    if res[0] != 0:
        logger.error("can't post workfront note. %s. %s", res[1], res[2])
        return False
    return True


def get_next_release(branch):
    command = ["/usr/bin/meta-release-helper", "--next-release", branch]
    logger.debug("meta-release-helper command: %s", command)
    res = executeAndReturnOutput(command)
    if res[0] != 0:
        logger.error(
            "can't find out next release version. %s. %s", res[1], res[2]
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


def workfront_set_release_target(_id, release):
    command = [
        "/usr/bin/workfront-target-task",
        "--credfile=%s" % settings.WORKFRONT_CREDENTIALS,
        "--taskid=%s" % _id,
        "--release=%s" % release,
    ]
    logger.debug("workfront-target-task command: %s", command)
    res = executeAndReturnOutput(command)
    if res[0] != 0:
        logger.error("can't set release target. %s. %s", res[1], res[2])
        return False
    return True


def is_download_artifacts(jobname):
    if jobname in settings.JBI_ARTIFACT_JOBS:
        return True
    for check in settings.REPOAPI_ARTIFACT_JOB_REGEX:
        if re.search(check, jobname) is not None:
            return True
    return False
