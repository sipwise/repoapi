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
from views import build, docker

urlpatterns = [
    url(r'^$', build.index, name='index'),
    url(r'^build_deps/$', build.build_deps, name='build_deps'),
    url(r'^build/$', build.build_release, name='build_release'),
    url(r'^build_trunk_deps/$', build.build_trunk_deps,
        name='build_trunk_deps'),
    url(r'^build_trunk/$', build.build_trunk_release,
        name='build_trunk_release'),
    url(r'^build_tag/$', build.build_release,
        {'tag_only': True}, name='build_release_tag'),
    url(r'^hotfix/$', build.hotfix, name='hotfix'),
    url(r'^hotfix/(?P<branch>[^/]+)/(?P<project>[^/]+)/$',
        build.hotfix_build),
    url(r'^refresh/$', build.refresh_all, name='refresh_all'),
    url(r'^refresh/(?P<project>[^/]+)/$', build.refresh, name='refresh'),
    url(r'^build_docker/$', docker.build_docker_images,
        name='build_docker_images'),
    url(r'^docker/refresh/$', docker.refresh_all,
        name='refresh_docker_all'),
    url(r'^docker/refresh/(?P<project>[^/]+)/$', docker.refresh,
        name='refresh_docker'),
    url(r'^docker/$', docker.docker_images,
        name='docker_images'),
]
