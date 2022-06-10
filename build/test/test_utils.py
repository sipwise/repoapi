# Copyright (C) 2017-2022 The Sipwise Team - http://sipwise.com
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
import re
from unittest.mock import patch

from django.apps import apps
from django.test import override_settings
from django.test import SimpleTestCase

from build import exceptions as err
from build.conf import settings
from build.utils import get_common_release
from build.utils import get_simple_release
from build.utils import is_release_trunk
from build.utils import ReleaseConfig
from build.utils import remove_from_textlist
from build.utils import trigger_build
from build.utils import trigger_build_matrix
from build.utils import trigger_copy_deps
from repoapi.test.base import BaseTest


class SimpleIsReleaseTrunkTest(SimpleTestCase):
    def test_trunk(self):
        ok, val = is_release_trunk("trunk")
        self.assertFalse(ok)
        self.assertIsNone(val)

    def test_mrXX(self):
        ok, val = is_release_trunk("release-mr8.5")
        self.assertFalse(ok)
        self.assertIsNone(val)

    def test_release_trunk(self):
        ok, val = is_release_trunk("release-trunk-buster")
        self.assertTrue(ok)
        self.assertEqual(val, "buster")

        ok, val = is_release_trunk("release-trunk-bullseye")
        self.assertTrue(ok)
        self.assertEqual(val, "bullseye")


class SimpleReleaseTest(SimpleTestCase):
    def test_trunk(self):
        val = get_simple_release("release-trunk-buster")
        self.assertEqual(val, "trunk")

    def test_branch_release(self):
        val = get_simple_release("release-mr8.0")
        self.assertEqual(val, "mr8.0")

    def test_release_ok(self):
        val = get_simple_release("release-mr8.1.1")
        self.assertEqual(val, "mr8.1.1")

    def test_release_update_ok(self):
        val = get_simple_release("release-mr8.1-update")
        self.assertEqual(val, "mr8.1")

    def test_release_ko(self):
        val = get_simple_release("mr8.1.1")
        self.assertIsNone(val)


class CommonReleaseTest(SimpleTestCase):
    def test_trunk(self):
        val = get_common_release("release-trunk-buster")
        self.assertEqual(val, "master")

        val = get_common_release("trunk-weekly")
        self.assertEqual(val, "master")

    def test_branch_release(self):
        val = get_common_release("release-mr8.0")
        self.assertEqual(val, "mr8.0")

    def test_release_ok(self):
        val = get_common_release("mr8.1.1")
        self.assertEqual(val, "mr8.1")

    def test_release_ko(self):
        val = get_common_release("whatever-mr8.1.1")
        self.assertIsNone(val)


