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
import os

from django.conf import settings
from mock import call
from mock import mock_open
from mock import patch

from repoapi.models import JenkinsBuildInfo
from repoapi.test.base import BaseTest
from repoapi.utils import JBI_ARTIFACT_URL
from repoapi.utils import JBI_BUILD_URL
from repoapi.utils import JBI_CONSOLE_URL
from repoapi.utils import JBI_ENVVARS_URL

artifacts_json = """{
    "artifacts": [
        {
            "displayPath": "builddeps.list",
            "fileName": "builddeps.list",
            "relativePath": "builddeps.list"
        }
    ]
}"""


class TestJBICelery(BaseTest):
    def get_defaults(self):
        defaults = {
            "tag": "edc90cd9-37f3-4613-9748-ed05a32031c2",
            "projectname": "real-fake",
            "jobname": "real-fake-gerrit",
            "buildnumber": 1,
            "result": "SUCCESS",
            "job_url": "https://jenkins-dev.mgm.sipwise.com/job"
            "/real-fake-gerrit/",
            "param_tag": "none",
            "param_branch": "master",
            "param_release": "none",
            "param_distribution": "wheezy",
            "param_ppa": "gerrit_MT10339_review2054",
            "git_commit_msg": "7fg4567 TT#0001 whatever",
        }
        return defaults

    @patch("builtins.open", mock_open(read_data=artifacts_json))
    @patch("repoapi.utils.dlfile")
    def test_jbi_path_creation(self, dlfile):
        param = self.get_defaults()
        param["jobname"] = "fake-me"
        jbi = JenkinsBuildInfo.objects.create(**param)
        base_path = os.path.join(
            settings.JBI_BASEDIR, jbi.jobname, str(jbi.buildnumber)
        )
        self.assertTrue(os.path.isdir(base_path), base_path)

    @patch("builtins.open", mock_open(read_data=artifacts_json))
    @patch("repoapi.utils.dlfile")
    def test_jbi_console(self, dlfile):
        param = self.get_defaults()
        jbi = JenkinsBuildInfo.objects.create(**param)
        base_path = os.path.join(
            settings.JBI_BASEDIR, jbi.jobname, str(jbi.buildnumber)
        )

        path = os.path.join(base_path, "console.txt")
        url = JBI_CONSOLE_URL.format(
            settings.JENKINS_URL, jbi.jobname, jbi.buildnumber
        )
        dlfile.assert_any_call(url, path)
        url = JBI_ARTIFACT_URL.format(
            settings.JENKINS_URL,
            jbi.jobname,
            jbi.buildnumber,
            "builddeps.list",
        )
        artifact_base_path = os.path.join(base_path, "artifact")
        path = os.path.join(artifact_base_path, "builddeps.list")
        self.assertNotIn(call(url, path), dlfile.call_args_list)

    @patch("builtins.open", mock_open(read_data=artifacts_json))
    @patch("repoapi.utils.dlfile")
    def test_jbi_buildinfo(self, dlfile):
        param = self.get_defaults()
        jbi = JenkinsBuildInfo.objects.create(**param)
        base_path = os.path.join(
            settings.JBI_BASEDIR, jbi.jobname, str(jbi.buildnumber)
        )
        url = JBI_BUILD_URL.format(
            settings.JENKINS_URL, jbi.jobname, jbi.buildnumber
        )
        path = os.path.join(base_path, "build.json")
        dlfile.assert_any_call(url, path)
        url = JBI_ARTIFACT_URL.format(
            settings.JENKINS_URL,
            jbi.jobname,
            jbi.buildnumber,
            "builddeps.list",
        )
        artifact_base_path = os.path.join(base_path, "artifact")
        path = os.path.join(artifact_base_path, "builddeps.list")
        self.assertNotIn(call(url, path), dlfile.call_args_list)

    @patch("builtins.open", mock_open(read_data=artifacts_json))
    @patch("repoapi.utils.dlfile")
    def test_jbi_artifact(self, dlfile):
        param = self.get_defaults()
        param["jobname"] = "fake-release-tools-runner"
        jbi = JenkinsBuildInfo.objects.create(**param)
        base_path = os.path.join(
            settings.JBI_BASEDIR, jbi.jobname, str(jbi.buildnumber)
        )
        url = JBI_ARTIFACT_URL.format(
            settings.JENKINS_URL,
            jbi.jobname,
            jbi.buildnumber,
            "builddeps.list",
        )
        artifact_base_path = os.path.join(base_path, "artifact")
        path = os.path.join(artifact_base_path, "builddeps.list")
        dlfile.assert_any_call(url, path)

    @patch("builtins.open", mock_open(read_data=artifacts_json))
    @patch("repoapi.utils.dlfile")
    def test_jbi_envVars(self, dlfile):
        param = self.get_defaults()
        jbi = JenkinsBuildInfo.objects.create(**param)
        base_path = os.path.join(
            settings.JBI_BASEDIR, jbi.jobname, str(jbi.buildnumber)
        )
        url = JBI_ENVVARS_URL.format(
            settings.JENKINS_URL, jbi.jobname, jbi.buildnumber
        )
        path = os.path.join(base_path, "envVars.json")
        dlfile.assert_any_call(url, path)


class TestJBIReleaseChangedCelery(BaseTest):
    @patch("builtins.open", mock_open(read_data=artifacts_json))
    @patch("repoapi.utils.dlfile")
    @patch("repoapi.tasks.app")
    def test_jbi_release_changed(self, app, dlfile):
        param = {
            "projectname": "check-ngcp-release-changes",
            "jobname": "check-ngcp-release-changes",
            "buildnumber": 1,
            "result": "SUCCESS",
            "job_url": "https://jenkins-dev.mgm.sipwise.com/job"
            "/check-ngcp-release-changed",
        }
        jbi = JenkinsBuildInfo.objects.create(**param)
        base_path = os.path.join(
            settings.JBI_BASEDIR, jbi.jobname, str(jbi.buildnumber)
        )
        url = JBI_ENVVARS_URL.format(
            settings.JENKINS_URL, jbi.jobname, jbi.buildnumber
        )
        path = os.path.join(base_path, "envVars.json")
        dlfile.assert_any_call(url, path)
        app.send_task.assert_called_once_with(
            "release_changed.tasks.process_result", args=[jbi.id, path]
        )
