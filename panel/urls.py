# Copyright (C) 2015-2022 The Sipwise Team - http://sipwise.com
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
from django.urls import re_path

from . import views

app_name = "panel"
urlpatterns = [
    re_path(r"^$", views.index, name="index"),
    re_path(
        r"^release/(?P<_uuid>[^/]+)/$", views.release_uuid, name="release-uuid"
    ),
    re_path(r"^(?P<_release>[^/]+)/$", views.release, name="release-view"),
    re_path(
        r"^(?P<_release>[^/]+)/(?P<_project>[^/]+)/$",
        views.project,
        name="project-view",
    ),
    re_path(
        r"^(?P<_release>[^/]+)/(?P<_project>[^/]+)/latest/$",
        views.latest_uuid,
        name="latest_uuid-view",
    ),
    re_path(
        r"^(?P<_release>[^/]+)/(?P<_project>[^/]+)/(?P<_uuid>[^/]+)/$",
        views.uuid,
        name="uuid-view",
    ),
]
