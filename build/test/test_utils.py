# Copyright (C) 2017 The Sipwise Team - http://sipwise.com
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

from django.conf import settings
from django.test import override_settings
from django.test import SimpleTestCase
from mock import patch

from build import exceptions as err
from build.utils import get_simple_release
from build.utils import ReleaseConfig
from build.utils import trigger_build
from build.utils import trigger_copy_deps


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

    def test_release_ko(self):
        val = get_simple_release("mr8.1.1")
        self.assertIsNone(val)


@override_settings(DEBUG=True)
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

    @override_settings(RELEASES_SKIP=["mr0.1"])
    def test_supported_releases(self):
        supported = ["trunk", "mr8.1", "mr7.5.2"]
        res = ReleaseConfig.supported_releases()
        self.assertListEqual(res, supported)

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

    def test_release_value(self):
        rc = ReleaseConfig("trunk")
        self.assertEqual(rc.release, "release-trunk-buster")

    def test_branch_tag_value_trunk(self):
        rc = ReleaseConfig("trunk")
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


@patch("build.utils.openurl")
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
