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
from os.path import join
from unittest.mock import mock_open
from unittest.mock import patch

from . import tasks
from .conf import settings
from .models import ReleaseChanged
from repoapi.models import JenkinsBuildInfo
from repoapi.test.base import BaseTest

FIXTURES_PATH = join(settings.BASE_DIR, "release_changed", "fixtures")
FILE_PATH = join(FIXTURES_PATH, "test_envVars.json")
FILE_PATH_DONE = join(FIXTURES_PATH, "test_envVars_done.json")
with open(FILE_PATH) as file:
    DATA = file.read()
with open(FILE_PATH_DONE) as file:
    DATA_DONE = file.read()


class TasksTestCase(BaseTest):
    fixtures = ["test_release_changed_jbi"]

    def test_process_create(self):
        jbi = JenkinsBuildInfo.objects.get(pk=1)
        with patch("builtins.open", mock_open(read_data=DATA)):
            tasks.process_result.delay(jbi.id, FILE_PATH)
        r = ReleaseChanged.objects.get(version="mr8.5.1", vmtype="CE")
        self.assertEqual("FAILED", r.result)

    def test_process_modify(self):
        r = ReleaseChanged.objects.create(
            version="mr8.5.1", vmtype="CE", result="SUCCESS"
        )
        r_id = r.id
        jbi = JenkinsBuildInfo.objects.get(pk=1)
        with patch("builtins.open", mock_open(read_data=DATA)):
            tasks.process_result.delay(jbi.id, FILE_PATH)
        r = ReleaseChanged.objects.get(version="mr8.5.1", vmtype="CE")
        self.assertEqual(r_id, r.id)
        self.assertEqual("FAILED", r.result)

    def test_process_done(self):
        ReleaseChanged.objects.create(
            version="mr8.5.1", vmtype="CE", result="FAILED"
        )
        jbi = JenkinsBuildInfo.objects.get(pk=1)
        with patch("builtins.open", mock_open(read_data=DATA_DONE)):
            tasks.process_result.delay(jbi.id, FILE_PATH)
        rs = ReleaseChanged.objects.filter(version="mr8.5.1", vmtype="CE")
        self.assertFalse(rs.exists())

    def test_process_done_no_obj(self):
        jbi = JenkinsBuildInfo.objects.get(pk=1)
        with patch("builtins.open", mock_open(read_data=DATA_DONE)):
            tasks.process_result.delay(jbi.id, FILE_PATH)
        rs = ReleaseChanged.objects.filter(version="mr8.5.1", vmtype="CE")
        self.assertFalse(rs.exists())
