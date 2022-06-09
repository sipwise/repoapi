# Copyright (C) 2015 The Sipwise Team - http://sipwise.com
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
from django.test import SimpleTestCase


class TestReleaseDashboardConf(SimpleTestCase):
    def test_django_settings(self):
        from django.conf import settings

        self.assertIsNotNone(settings.RELEASE_DASHBOARD_FILTER_TAGS)

    def test_release_dashboard_settings(self):
        from release_dashboard.conf import settings

        self.assertIsNotNone(settings.RELEASE_DASHBOARD_FILTER_TAGS)
