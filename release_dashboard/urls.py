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

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^build_deps$', views.build_deps, name='build_deps'),
    url(r'^build$', views.build_release, name='build_release'),
    url(r'^hotfix/(?P<branch>[^/]+)/(?P<project>[^/]+)/$',
        views.hotfix, name='hotfix'),
    url(r'^refresh/$', views.refresh_all, name='refresh_all'),
    url(r'^refresh/(?P<project>[^/]+)/$', views.refresh, name='refresh'),
]
