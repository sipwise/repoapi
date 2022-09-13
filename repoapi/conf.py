# Copyright (C) 2020-2022 The Sipwise Team - http://sipwise.com
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


class RepoAPIConf(AppConf):
    ARTIFACT_JOB_REGEX = [
        ".*-repos$",
    ]
    TRACKER = Tracker.MANTIS

    class Meta:
        prefix = "repoapi"
