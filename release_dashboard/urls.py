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
from django.conf.urls import url
from django.views.generic import TemplateView

from .views import build
from .views import docker

urlpatterns = [
    url(
        r"^$",
        TemplateView.as_view(template_name="release_dashboard/index.html"),
        name="index",
    ),
    url(r"^build/$", build.index, name="build_index"),
    url(
        r"^build/(?P<release>[^/]+)/$",
        build.build_release,
        name="build_release",
    ),
    url(r"^hotfix/$", build.hotfix, name="hotfix"),
    url(r"^hotfix/(?P<branch>[^/]+)/(?P<project>[^/]+)/$", build.hotfix_build),
    url(r"^refresh/$", build.refresh_all, name="refresh_all"),
    url(r"^refresh/(?P<project>[^/]+)/$", build.refresh, name="refresh"),
    url(
        r"^build_docker/$",
        docker.build_docker_images,
        name="build_docker_images",
    ),
    url(r"^docker/refresh/$", docker.refresh_all, name="refresh_docker_all"),
    url(
        r"^docker/refresh/(?P<project>[^/]+)/$",
        docker.refresh,
        name="refresh_docker",
    ),
    url(r"^docker/$", docker.docker_images, name="docker_images"),
    url(
        r"^docker/(?P<project>[^/]+)/$",
        docker.docker_project_images,
        name="docker_project_images",
    ),
    url(
        r"^docker/(?P<project>[^/]+)/(?P<image>[^/]+)$",
        docker.docker_image_tags,
        name="docker_image_tag",
    ),
]
