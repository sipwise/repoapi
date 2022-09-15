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
from enum import Enum, unique
from django.conf import settings  # noqa
from appconf import AppConf


@unique
class Tracker(Enum):
    NONE = "None"
    MANTIS = "Mantis"
    WORKFRONT = "WorkFront"


@unique
class MapperType(Enum):
    ISSUE = "Issue"
    TASK = "Task"


class TrackerConf(AppConf):
    REGEX = {
        Tracker.NONE: r"#(\d+)",
        Tracker.WORKFRONT: r"TT#(\d+)",
        Tracker.MANTIS: r"MT#(\d+)",
    }
    ARTIFACT_JOB_REGEX = [
        ".*-repos$",
    ]
    WORKFRONT_CREDENTIALS = "fake.txt"
    MANTIS_URL = "https://support.local/api/rest/{}"
    MANTIS_MAPPER_URL = "https://support.local/view.php?id={mantis_id}"
    MANTIS_TOKEN = "fake_mantis_token"
    MANTIS_TARGET_RELEASE = {
        "id": 75,
        "name": "Target Release",
    }
    PROVIDER = Tracker.MANTIS

    class Meta:
        prefix = "tracker"
