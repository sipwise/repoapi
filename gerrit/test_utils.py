# Copyright (C) 2023 The Sipwise Team - http://sipwise.com
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
from datetime import datetime

from django.test import SimpleTestCase

from gerrit import utils

GERRIT_REST_TAGS = """
)]}'
[
  {
    "ref": "refs/tags/mr2.0.0"
  },
  {
    "ref": "refs/tags/mr1.0.0"
  }
]
"""
FILTERED_TAGS = [
    {"ref": "refs/tags/mr2.0.0"},
    {"ref": "refs/tags/mr1.0.0"},
]
GERRIT_REST_BRANCHES = """
)]}'
[
  {
    "ref": "refs/heads/master"
  },
  {
    "ref": "refs/heads/vseva/1789"
  }
]
"""
FILTERED_BRANCHES = [
    {"ref": "refs/heads/master"},
    {"ref": "refs/heads/vseva/1789"},
]


class GerritUtils(SimpleTestCase):
    def test_filtered_json(self):
        res = utils.get_filtered_json(GERRIT_REST_TAGS)
        self.assertEqual(res, FILTERED_TAGS)

        res = utils.get_filtered_json(GERRIT_REST_BRANCHES)
        self.assertEqual(res, FILTERED_BRANCHES)

    def test_get_datetime(self):
        val = "2023-03-03 08:45:06.000000000"
        expected = datetime(2023, 3, 3, 8, 45, 6)
        res = utils.get_datetime(val)
        self.assertEqual(res, expected)

        val = "2023-03-03 09:09:25.000000000"
        res = utils.get_datetime(val)
        expected = datetime(2023, 3, 3, 9, 9, 25)
        self.assertEqual(res, expected)
