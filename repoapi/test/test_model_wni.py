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
from django.test import override_settings

from repoapi.models.wni import MantisNoteInfo
from repoapi.models.wni import NoteInfo
from repoapi.models.wni import WorkfrontNoteInfo
from repoapi.test.base import BaseTest
from tracker.conf import Tracker


@override_settings(TRACKER_PROVIDER=Tracker.WORKFRONT)
class WorkfrontNoteTestCase(BaseTest):
    def test_get_model(self):
        self.assertIs(NoteInfo.get_model(), WorkfrontNoteInfo)

    def test_getID(self):
        res = WorkfrontNoteInfo.getIds("jojo TT#0891 whatever")
        self.assertCountEqual(res, ["0891"])

    def test_getID_multiple(self):
        res = WorkfrontNoteInfo.getIds("jojo TT#0891 whatever TT#0001")
        self.assertCountEqual(res, ["0891", "0001"])

    def test_getID_multiple_duplicate(self):
        res = WorkfrontNoteInfo.getIds("jojo TT#0891 whatever TT#0001 TT#0891")
        self.assertCountEqual(res, ["0891", "0001"])

    def test_getCommit(self):
        res = WorkfrontNoteInfo.getCommit("1234567 TT#67676 whatever")
        self.assertEqual(res, "1234567")


@override_settings(TRACKER_PROVIDER=Tracker.MANTIS)
class MantisNoteTestCase(BaseTest):
    def test_get_model(self):
        self.assertIs(NoteInfo.get_model(), MantisNoteInfo)

    def test_getID(self):
        res = MantisNoteInfo.getIds("jojo TT#0891 MT#123 whatever")
        self.assertCountEqual(res, ["123"])

    def test_getID_multiple(self):
        res = MantisNoteInfo.getIds("jojo MT#0891 whatever MT#0001")
        self.assertCountEqual(res, ["0891", "0001"])

    def test_getID_multiple_duplicate(self):
        res = MantisNoteInfo.getIds("jojo MT#0891 whatever MT#0001 MT#0891")
        self.assertCountEqual(res, ["0891", "0001"])

    def test_getCommit(self):
        res = MantisNoteInfo.getCommit("1234567 TT#67676 MT#1234 whatever")
        self.assertEqual(res, "1234567")
