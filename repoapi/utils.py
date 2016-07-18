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
from __future__ import absolute_import

from distutils.dir_util import mkpath
import logging
import os
import subprocess
import urllib2
from django.conf import settings

logger = logging.getLogger(__name__)

JBI_CONSOLE_URL = "{}/job/{}/{}/consoleText"
JBI_JOB_URL = "{}/job/{}/{}/api/json"


def executeAndReturnOutput(command, env=None):
    proc = subprocess.Popen(command, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, env=env)
    stdoutdata, stderrdata = proc.communicate()
    logger.debug("<stdout>%s</stdout>", stdoutdata)
    logger.debug("<strerr>%s</stderr>", stderrdata)
    return proc.returncode, stdoutdata, stderrdata


def dlfile(url, path):
    if settings.DEBUG:
        logger.info("I would call %s", url)
    else:
        remote_file = urllib2.urlopen(url)
        logger.debug("url:[%s]", url)
        with open(path, "wb") as local_file:
            local_file.write(remote_file.read())


def openurl(url):
    req = urllib2.Request(url)
    logger.debug("url:[%s]", url)
    response = urllib2.urlopen(req)
    if response.code is 200:
        logger.debug("OK")
        return 0
    else:
        logger.error("Error retrieving %s", url)
        return 1


def jenkins_remove_ppa(repo):
    url = "%s/job/remove-reprepro-codename/buildWithParameters?"\
        "token=%s&repository=%s" % \
        (settings.JENKINS_URL, settings.JENKINS_TOKEN, repo)
    if settings.DEBUG:
        logger.info("I would call %s", url)
    else:
        openurl(url)


def _jenkins_get(url, base_path, filename):
    mkpath(base_path)
    path = os.path.join(base_path, filename)
    logger.info("url:[%s] path[%s]", url, path)
    dlfile(url, path)


def jenkins_get_console(jobname, buildnumber):
    url = JBI_CONSOLE_URL.format(
        settings.JENKINS_URL,
        jobname,
        buildnumber
    )
    base_path = os.path.join(settings.JBI_BASEDIR,
                             jobname, str(buildnumber))
    _jenkins_get(url, base_path, 'console.txt')


def jenkins_get_job(jobname, buildnumber):
    url = JBI_JOB_URL.format(
        settings.JENKINS_URL,
        jobname,
        buildnumber
    )
    base_path = os.path.join(settings.JBI_BASEDIR,
                             jobname, str(buildnumber))
    _jenkins_get(url, base_path, 'job.json')


def workfront_note_send(_id, message):
    command = [
        "/usr/bin/workfront-post-note",
        "--credfile=%s" % settings.WORKFRONT_CREDENTIALS,
        "--private",
        "--taskid=%s" % _id,
        '--message="%s"' % message
    ]
    logger.debug("workfront-port-note command: %s", command)
    res = executeAndReturnOutput(command)
    if res[0] != 0:
        logger.error("can't post workfront note. %s. %s", res[1], res[2])
        return False
    return True
