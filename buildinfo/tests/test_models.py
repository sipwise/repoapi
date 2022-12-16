# Copyright (C) 2022 The Sipwise Team - http://sipwise.com
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
from buildinfo import models
from repoapi.test.base import BaseTest


class TestBuildInfo(BaseTest):
    def get_defaults(self, info=False):
        defaults = {
            "projectname": "fake",
            "jobname": "upgrade-binaries",
            "buildnumber": 1,
            "param_tag": "none",
            "param_branch": "mr4.5",
            "param_release": "none",
            "param_distribution": "wheezy",
            "param_ppa": "gerrit_MT10339_review2054",
            "builton": "fake-slave-1",
            "datetime": 1668083617940,
            "duration": 0,
        }
        return defaults

    def test_model(self):
        param = self.get_defaults()
        info = models.BuildInfo.objects.create(**param)
        self.assertIsNotNone(info.pk)
        self.assertEqual(str(info), "upgrade-binaries:1:mr4.5:none")
