# Copyright (C) 2017 The Sipwise Team - http://sipwise.com
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
from django.test import override_settings
from django.test import TestCase

from build.models import BuildRelease


@override_settings(DEBUG=True)
class BuildReleaseManagerTestCase(TestCase):
    def test_create_trunk(self):
        br = BuildRelease.objects.create_build_release("AAA", "trunk")
        self.assertEqual(br.release, "release-trunk-buster")
        self.assertEqual(br.distribution, "buster")
        self.assertIsNone(br.tag)
        self.assertEqual(br.branch, "master")
        self.assertNotEqual(len(br.projects), 0)


@override_settings(DEBUG=True)
class BuildReleaseTestCase(TestCase):
    fixtures = [
        "test_models",
    ]

    def test_projects_list(self):
        build = BuildRelease.objects.get(
            uuid="dbe569f7-eab6-4532-a6d1-d31fb559649b"
        )
        self.assertCountEqual(
            build.projects_list,
            ["kamailio", "lua-ngcp-kamailio", "ngcp-panel"],
        )

    def test_config(self):
        build = BuildRelease.objects.get(
            uuid="dbe569f7-eab6-4532-a6d1-d31fb559649b"
        )
        config = build.config
        self.assertIsNotNone(config)
        self.assertIs(config, build.config)

    def test_branch_or_tag_trunk(self):
        build = BuildRelease.objects.create_build_release("AAA", "trunk")
        self.assertEqual(build.branch_or_tag, "branch/master")

    def test_branch_or_tag_mrXX(self):
        build = BuildRelease.objects.get(
            uuid="dbe569f7-eab6-4532-a6d1-d31fb559649b"
        )
        self.assertEqual(build.branch_or_tag, "branch/mr8.1")

    def test_branch_or_tag_mrXXX(self):
        build = BuildRelease.objects.create_build_release("AAA", "mr7.5.2")
        self.assertEqual(build.branch_or_tag, "tag/mr7.5.2.1")
