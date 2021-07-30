# Copyright (C) 2020 The Sipwise Team - http://sipwise.com
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
from django.conf.urls import url

from . import views

app_name = "release_changed"
urlpatterns = [
    url(r"^$", views.ReleaseChangedList.as_view(), name="list"),
    url(
        r"^(?P<pk>[0-9]+)/?$",
        views.ReleaseChangedDetail.as_view(),
        name="detail",
    ),
    url(
        r"^(?P<label>[^/]+)/(?P<vmtype>[^/]+)/(?P<release>[^/]+)/$",
        views.ReleaseChangedCheck.as_view(),
        name="check",
    ),
]