class ReleaseConfigTestCase(SimpleTestCase):
    build_deps = [
        "data-hal",
        "ngcp-schema",
        "libinewrate",
        "libswrate",
        "libtcap",
        "sipwise-base",
        "check-tools",
    ]

    @override_settings(BUILD_RELEASES_SKIP=["mr0.1"])
    def test_supported_releases(self):
        supported = [
            "trunk-weekly",
            "release-trunk-buster",
            "release-trunk-bullseye",
            "mr10.1.1",
            "mr10.1",
            "mr10.0",
            "mr8.1.2",
            "mr8.1",
            "mr7.5.3",
            "mr7.5.2",
            "mr7.5.1",
            "mr7.5",
        ]
        res = ReleaseConfig.supported_releases()
        self.assertListEqual(res, supported)

    @patch.object(ReleaseConfig, "supported_releases")
    def test_supported_releases_dict(self, sr):
        res_ok = [
            {"base": "master", "release": "release-trunk-buster"},
            {"base": "mr8.0", "release": "mr8.0.1"},
            {"base": "mr8.0", "release": "mr8.0"},
            {"base": "mr7.5", "release": "mr7.5.1"},
        ]
        sr.return_value = [
            "release-trunk-buster",
            "mr8.0",
            "mr8.0.1",
            "mr7.5.1",
        ]
        res = ReleaseConfig.supported_releases_dict()
        self.assertListEqual(res, res_ok)

    def test_no_release_config(self):
        with self.assertRaises(err.NoConfigReleaseFile):
            ReleaseConfig("fake_release")

    def test_no_jenkins_jobs(self):
        with self.assertRaises(err.NoJenkinsJobsInfo):
            ReleaseConfig("mr0.1")

    def test_ok(self):
        rc = ReleaseConfig("trunk")
        self.assertIsNotNone(rc.config)
        self.assertListEqual(list(rc.build_deps.keys()), self.build_deps)
        self.assertEqual(rc.debian_release, "buster")
        self.assertEqual(len(rc.projects), 73)

    def test_debian_release_value(self):
        rc = ReleaseConfig("trunk")
        self.assertEqual(rc.debian_release, "buster")

        rc = ReleaseConfig("release-trunk-bullseye")
        self.assertEqual(rc.debian_release, "bullseye")

        rc = ReleaseConfig("trunk", "bullseye")
        self.assertEqual(rc.debian_release, "bullseye")

        rc = ReleaseConfig("trunk-weekly")
        self.assertEqual(rc.debian_release, "bullseye")

        # distribution parameter is only used with trunk
        rc = ReleaseConfig("release-mr8.1-update", "bullseye")
        self.assertEqual(rc.debian_release, "buster")

    def test_release_value(self):
        rc = ReleaseConfig("trunk")
        self.assertEqual(rc.release, "trunk")

        rc = ReleaseConfig("trunk-weekly")
        self.assertEqual(rc.release, "release-trunk-weekly")

    def test_branch_tag_value_trunk(self):
        rc = ReleaseConfig("trunk")
        self.assertEqual(rc.branch, "master")
        self.assertIsNone(rc.tag)

        rc = ReleaseConfig("trunk-weekly")
        self.assertEqual(rc.branch, "master")
        self.assertIsNone(rc.tag)

    def test_branch_tag_value_mrXX(self):
        rc = ReleaseConfig("mr8.1")
        self.assertEqual(rc.branch, "mr8.1")
        self.assertIsNone(rc.tag)

    def test_branch_tag_value_mrXXX(self):
        rc = ReleaseConfig("mr7.5.2")
        self.assertEqual(rc.branch, "mr7.5.2")
        self.assertEqual(rc.tag, "mr7.5.2.1")

    def test_build_deps(self):
        rc = ReleaseConfig("trunk")
        build_deps = [
            "data-hal",
            "ngcp-schema",
            "libinewrate",
            "libswrate",
            "libtcap",
            "sipwise-base",
            "check-tools",
        ]
        self.assertListEqual(list(rc.build_deps.keys()), build_deps)

    def test_build_deps_iter_step_1(self):
        rc = ReleaseConfig("trunk")
        build_deps = [
            "data-hal",
            "libinewrate",
            "libswrate",
            "libtcap",
            "sipwise-base",
            "check-tools",
        ]
        values = []
        for prj in rc.wanna_build_deps(0):
            values.append(prj)
        self.assertListEqual(build_deps, values)

    def test_build_deps_iter_step_2(self):
        rc = ReleaseConfig("trunk")
        values = []
        for prj in rc.wanna_build_deps(1):
            values.append(prj)
        self.assertListEqual(["ngcp-schema"], values)


