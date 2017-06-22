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

from release_dashboard.models import Project


def get_tags(projectname, regex=None):
    project, _ = Project.objects.get_or_create(name=projectname)
    return project.filter_tags(regex)


def get_branches(projectname, regex=None):
    project, _ = Project.objects.get_or_create(name=projectname)
    return project.filter_branches(regex)
