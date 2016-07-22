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

import os
import shutil

from django.test import TestCase
from django.conf import settings
from repoapi.models import JenkinsBuildInfo
from repoapi.utils import JBI_CONSOLE_URL, JBI_JOB_URL, JBI_ARTIFACT_URL
from mock import patch, call, mock_open


artifacts_json = """{
    "artifacts": [
        {
            "displayPath": "builddeps.list",
            "fileName": "builddeps.list",
            "relativePath": "builddeps.list"
        }
    ]
}"""


class TestJBICelery(TestCase):

    def get_defaults(self):
        defaults = {
            'tag': "edc90cd9-37f3-4613-9748-ed05a32031c2",
            'projectname': "real-fake",
            'jobname': "real-fake-gerrit",
            'buildnumber': 1,
            'result': "SUCCESS",
            'job_url': "https://jenkins.mgm.sipwise.com/job/real-fake-gerrit/",
            'param_tag': "none",
            'param_branch': "master",
            'param_release': "none",
            'param_distribution': "wheezy",
            'param_ppa': "gerrit_MT10339_review2054",
            'git_commit_msg': "7fg4567 TT#0001 whatever",
        }
        return defaults

    def setUp(self):
        if not os.path.exists(settings.JBI_BASEDIR):
            os.makedirs(settings.JBI_BASEDIR)

    def tearDown(self):
        if os.path.exists(settings.JBI_BASEDIR):
            shutil.rmtree(settings.JBI_BASEDIR)

    @patch('__builtin__.open', mock_open(read_data=artifacts_json))
    @patch('repoapi.utils.dlfile')
    def test_jbi_path_creation(self, dlfile):
        param = self.get_defaults()
        jbi = JenkinsBuildInfo.objects.create(**param)
        base_path = os.path.join(settings.JBI_BASEDIR,
                                 jbi.jobname, str(jbi.buildnumber))
        self.assertTrue(
            os.path.exists(settings.JBI_BASEDIR), settings.JBI_BASEDIR)
        self.assertTrue(os.path.exists(base_path))
        path = os.path.join(base_path, 'console.txt')
        url = JBI_CONSOLE_URL.format(
            settings.JENKINS_URL,
            jbi.jobname,
            jbi.buildnumber
        )
        calls = [call(url, path), ]
        url = JBI_JOB_URL.format(
            settings.JENKINS_URL,
            jbi.jobname,
            jbi.buildnumber
        )
        path = os.path.join(base_path, 'job.json')
        calls.append(call(url, path))
        dlfile.assert_has_calls(calls)
        url = JBI_ARTIFACT_URL.format(
            settings.JENKINS_URL,
            jbi.jobname,
            jbi.buildnumber,
            "builddeps.list"
        )
        artifact_base_path = os.path.join(base_path, 'artifact')
        path = os.path.join(artifact_base_path, 'builddeps.list')
        calls.append(call(url, path))
        dlfile.assert_has_calls(calls)
