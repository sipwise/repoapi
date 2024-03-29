# Copyright (C) 2015-2024 The Sipwise Team - http://sipwise.com
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
from unittest.mock import call
from unittest.mock import mock_open
from unittest.mock import patch

from django.conf import settings

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
        base_path = self.path.joinpath(jbi.jobname, str(jbi.buildnumber))
        self.assertTrue(base_path.is_dir(), base_path)

    @patch("builtins.open", mock_open(read_data=artifacts_json))
    @patch("repoapi.utils.dlfile")
    def test_jbi_console(self, dlfile):
        param = self.get_defaults()
        jbi = JenkinsBuildInfo.objects.create(**param)
        base_path = self.path.joinpath(jbi.jobname, str(jbi.buildnumber))

        path = base_path.joinpath("console.txt")
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
        artifact_base_path = base_path.joinpath("artifact")
        path = artifact_base_path.joinpath("builddeps.list")
        self.assertNotIn(call(url, path), dlfile.call_args_list)

    @patch("builtins.open", mock_open(read_data=artifacts_json))
    @patch("repoapi.utils.dlfile")
    def test_jbi_buildinfo(self, dlfile):
        param = self.get_defaults()
        jbi = JenkinsBuildInfo.objects.create(**param)
        base_path = self.path.joinpath(jbi.jobname, str(jbi.buildnumber))
        url = JBI_BUILD_URL.format(
            settings.JENKINS_URL, jbi.jobname, jbi.buildnumber
        )
        path = base_path.joinpath("build.json")
        dlfile.assert_any_call(url, path)
        url = JBI_ARTIFACT_URL.format(
            settings.JENKINS_URL,
            jbi.jobname,
            jbi.buildnumber,
            "builddeps.list",
        )
        artifact_base_path = base_path.joinpath("artifact")
        path = artifact_base_path.joinpath("builddeps.list")
        self.assertNotIn(call(url, path), dlfile.call_args_list)

    @patch("builtins.open", mock_open(read_data=artifacts_json))
    @patch("repoapi.utils.dlfile")
    def test_jbi_artifact(self, dlfile):
        param = self.get_defaults()
        param["jobname"] = "fake-release-tools-runner"
        jbi = JenkinsBuildInfo.objects.create(**param)
        base_path = self.path.joinpath(jbi.jobname, str(jbi.buildnumber))
        url = JBI_ARTIFACT_URL.format(
            settings.JENKINS_URL,
            jbi.jobname,
            jbi.buildnumber,
            "builddeps.list",
        )
        artifact_base_path = base_path.joinpath("artifact")
        path = artifact_base_path.joinpath("builddeps.list")
        dlfile.assert_any_call(url, path)

    @patch("builtins.open", mock_open(read_data=artifacts_json))
    @patch("repoapi.utils.dlfile")
    def test_jbi_envVars(self, dlfile):
        param = self.get_defaults()
        jbi = JenkinsBuildInfo.objects.create(**param)
        base_path = self.path.joinpath(jbi.jobname, str(jbi.buildnumber))
        url = JBI_ENVVARS_URL.format(
            settings.JENKINS_URL, jbi.jobname, jbi.buildnumber
        )
        path = base_path.joinpath("envVars.json")
        dlfile.assert_any_call(url, path)


class TestJBICleanUP(BaseTest):
    fixtures = ["test_model_queries"]

    def setUp(self):
        super().setUp()
        self.jbi = JenkinsBuildInfo.objects.get(id=1)
        self.jbi.build_path.mkdir(parents=True, exist_ok=True)

    @patch("repoapi.utils.shutil")
    def test_jbi_cleanup(self, sh):
        build_path = self.jbi.build_path
        dst_path = settings.JBI_ARCHIVE / self.jbi.jobname
        self.assertTrue(build_path.exists())
        self.jbi.delete()
        sh.move.assert_called_with(build_path, dst_path)

    @patch("repoapi.signals.jbi_files_cleanup")
    def test_jbi_cleanup_called(self, jfc):
        jbi_id = self.jbi.id
        self.jbi.delete()
        jfc.delay.assert_called_with(jbi_id)


class TestJBIReleaseChangedCelery(BaseTest):
    @patch("builtins.open", mock_open(read_data=artifacts_json))
    @patch("repoapi.utils.dlfile")
    @patch("repoapi.tasks.process_result")
    def test_jbi_release_changed(self, process_result, dlfile):
        param = {
            "projectname": "check-ngcp-release-changes",
            "jobname": "check-ngcp-release-changes",
            "buildnumber": 1,
            "result": "SUCCESS",
            "job_url": "https://jenkins-dev.mgm.sipwise.com/job"
            "/check-ngcp-release-changed",
        }
        jbi = JenkinsBuildInfo.objects.create(**param)
        base_path = self.path.joinpath(jbi.jobname, str(jbi.buildnumber))
        url = JBI_ENVVARS_URL.format(
            settings.JENKINS_URL, jbi.jobname, jbi.buildnumber
        )
        path = base_path.joinpath("envVars.json")
        dlfile.assert_any_call(url, path)
        process_result.delay.assert_called_once_with(jbi.id, str(path))
