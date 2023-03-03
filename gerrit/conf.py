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
#
from django.conf import settings  # noqa
from appconf import AppConf


class GerritConf(AppConf):
    URL = "https://gerrit.local/{}"
    REST_HTTP_USER = "jenkins"
    REST_HTTP_PASSWD = "verysecrethttppasswd"
    DATETIME_FMT = "%Y-%m-%d %H:%M:%S.%f000"

    class Meta:
        prefix = "gerrit"
