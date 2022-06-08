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

from .views import build
from .views import docker
from .views import Index

app_name = "release_dashboard"
urlpatterns = [
    re_path(r"^$", Index.as_view(), name="index"),
    re_path(r"^build/$", build.index, name="build_index"),
    re_path(
        r"^build/(?P<release>[^/]+)/$",
        build.build_release,
        name="build_release",
    ),
    re_path(r"^hotfix/$", build.hotfix, name="hotfix"),
    re_path(
        r"^hotfix/(?P<branch>[^/]+)/(?P<project>[^/]+)/$", build.hotfix_build
    ),
    re_path(r"^refresh/$", build.refresh_all, name="refresh_all"),
    re_path(r"^refresh/(?P<project>[^/]+)/$", build.refresh, name="refresh"),
    re_path(
        r"^build_docker/$",
        docker.build_docker_images,
        name="build_docker_images",
    ),
    re_path(
        r"^docker/refresh/$", docker.refresh_all, name="refresh_docker_all"
    ),
    re_path(
        r"^docker/refresh/(?P<project>[^/]+)/$",
        docker.refresh,
        name="refresh_docker",
    ),
    re_path(r"^docker/$", docker.docker_images, name="docker_images"),
    re_path(
        r"^docker/(?P<project>[^/]+)/$",
        docker.docker_project_images,
        name="docker_project_images",
    ),
    re_path(
        r"^docker/(?P<project>[^/]+)/(?P<image>[^/]+)$",
        docker.docker_image_tags,
        name="docker_image_tag",
    ),
]
