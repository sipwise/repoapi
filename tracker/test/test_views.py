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
from django.urls import reverse

from repoapi.test.base import BaseTest
from tracker.conf import TrackerConf

tracker_settings = TrackerConf()


class TrackerMapperTest(BaseTest):
    fixtures = ["test_mapper"]
    ISSUE_mantis = "33066"
    ISSUE_id = "1022"
    ISSUE_uuid = "577a4dfb004111d28a015ed5a24512a4"
    TASK_mantis = "55282"
    TASK_id = "190650"
    TASK_uuid = "631ee19a0283b8913a3ed6e6938bbd6d"

    def test_issue_uuid(self):
        res = self.client.get(
            reverse("tracker:mapper-issues", args=[self.ISSUE_uuid])
        )
        self.assertEqual(res.status_code, 301)
        self.assertEqual(
            res.url,
            tracker_settings.MANTIS_MAPPER_URL.format(
                mantis_id=self.ISSUE_mantis
            ),
        )

    def test_issue_id(self):
        res = self.client.get(
            reverse("tracker:mapper-issues", args=[self.ISSUE_id])
        )
        self.assertEqual(res.status_code, 301)
        self.assertEqual(
            res.url,
            tracker_settings.MANTIS_MAPPER_URL.format(
                mantis_id=self.ISSUE_mantis
            ),
        )

    def test_task_uuid(self):
        res = self.client.get(
            reverse("tracker:mapper-tasks", args=[self.TASK_uuid])
        )
        self.assertEqual(res.status_code, 301)
        self.assertEqual(
            res.url,
            tracker_settings.MANTIS_MAPPER_URL.format(
                mantis_id=self.TASK_mantis
            ),
        )

    def test_task_id(self):
        res = self.client.get(
            reverse("tracker:mapper-tasks", args=[self.TASK_id])
        )
        self.assertEqual(res.status_code, 301)
        self.assertEqual(
            res.url,
            tracker_settings.MANTIS_MAPPER_URL.format(
                mantis_id=self.TASK_mantis
            ),
        )
