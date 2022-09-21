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
from urllib.parse import urlparse

from django.test import SimpleTestCase


class TestTrackerConf(SimpleTestCase):
    def test_django_settings(self):
        from django.conf import settings

        self.assertIsNotNone(settings.TRACKER_MANTIS_URL)

    def test_tracker_settings(self):
        from tracker.conf import settings

        self.assertIsNotNone(settings.TRACKER_MANTIS_URL)

    def test_dynamic(self):
        from tracker.conf import TrackerConf

        tracker_settings = TrackerConf()
        parsed = urlparse(tracker_settings.MANTIS_URL)
        MANTIS_MAPPER_URL = (
            f"{parsed.scheme}://{parsed.netloc}/view.php?id=" + "{mantis_id}"
        )
        self.assertEqual(MANTIS_MAPPER_URL, tracker_settings.MANTIS_MAPPER_URL)
