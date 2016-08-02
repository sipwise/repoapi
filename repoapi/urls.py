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

from django.conf.urls import include, url
from django.contrib import admin
from rest_framework.urlpatterns import format_suffix_patterns
from repoapi import views

api_patterns = [
    url(r'^$', views.api_root, name='index'),
    url(r'^jenkinsbuildinfo/$',
        views.JenkinsBuildInfoList.as_view(),
        name='jenkinsbuildinfo-list'),
    url(r'^jenkinsbuildinfo/(?P<pk>[0-9]+)/$',
        views.JenkinsBuildInfoDetail.as_view(),
        name='jenkinsbuildinfo-detail'),
    url(r'^release/$',
        views.ReleaseList.as_view(),
        name='release-list'),
    url(r'^release/(?P<release>[^/]+)/$',
        views.ProjectList.as_view(),
        name='project-list'),
    url(r'^release_full/(?P<release>[^/]+)/$',
        views.ProjectFullList.as_view(),
        name='project-fulllist'),
    url(r'^release/(?P<release>[^/]+)/(?P<project>[^/]+)/latest/$',
        views.LatestUUID.as_view(),
        name='latestuuid-list'),
    url(r'^release/(?P<release>[^/]+)/(?P<project>[^/]+)/$',
        views.ProjectUUIDList.as_view(),
        name='projectuuid-list'),
    url(r'^release/(?P<release>[^/]+)'
        '/(?P<project>[^/]+)/(?P<uuid>[^/]+)/$',
        views.UUIDInfoList.as_view(),
        name='uuidinfo-list'),
]

api_patterns = format_suffix_patterns(api_patterns)

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include(api_patterns)),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
    url(r'^docs/', views.schema_view),
    url(r'^panel/', include('panel.urls',
                            namespace='panel')),
]
