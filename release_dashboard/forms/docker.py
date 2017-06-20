# Copyright (C) 2016 The Sipwise Team - http://sipwise.com

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

from django import forms
from . import docker_projects


class BuildDockerForm(forms.Form):
    common_select = forms.CharField(max_length=50)

    def __init__(self, *args, **kwargs):
        super(BuildDockerForm, self).__init__(*args, **kwargs)

        for project in docker_projects:
            self.fields['version_%s' %
                        project] = forms.CharField(max_length=15)
