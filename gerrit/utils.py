# Copyright (C) 2022 The Sipwise Team - http://sipwise.com
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
import datetime
import json

import requests
import structlog
from requests.auth import HTTPBasicAuth

from .conf import GerritConf

gerrit_settings = GerritConf()
logger = structlog.get_logger(__name__)


def get_gerrit_response(url: str) -> requests.Response:
    auth = HTTPBasicAuth(
        gerrit_settings.REST_HTTP_USER,
        gerrit_settings.REST_HTTP_PASSWD,
    )
    response = requests.get(url, auth=auth)
    return response


def get_filtered_json(text: str):
    """gerrit responds with malformed json
    https://gerrit-review.googlesource.com/Documentation/rest-api.html#output
    """
    return json.loads(text[5:])


def get_gerrit_info(url: str) -> str:
    from django.conf import settings

    if settings.DEBUG:
        logger.debug(f"Debug mode, would trigger: {url}")
        return r")]}'\n[]"
    else:
        response = get_gerrit_response(url)
        response.raise_for_status()
        return response.text


def get_gerrit_tags(project: str, regex=None):
    url = gerrit_settings.URL.format(f"a/projects/{project}/tags/")
    return get_gerrit_info(url)


def get_gerrit_branches(project: str, regex=None):
    url = gerrit_settings.URL.format(f"a/projects/{project}/branches/")
    return get_gerrit_info(url)


def get_gerrit_change(id: str) -> str:
    url = gerrit_settings.URL.format(f"changes/{id}/")
    return get_gerrit_info(url)


def get_change_info(id: str):
    return get_filtered_json(get_gerrit_info(id))


def get_datetime(val: str) -> datetime.datetime:
    return datetime.datetime.strptime(val, gerrit_settings.DATETIME_FMT)
