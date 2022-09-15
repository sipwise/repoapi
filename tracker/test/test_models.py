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
from repoapi.test.base import BaseTest
from tracker.models import TrackerMapper


class TrackerMapperTest(BaseTest):
    fixtures = ["test_mapper"]
    ISSUE_id = "1022"
    ISSUE_uuid = "577a4dfb004111d28a015ed5a24512a4"
    TASK_id = "190650"
    TASK_uuid = "631ee19a0283b8913a3ed6e6938bbd6d"

    def test_get_workfront_issue_qs(self):
        qs_uuid = TrackerMapper.objects.get_workfront_issue_qs(self.ISSUE_uuid)
        qs_id = TrackerMapper.objects.get_workfront_issue_qs(self.ISSUE_id)
        self.assertEqual(qs_uuid.count(), 1)
        self.assertEqual(qs_id.first(), qs_uuid.first())

    def test_get_workfront_issue_qs_ko(self):
        qs_uuid = TrackerMapper.objects.get_workfront_issue_qs("fake")
        self.assertEqual(qs_uuid.count(), 0)
