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
import urllib
import requests
import json
import uuid
from django.conf import settings
from repoapi.utils import openurl

logger = logging.getLogger(__name__)

docker_url = ("{base}/job/build-project-docker/buildWithParameters?"
              "token={token}&project={project}&branch={branch}")


def trigger_docker_build(project, branch):
    if branch == "ignore":
        logger.debug("ignoring request to trigger project %s due"
                     " to request of version 'ignore'", project)
        return
    branch = branch.split("branch/")[1]
    params = {
        'base': settings.JENKINS_URL,
        'token': urllib.parse.quote(settings.JENKINS_TOKEN),
        'project': project,
        'branch': urllib.parse.quote(branch),
    }

    url = docker_url.format(**params)
    if settings.DEBUG:
        logger.debug("Debug mode, would trigger: %s", url)
    else:
        openurl(url)
    return "{base}/job/build-project-docker/".format(**params)


def _get_info(url, headers=None):
    if settings.DEBUG:
        logger.debug("Debug mode, would trigger: %s", url)
    else:
        if headers:
            logger.debug("trigger: %s, headers: '%s'", url, headers)
            response = requests.get(url, headers)
        else:
            logger.debug("trigger: %s", url)
            response = requests.get(url)
        logger.debug("response: %s" % response)
        response.raise_for_status()
        return response


def get_docker_info(url):
    response = _get_info(url)
    return response.text


def get_docker_manifests_info(url):
    headers = {'accept': 'application/vnd.docker.distribution.manifest.v1+prettyjws' }
    response = _get_info(url, headers)
    return (response.text, response.headers['Docker-Content-Digest'])


def delete_docker_info(url):
    if settings.DEBUG:
        logger.debug("Debug mode, would trigger: %s", url)
    else:
        logger.debug("trigger: %s", url)
        headers = {'accept': 'application/vnd.docker.distribution.manifest.v1+prettyjws' }
        response = requests.delete(url, headers)
        logger.debug("response: %s" % response)
        response.raise_for_status()
        return


def get_docker_repositories():
    if settings.DEBUG:
        result = json.loads(settings.DOCKER_REGISTRY)
        return result['repositories']
    else:
        url = settings.DOCKER_REGISTRY_URL.format("_catalog")
        try:
            info = get_docker_info(url)
            logger.debug("response: %s" % info)
            result = json.loads(info)
            return result['repositories']
        except Exception as e:
            logger.error(e)
            return []


def get_docker_tags(image):
    if settings.DEBUG:
        try:
            return settings.DOCKER_IMAGES[image]
        except Exception as e:
            return []
    else:
        url = settings.DOCKER_REGISTRY_URL.format("%s/tags/list" % image)
        try:
            info = get_docker_info(url)
            logger.debug("response: %s" % info)
            result = json.loads(info)
            return result['tags']
        except Exception as e:
            logger.error('image: %s %s' % (image, e))
            return []


def get_docker_manifests(image, tag):
    if settings.DEBUG:
        return ('{}', uuid.uuid4())
    else:
        dru = settings.DOCKER_REGISTRY_URL
        url = dru.format("%s/manifests/%s" % (image, tag))
        try:
            info, digest = get_docker_manifests_info(url)
            logger.debug("response: %s" % info)
            result = json.loads(info)
            return (result, digest)
        except Exception as e:
            logger.error('image: %s tag:%s %s' % (image, tag, e))
            return (None, None)


def delete_tag(image, reference):
    dru = settings.DOCKER_REGISTRY_URL
    url = dru.format("%s/manifests/%s" % (image, reference))
    delete_docker_info(url)
