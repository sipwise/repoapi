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
from io import StringIO

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

from tracker.conf import MapperType
from tracker.models import TrackerMapper

FIXTURES_PATH = settings.BASE_DIR.joinpath("tracker", "fixtures")
DB_FILE = FIXTURES_PATH.joinpath("mapper.db")


class createFakeBuildReleaseTest(TestCase):
    fixtures = ["test_models"]

    def test_ok(self):
        out = StringIO()
        call_command("mapper_import", DB_FILE, stdout=out)
        self.assertIn("('new', 20)", out.getvalue())
        self.assertIn("('error', 0)", out.getvalue())
        qs = TrackerMapper.objects
        val = qs.filter(mapper_type=MapperType.ISSUE).count()
        self.assertEqual(val, 10)
        val = qs.filter(mapper_type=MapperType.TASK).count()
        self.assertEqual(val, 10)