@patch("build.utils.open_jenkins_url")
@override_settings(DEBUG=False)
class TriggerBuild(SimpleTestCase):
    def test_project_build(self, openurl):
        params = {
            "project": "kamailio-get-code",
            "release_uuid": "UUID_mr8.2",
            "trigger_release": "release-mr8.2",
            "trigger_branch_or_tag": "branch/mr8.2",
            "trigger_distribution": "buster",
            "uuid": "UUID_A",
        }
        url = (
            "{base}/job/{project}/buildWithParameters?"
            "token={token}&cause={trigger_release}&uuid={uuid}&"
            "release_uuid={release_uuid}&"
            "branch=mr8.2&tag=none&"
            "release={trigger_release}&distribution={trigger_distribution}"
        )
        res = trigger_build(**params)
        params["base"] = settings.JENKINS_URL
        params["token"] = settings.JENKINS_TOKEN
        self.assertEqual(res, "{base}/job/{project}/".format(**params))
        openurl.assert_called_once_with(url.format(**params))

    def test_project_build_uuid(self, openurl):
        params = {
            "project": "kamailio-get-code",
            "release_uuid": "UUID_mr8.2",
            "trigger_release": "release-mr8.2",
            "trigger_branch_or_tag": "branch/mr8.2",
            "trigger_distribution": "buster",
        }
        res = [trigger_build(**params), trigger_build(**params)]
        params["base"] = settings.JENKINS_URL
        params["token"] = settings.JENKINS_TOKEN
        self.assertEqual(res[0], "{base}/job/{project}/".format(**params))
        self.assertEqual(res[0], res[1])
        uuids = list()
        self.assertEqual(len(openurl.call_args_list), 2)
        for call in openurl.call_args_list:
            m = re.match(r".+&uuid=([^&]+)&.+", str(call))
            self.assertIsNotNone(m)
            uuids.append(m.groups(0))
        self.assertNotEqual(uuids[0], uuids[1])

    def test_copy_debs_build(self, openurl):
        params = {
            "release": "release-mr8.2",
            "internal": True,
            "release_uuid": "UUID_mr8.2",
            "uuid": "UUID_A",
        }
        url = (
            "{base}/job/{project}/buildWithParameters?"
            "token={token}&cause={release}&uuid={uuid}&"
            "release_uuid={release_uuid}&"
            "release=mr8.2&internal=true"
        )
        res = trigger_copy_deps(**params)
        params["project"] = "release-copy-debs-yml"
        params["base"] = settings.JENKINS_URL
        params["token"] = settings.JENKINS_TOKEN
        self.assertEqual(res, "{base}/job/{project}/".format(**params))
        openurl.assert_called_once_with(url.format(**params))

    def test_project_build_trunk(self, openurl):
        params = {
            "project": "kamailio-get-code",
            "release_uuid": "UUID_mr8.2",
            "trigger_release": "trunk",
            "trigger_branch_or_tag": "branch/master",
            "trigger_distribution": "buster",
            "uuid": "UUID_A",
        }
        url = (
            "{base}/job/{project}/buildWithParameters?"
            "token={token}&cause={trigger_release}&uuid={uuid}&"
            "release_uuid={release_uuid}&"
            "branch=master&tag=none&"
            "release=trunk&distribution={trigger_distribution}"
        )
        res = trigger_build(**params)
        params["base"] = settings.JENKINS_URL
        params["token"] = settings.JENKINS_TOKEN
        self.assertEqual(res, "{base}/job/{project}/".format(**params))
        openurl.assert_called_once_with(url.format(**params))

    def test_copy_debs_build_trunk(self, openurl):
        params = {
            "release": "release-trunk-buster",
            "internal": True,
            "release_uuid": "UUID_master",
            "uuid": "UUID_B",
        }
        url = (
            "{base}/job/{project}/buildWithParameters?"
            "token={token}&cause={release}&uuid={uuid}&"
            "release_uuid={release_uuid}&"
            "release=release-trunk-buster&internal=true"
        )
        res = trigger_copy_deps(**params)
        params["project"] = "release-copy-debs-yml"
        params["base"] = settings.JENKINS_URL
        params["token"] = settings.JENKINS_TOKEN
        self.assertEqual(res, "{base}/job/{project}/".format(**params))
        openurl.assert_called_once_with(url.format(**params))


@patch("build.utils.open_jenkins_url")
@override_settings(DEBUG=False)
class TriggerBuildMatrix(BaseTest):
    fixtures = [
        "test_weekly",
    ]
    release = "release-trunk-weekly"
    release_uuid = "dbe569f7-eab6-4532-a6d1-d31fb559649b"

    def test_trigger_build_matrix(self, openurl):
        BuildRelease = apps.get_model("build", "BuildRelease")
        br = BuildRelease.objects.get(uuid=self.release_uuid)
        params = {
            "base": settings.JENKINS_URL,
            "token": settings.JENKINS_TOKEN,
            "job": "weekly-build-matrix-trunk-weekly",
            "cause": "repoapi finished to build trunk-weekly",
        }
        url = (
            "{base}/job/{job}/buildWithParameters?token={token}&cause={cause}"
        )
        res = trigger_build_matrix(br)
        self.assertEqual(res, "{base}/job/{job}/".format(**params))
        openurl.assert_called_once_with(url.format(**params))

    def test_trigger_build_matrix_ko(self, openurl):
        BuildRelease = apps.get_model("build", "BuildRelease")
        br = BuildRelease.objects.get(uuid=self.release_uuid)
        params = {
            "base": settings.JENKINS_URL,
            "token": settings.JENKINS_TOKEN,
            "job": "weekly-build-matrix-trunk-weekly",
            "cause": "repoapi finished to build trunk-weekly",
        }
        res = br.append_triggered_job(params["job"])
        self.assertTrue(res)
        res = trigger_build_matrix(br)
        self.assertIsNone(res)
        openurl.assert_not_called()


@override_settings(DEBUG=False)
class RemoveList(BaseTest):
    fixtures = [
        "test_weekly",
    ]
    release = "release-trunk-weekly"
    release_uuid = "dbe569f7-eab6-4532-a6d1-d31fb559649b"

    def setUp(self):
        BuildRelease = apps.get_model("build", "BuildRelease")
        self.br = BuildRelease.objects.get(uuid=self.release_uuid)

    def test_remove_from_textlist(self):
        self.br.triggered_projects = "fake-project"
        remove_from_textlist(self.br, "triggered_projects", "fake-project")
        self.assertIsNone(self.br.triggered_projects)
