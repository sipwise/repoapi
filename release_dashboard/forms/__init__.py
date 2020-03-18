# Copyright (C) 2017 The Sipwise Team - http://sipwise.com
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
from release_dashboard.conf import settings

trunk_projects = sorted(
    set(settings.RELEASE_DASHBOARD_PROJECTS)
    - set(settings.RELEASE_DASHBOARD_ABANDONED)
    - set(settings.RELEASE_DASHBOARD_BUILD_DEPS)
)
trunk_build_deps = sorted(
    set(settings.RELEASE_DASHBOARD_BUILD_DEPS)
    - set(settings.RELEASE_DASHBOARD_ABANDONED)
)
docker_projects = settings.RELEASE_DASHBOARD_DOCKER_PROJECTS
