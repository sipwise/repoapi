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
from unittest.mock import mock_open
from unittest.mock import patch

from buildinfo import models
from buildinfo import utils
from repoapi.models import JenkinsBuildInfo
from repoapi.test.base import BaseTest

build_info = """{
"building": false,
"description": null,
"displayName": "#9000",
"duration": 55479,
"estimatedDuration": 62270,
"executor": null,
"fullDisplayName": "upgrade-binaries #9000",
"id": "9000",
"keepLog": false,
"number": 9000,
"queueId": 4582301,
"result": "SUCCESS",
"timestamp": 1668083617940,
"url": "https://jenkins-dev.mgm.sipwise.com/job/upgrade-binaries/9000/",
"builtOn": "jenkins-slave13",
"changeSet": {
    "_class": "hudson.scm.EmptyChangeLogSet",
    "items": [],
    "kind": null
},
"culprits": []}"""


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
        }
        jbi_defaults = {
            "tag": "edc90cd9-37f3-4613-9748-ed05a32031c2",
            "result": "SUCCESS",
            "job_url": "https://jenkins.mgm.sipwise.com/job/upgrade-binaries/",
            "git_commit_msg": "7fg4567 TT#0001 whatever",
        }
        if info:
            defaults.update(
                {
                    "builton": "fake-slave-1",
                    "timestamp": 0,
                    "duration": 0,
                }
            )
            return defaults
        defaults.update(jbi_defaults)
        return defaults

    @patch("builtins.open", mock_open(read_data=build_info))
    @patch("repoapi.utils.dlfile")
    def test_process_buildinfo(self, dlfile):
        qs = models.BuildInfo.objects.all()
        self.assertEqual(qs.count(), 0)
        param = self.get_defaults()
        jbi = JenkinsBuildInfo.objects.create(**param)
        utils.process_buildinfo(jbi.pk, "/tmp/fake.txt")
        qs = models.BuildInfo.objects.filter(builton="jenkins-slave13")
        self.assertEqual(qs.count(), 1)
