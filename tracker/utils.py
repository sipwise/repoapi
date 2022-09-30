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
import json

import requests
import structlog
from natsort import humansorted

from .conf import TrackerConf
from .exceptions import IssueNotFound
from repoapi.utils import executeAndReturnOutput

tracker_settings = TrackerConf()
logger = structlog.get_logger(__name__)

MANTIS_HEADERS = {
    "Authorization": tracker_settings.MANTIS_TOKEN,
    "Content-Type": "application/json",
}


def workfront_note_send(_id, message):
    command = [
        "/usr/bin/workfront-jenkins-update",
        "--credfile=%s" % tracker_settings.WORKFRONT_CREDENTIALS,
        "--taskid=%s" % _id,
        '--message="%s"' % message,
    ]
    res = executeAndReturnOutput(command)
    if res[0] != 0:
        logger.error(
            "can't post workfront notes", stdout=res[1], stderr=res[2]
        )
        return False
    return True


def workfront_set_release_target(_id, release):
    command = [
        "/usr/bin/workfront-target-task",
        "--credfile=%s" % tracker_settings.WORKFRONT_CREDENTIALS,
        "--taskid=%s" % _id,
        "--release=%s" % release,
    ]
    res = executeAndReturnOutput(command)
    if res[0] != 0:
        logger.error("can't set release target", stdout=res[1], stderr=res[2])
        return False
    return True


def mantis_query(method, url, payload=None) -> requests.Response:
    response = requests.request(
        f"{method}", url, headers=MANTIS_HEADERS, data=payload
    )
    response.raise_for_status()
    return response


def mantis_get_issue_id(res, _id: int):
    for issue in res["issues"]:
        if int(issue["id"]) == int(_id):
            return issue


def mantis_get_issue(_id: int):
    url = tracker_settings.MANTIS_URL.format(f"issues/{_id}")
    response = mantis_query("GET", url)
    res_json = response.json()
    res = mantis_get_issue_id(res_json, _id)
    if res:
        return res
    raise IssueNotFound(
        "{} Not found in response:{}".format(_id, res_json["issues"])
    )


def mantis_note_send(_id: int, message: str) -> requests.Response:
    url = tracker_settings.MANTIS_URL.format(f"issues/{_id}/notes")
    payload = json.dumps(
        {"text": f"{message}", "view_state": {"name": "private"}}
    )
    return mantis_query("POST", url, payload)


def mantis_get_target_releases(issue) -> list:
    cf = issue["custom_fields"]
    res = set()
    for val in cf:
        if val["field"]["id"] == tracker_settings.MANTIS_TARGET_RELEASE["id"]:
            for word in val["value"].split(","):
                word = word.strip()
                if word:
                    res.add(word)
            break
    return humansorted(res)


def mantis_set_release_target(
    _id: int, release: str, force=False
) -> requests.Response:
    issue = mantis_get_issue(_id)
    if force:
        releases_val = release
    else:
        releases = mantis_get_target_releases(issue)
        if release in releases:
            logger.info(
                "release:{release} already in target_release:{releases}"
            )
            return None
        releases.append(release)
        releases_val = ",".join(humansorted(releases))
    url = tracker_settings.MANTIS_URL.format(f"issues/{_id}")
    cf = tracker_settings.MANTIS_TARGET_RELEASE
    payload = json.dumps(
        {
            "custom_fields": [
                {
                    "field": {
                        "id": cf["id"],
                        "name": cf["name"],
                    },
                    "value": f"{releases_val}",
                },
            ]
        }
    )
    return mantis_query("PATCH", url, payload)
