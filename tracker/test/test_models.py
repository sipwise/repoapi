# Copyright (C) 2022 The Sipwise Team - http://sipwise.com
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
from natsort import humansorted

from repoapi.test.base import BaseTest
from tracker.models import MantisInfo
from tracker.models import TrackerMapper


class TrackerMapperTest(BaseTest):
    fixtures = ["test_mapper"]
    ISSUE_id = "1022"
    ISSUE_uuid = "577a4dfb004111d28a015ed5a24512a4"
    ISSUE_mantis_id = "33066"
    TASK_id = "190650"
    TASK_uuid = "631ee19a0283b8913a3ed6e6938bbd6d"
    TASK_mantis_id = "55282"

    def test_get_workfront_issue_qs(self):
        qs_uuid = TrackerMapper.objects.get_workfront_issue_qs(self.ISSUE_uuid)
        qs_id = TrackerMapper.objects.get_workfront_issue_qs(self.ISSUE_id)
        self.assertEqual(qs_uuid.count(), 1)
        self.assertEqual(qs_id.first(), qs_uuid.first())

    def test_get_workfront_issue_qs_ko(self):
        qs_uuid = TrackerMapper.objects.get_workfront_issue_qs("fake")
        self.assertEqual(qs_uuid.count(), 0)

    def test_get_wf_qs(self):
        qs = TrackerMapper.objects.get_wf_qs([self.ISSUE_id, self.TASK_id])
        self.assertEqual(qs.count(), 2)
        self.assertEqual(qs.first().mantis_id, self.ISSUE_mantis_id)
        self.assertEqual(qs.last().mantis_id, self.TASK_mantis_id)

    def test_get_wf_qs_ko(self):
        wf = TrackerMapper.objects.get_wf_qs(["0000"])
        self.assertEqual(wf.count(), 0)

    @override_settings(TRACKER_WORKFRONT_MAPPER_IDS=False)
    def test_getIds(self):
        ids = MantisInfo.getIds("whatever MT#1234 TT#1022 TT#190650 MT#33006")
        self.assertListEqual(
            humansorted(ids),
            ["1234", "33006"],
        )

    @override_settings(TRACKER_WORKFRONT_MAPPER_IDS=True)
    def test_getIds_mapper(self):
        ids = MantisInfo.getIds(
            "whatever MT#1234 TT#1022 TT#190650 MT#33006",
        )
        self.assertListEqual(
            humansorted(ids),
            ["1234", "33006", self.ISSUE_mantis_id, self.TASK_mantis_id],
        )

    @override_settings(TRACKER_WORKFRONT_MAPPER_IDS=True)
    def test_getIds_mapper_ko(self):
        ids = MantisInfo.getIds("whatever MT#1234 TT#000 TT#0 MT#33006")
        self.assertListEqual(
            humansorted(ids),
            ["1234", "33006"],
        )
