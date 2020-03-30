# Copyright (C) 2015 The Sipwise Team - http://sipwise.com
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
import object_tools
from django.conf.urls import include
from django.conf.urls import url
from django.contrib import admin
from rest_framework.urlpatterns import format_suffix_patterns

from build import views as build_views
from release_dashboard.views import api as rd_api
from release_dashboard.views import docker
from repoapi import views

api_patterns = [
    url(r"^$", views.api_root, name="index"),
    url(
        r"^jenkinsbuildinfo/$",
        views.JenkinsBuildInfoList.as_view(),
        name="jenkinsbuildinfo-list",
    ),
    url(
        r"^jenkinsbuildinfo/(?P<pk>[0-9]+)/$",
        views.JenkinsBuildInfoDetail.as_view(),
        name="jenkinsbuildinfo-detail",
    ),
    url(r"^release/$", views.ReleaseList.as_view(), name="release-list"),
    url(
        r"^release/(?P<release>[^/]+)/$",
        views.ProjectList.as_view(),
        name="project-list",
    ),
    url(
        r"^release_jobs/(?P<release_uuid>[^/]+)/$",
        build_views.ReleaseJobs.as_view(),
        name="release-job-list",
    ),
    url(
        r"^release_jobs/(?P<release_uuid>[^/]+)/(?P<job>[^/]+)/$",
        build_views.ReleaseJobsUUID.as_view(),
        name="release-job-uuid-list",
    ),
    url(
        r"^release_jobs_full/(?P<release_uuid>[^/]+)/$",
        build_views.ReleaseJobsFull.as_view(),
        name="release-job-full-list",
    ),
    url(
        r"^release_full/(?P<release>[^/]+)/$",
        views.ProjectFullList.as_view(),
        name="project-fulllist",
    ),
    url(
        r"^release/(?P<release>[^/]+)/(?P<project>[^/]+)/latest/$",
        views.LatestUUID.as_view(),
        name="latestuuid-list",
    ),
    url(
        r"^release/(?P<release>[^/]+)/(?P<project>[^/]+)/$",
        views.ProjectUUIDList.as_view(),
        name="projectuuid-list",
    ),
    url(
        r"^release/(?P<release>[^/]+)" "/(?P<project>[^/]+)/(?P<uuid>[^/]+)/$",
        views.UUIDInfoList.as_view(),
        name="uuidinfo-list",
    ),
    url(
        r"^docker/image/$",
        docker.DockerImageList.as_view(),
        name="dockerimage-list",
    ),
    url(
        r"^docker/image/(?P<pk>[0-9]+)/$",
        docker.DockerImageDetail.as_view(),
        name="dockerimage-detail",
    ),
    url(
        r"^docker/tag/(?P<pk>[0-9]+)/$",
        docker.DockerTagDetail.as_view(),
        name="dockertag-detail",
    ),
    url(
        r"^gerrit/refresh/$",
        rd_api.RefreshGerritInfo.as_view(),
        name="gerrit-refresh",
    ),
    url(r"^build/", include("build.urls")),
]

api_patterns = format_suffix_patterns(api_patterns)

urlpatterns = [
    url(r"^object-tools/", object_tools.tools.urls),
    url(r"^admin/", admin.site.urls),
    url(r"^", include(api_patterns)),
    url(
        r"^api-auth/",
        include("rest_framework.urls", namespace="rest_framework"),
    ),
    url(r"^docs/", views.schema_view),
    url(r"^panel/", include("panel.urls")),
    url(r"^release_panel/", include("release_dashboard.urls"),),
]
