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
from django.test import SimpleTestCase
from natsort import humansorted

from hotfix import utils
from tracker.conf import Tracker

debian_changelog = """ngcp-fake (3.8.7.4+0~mr3.8.7.4) unstable; urgency=medium
  [ Kirill Solomko ]
  * [ee3c706] MT#21499 add mysql replication options
  [ Victor Seva ]
  * [aabb345] TT#345 fake comment
  * [aabb123] MT#8989 TT#123 fake comment
  [ Sipwise Jenkins Builder ]
 -- whatever <jenkins@sipwise.com>  Fri, 22 Jul 2016 17:29:27 +0200
"""


class TestUtils(SimpleTestCase):
    @override_settings(TRACKER_PROVIDER=Tracker.NONE)
    @patch("builtins.open", mock_open(read_data=debian_changelog))
    def test_parse_changelog_none(self):
        ids, changelog = utils.parse_changelog("/tmp/fake.txt")
        self.assertListEqual(humansorted(ids), ["123", "345", "8989", "21499"])
        self.assertEqual(changelog.full_version, "3.8.7.4+0~mr3.8.7.4")
        self.assertEqual(changelog.package, "ngcp-fake")

    @override_settings(TRACKER_PROVIDER=Tracker.WORKFRONT)
    @patch("builtins.open", mock_open(read_data=debian_changelog))
    def test_parse_changelog_wf(self):
        ids, changelog = utils.parse_changelog("/tmp/fake.txt")
        self.assertListEqual(humansorted(ids), ["123", "345"])
        self.assertEqual(changelog.full_version, "3.8.7.4+0~mr3.8.7.4")
        self.assertEqual(changelog.package, "ngcp-fake")

    @override_settings(TRACKER_PROVIDER=Tracker.MANTIS)
    @patch("builtins.open", mock_open(read_data=debian_changelog))
    def test_parse_changelog_mantis(self):
        ids, changelog = utils.parse_changelog("/tmp/fake.txt")
        self.assertListEqual(humansorted(ids), ["8989", "21499"])
        self.assertEqual(changelog.full_version, "3.8.7.4+0~mr3.8.7.4")
        self.assertEqual(changelog.package, "ngcp-fake")

    def test_get_target_release(self):
        from hotfix.models import NoteInfo

        val = NoteInfo.get_target_release("3.8.7.4+0~mr3.8.7.4")
        self.assertEqual(val, "mr3.8.7.4")

    def test_get_target_release_ko(self):
        from hotfix.models import NoteInfo

        val = NoteInfo.get_target_release("3.8.7.4-1")
        self.assertIsNone(val)
