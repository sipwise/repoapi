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

from django.test import TestCase, override_settings
from release_dashboard import tasks
from mock import patch


@override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True)
class TasksBuildTestCase(TestCase):

    @patch('release_dashboard.tasks.gerrit_fetch_info')
    def test_gerrit_fetch_all(self, gfi):
        result = tasks.gerrit_fetch_all.delay()
        self.assertTrue(result.successful())
