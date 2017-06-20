# Copyright (C) 2017 The Sipwise Team - http://sipwise.com

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

from django.conf import settings

rd_settings = settings.RELEASE_DASHBOARD_SETTINGS
trunk_projects = sorted(set(rd_settings['projects']) -
                        set(rd_settings['abandoned']) -
                        set(rd_settings['build_deps']))
trunk_build_deps = sorted(set(rd_settings['build_deps']) -
                          set(rd_settings['abandoned']))
docker_projects = rd_settings['docker_projects']
