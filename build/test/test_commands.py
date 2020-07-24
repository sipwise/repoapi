# Copyright (C) 2020 The Sipwise Team - http://sipwise.com
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
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from build.models import BuildRelease


class createFakeBuildReleaseTest(TestCase):
    fixtures = ["test_models"]

    def test_mrXXX_ko(self):
        with self.assertRaises(CommandError):
            call_command("create_fake_buildrelease", "mr8.1.1")

    def test_mrXX_ko(self):
        with self.assertRaises(CommandError):
            call_command("create_fake_buildrelease", "mr8.1")

    def test_mrXX_ok(self):
        self.assertEqual(
            BuildRelease.objects.release("release-mr7.5").count(), 0
        )
        call_command("create_fake_buildrelease", "mr7.5")
        qs = BuildRelease.objects.release("release-mr7.5")
        self.assertEqual(qs.count(), 1)
        br = qs.first()
        self.assertTrue(br.done)
