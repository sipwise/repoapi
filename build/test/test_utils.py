# Copyright (C) 2020 The Sipwise Team - http://sipwise.com

# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.

# You should have received a copy of the GNU General Public License along
# with this prograproj.  If not, see <http://www.gnu.org/licenses/>.

from django.test import TestCase, override_settings
from build.utils import ReleaseConfig
from build import exceptions as err


@override_settings(DEBUG=True)
class ReleaseConfigTestCase(TestCase):
    def test_no_release_config(self):
        with self.assertRaises(err.NoConfigReleaseFile):
            ReleaseConfig("fake_release")

    def test_no_jenkins_jobs(self):
        with self.assertRaises(err.NoJenkinsJobsInfo):
            ReleaseConfig("mr0.1")

    def test_ok(self):
        build_deps = [
            "data-hal",
            "ngcp-schema",
            "libinewrate",
            "libswrate",
            "libtcap",
            "sipwise-base",
            "check-tools",
        ]
        rc = ReleaseConfig("trunk")
        self.assertIsNotNone(rc.config)
        self.assertListEqual(list(rc.build_deps.keys()), build_deps)
        self.assertEqual(rc.debian_release, "buster")
        self.assertEqual(len(rc.projects), 73)

    def test_release_value(self):
        rc = ReleaseConfig("trunk")
        self.assertEqual(rc.release, "release-trunk-buster")
