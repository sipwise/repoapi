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
from django.contrib import admin
from django.urls import include
from django.urls import path
from django.urls import re_path
from drf_spectacular.views import SpectacularAPIView
from drf_spectacular.views import SpectacularRedocView
from drf_spectacular.views import SpectacularSwaggerView
from rest_framework.urlpatterns import format_suffix_patterns

from . import views
from build import views as build_views
from release_dashboard.views import api as rd_api
from release_dashboard.views import docker

api_patterns = [
    re_path(r"^$", views.api_root, name="index"),
    re_path(
        r"^jenkinsbuildinfo/$",
        views.JenkinsBuildInfoList.as_view(),
        name="jenkinsbuildinfo-list",
    ),
    re_path(
        r"^jenkinsbuildinfo/(?P<pk>[0-9]+)/$",
        views.JenkinsBuildInfoDetail.as_view(),
        name="jenkinsbuildinfo-detail",
    ),
    re_path(r"^release/$", views.ReleaseList.as_view(), name="release-list"),
    re_path(
        r"^release/(?P<release>[^/]+)/$",
        views.ProjectList.as_view(),
        name="project-list",
    ),
    re_path(
        r"^release_jobs/(?P<release_uuid>[^/]+)/$",
        build_views.ReleaseJobs.as_view(),
        name="release-job-list",
    ),
    re_path(
        r"^release_jobs/(?P<release_uuid>[^/]+)/(?P<job>[^/]+)/$",
        build_views.ReleaseJobsUUID.as_view(),
        name="release-job-uuid-list",
    ),
    re_path(
        r"^release_jobs_full/(?P<release_uuid>[^/]+)/$",
        build_views.ReleaseJobsFull.as_view(),
        name="release-job-full-list",
    ),
    re_path(
        r"^release_full/(?P<release>[^/]+)/$",
        views.ProjectFullList.as_view(),
        name="project-fulllist",
    ),
    re_path(
        r"^release/(?P<release>[^/]+)/(?P<project>[^/]+)/latest/$",
        views.LatestUUID.as_view(),
        name="latestuuid-list",
    ),
    re_path(
        r"^release/(?P<release>[^/]+)/(?P<project>[^/]+)/$",
        views.ProjectUUIDList.as_view(),
        name="projectuuid-list",
    ),
    re_path(
        r"^release/(?P<release>[^/]+)" "/(?P<project>[^/]+)/(?P<uuid>[^/]+)/$",
        views.UUIDInfoList.as_view(),
        name="uuidinfo-list",
    ),
    re_path(
        r"^docker/image/$",
        docker.DockerImageList.as_view(),
        name="dockerimage-list",
    ),
    re_path(
        r"^docker/image/(?P<pk>[0-9]+)/$",
        docker.DockerImageDetail.as_view(),
        name="dockerimage-detail",
    ),
    re_path(
        r"^docker/tag/(?P<pk>[0-9]+)/$",
        docker.DockerTagDetail.as_view(),
        name="dockertag-detail",
    ),
    re_path(r"^build/", include("build.urls")),
    re_path(r"^release_changed/", include("release_changed.urls")),
]

api_patterns = format_suffix_patterns(api_patterns)

urlpatterns = [
    re_path(r"^admin/", admin.site.urls),
    path("", include(api_patterns)),
    re_path(
        r"^api-auth/",
        include("rest_framework.urls", namespace="rest_framework"),
    ),
    path("api-schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"
    ),
    re_path(
        r"^gerrit/refresh/$",
        rd_api.RefreshGerritInfo.as_view(),
        name="gerrit-refresh",
    ),
    re_path(r"^panel/", include("panel.urls")),
    re_path(
        r"^release_panel/",
        include("release_dashboard.urls"),
    ),
]
