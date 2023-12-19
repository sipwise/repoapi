# Copyright (C) 2015-2022 The Sipwise Team - http://sipwise.com
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

from django.test import override_settings

from .base import BaseTest
from repoapi.conf import settings
from repoapi.models import JenkinsBuildInfo

FIXTURES_PATH = settings.BASE_DIR.joinpath("repoapi", "fixtures", "jbi_files")
JBI_HOST = "https://%s/job/fake-gerrit/"
ARTIFACTS_JSON = """{
    "artifacts": [
        {
            "displayPath": "builddeps.list",
            "fileName": "builddeps.list",
            "relativePath": "builddeps.list"
        }
    ]
}"""


class JenkinsBuildInfoTestCase(BaseTest):
    def test_creation_no_tag(self):
        jbi = JenkinsBuildInfo.objects.create(
            projectname="fake",
            jobname="fake-get-code",
            buildnumber=1,
            result="OK",
        )
        self.assertIsNone(jbi.tag)

    def test_empty_tag_with_release(self):
        jbi = JenkinsBuildInfo.objects.create(
            projectname="fake",
            jobname="fake-get-code",
            buildnumber=1,
            result="OK",
            param_release="release-mr4.0",
        )
        self.assertIsNone(jbi.tag)

    @override_settings(JBI_ALLOWED_HOSTS=["jenkins-dev.local"])
    def test_job_url_not_allowed(self):
        job = JenkinsBuildInfo.objects.create(
            projectname="fake",
            jobname="fake-get-code",
            buildnumber=1,
            result="OK",
            param_release="release-mr4.0",
        )
        self.assertFalse(job.is_job_url_allowed())
        job.job_url = JBI_HOST % "jenkins.mgm.sipwise.com"
        self.assertFalse(job.is_job_url_allowed())

    @override_settings(JBI_ALLOWED_HOSTS=[])
    def test_job_url_not_allowed_empty(self):
        job = JenkinsBuildInfo.objects.create(
            projectname="fake",
            jobname="fake-get-code",
            buildnumber=1,
            result="OK",
            param_release="release-mr4.0",
        )
        self.assertFalse(job.is_job_url_allowed())
        job.job_url = JBI_HOST % "jenkins.mgm.sipwise.com"
        self.assertFalse(job.is_job_url_allowed())
        job.job_url = None
        self.assertFalse(job.is_job_url_allowed())

    @override_settings(
        JBI_ALLOWED_HOSTS=["jenkins-dev.local", "jenkins.local"]
    )
    def test_job_url_allowed(self):
        job = JenkinsBuildInfo.objects.create(
            projectname="fake",
            jobname="fake-get-code",
            buildnumber=1,
            result="OK",
            param_release="release-mr4.0",
        )
        job.job_url = JBI_HOST % "jenkins-dev.local"
        self.assertTrue(job.is_job_url_allowed())
        job.job_url = JBI_HOST % "jenkins.local"
        self.assertTrue(job.is_job_url_allowed())

    def test_creation_no_ppa(self):
        jbi = JenkinsBuildInfo.objects.create(
            projectname="fake",
            jobname="fake-get-code",
            buildnumber=1,
            result="OK",
        )
        self.assertIsNone(jbi.param_ppa)
        self.assertFalse(jbi.has_ppa)


class JenkinsBuildInfoProperties(BaseTest):
    fixtures = ["test_model_queries"]

    def setUp(self):
        self.jbi = JenkinsBuildInfo.objects.get(id=1)

    def test_build_path(self):
        self.assertRegex(str(self.jbi.build_path), "^.+/fake-source/1$")

    @patch("builtins.open", mock_open(read_data="{}"))
    def test_build_info(self):
        self.assertEqual(self.jbi.build_info, {})

    def test_build_info_ko(self):
        self.assertIsNone(self.jbi.build_info)

    @patch("builtins.open", mock_open(read_data=ARTIFACTS_JSON))
    def test_artifacts(self):
        self.assertEqual(self.jbi.artifacts, ["builddeps.list"])

    def test_artifacts_ko(self):
        self.assertEqual(self.jbi.artifacts, [])


@override_settings(JBI_BASEDIR=FIXTURES_PATH)
class JenkinsBuildInfoSourceProp(BaseTest):
    fixtures = ["test_model_queries"]

    def setUp(self):
        self.jbi = JenkinsBuildInfo.objects.get(id=1)

    def tearDown(self, *args, **kwargs):
        pass  # don't remove FIXTURES_PATH

    def test_source_ko(self):
        self.assertIsNone(self.jbi.source)

    def test_source(self):
        params = {
            "gerrit_patchset": "44323",
            "gerrit_change": "44323",
            "gerrit_eventtype": "patchset-created",
            "tag": "de13c0b6-2e70-4c9d-b3a5-3a476149d2d1",
            "projectname": "lua-ngcp-kamailio",
            "git_commit_msg": "TT#95650 mocks/pv: ",
            "job_url": "https://fake/job/lua-ngcp-kamailio-repos/",
            "buildnumber": 605,
            "jobname": "lua-ngcp-kamailio-repos",
            "result": "SUCCESS",
            "param_tag": "none",
            "param_branch": "master",
            "param_release": "none",
            "param_release_uuid": "",
            "param_distribution": "buster",
            "param_ppa": "gerrit_vseva_95650",
        }
        jbi = JenkinsBuildInfo.objects.create(**params)
        self.assertEqual(jbi.source, "lua-ngcp-kamailio")

    def test_source_already_there(self):
        self.jbi._source = "fake"
        self.assertEqual(self.jbi.source, "fake")
