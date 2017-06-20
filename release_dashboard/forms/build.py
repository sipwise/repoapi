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
from . import rd_settings
from . import trunk_projects, trunk_build_deps


class BuildForm(forms.Form):
    common_select = forms.CharField(max_length=50)
    version_release = forms.CharField(max_length=50)
    distribution = forms.CharField(max_length=30)


class BuildDepForm(BuildForm):

    def __init__(self, *args, **kwargs):
        super(BuildDepForm, self).__init__(*args, **kwargs)

        for project in rd_settings['build_deps']:
            self.fields['version_%s' %
                        project] = forms.CharField(max_length=15)


class BuildReleaseForm(BuildForm):

    def __init__(self, *args, **kwargs):
        super(BuildReleaseForm, self).__init__(*args, **kwargs)

        for project in rd_settings['projects']:
            self.fields['version_%s' %
                        project] = forms.CharField(max_length=15)


class BuildTrunkDepForm(BuildForm):

    def __init__(self, *args, **kwargs):
        super(BuildTrunkDepForm, self).__init__(*args, **kwargs)

        for project in trunk_build_deps:
            self.fields['version_%s' %
                        project] = forms.CharField(max_length=15)


class BuildTrunkReleaseForm(BuildForm):

    def __init__(self, *args, **kwargs):
        super(BuildTrunkReleaseForm, self).__init__(*args, **kwargs)

        for project in trunk_projects:
            self.fields['version_%s' %
                        project] = forms.CharField(max_length=15)
