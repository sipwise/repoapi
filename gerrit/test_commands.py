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
import datetime
import json
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from repoapi.models.gri import GerritRepoInfo

change_info = """
{
  "id": "templates~mr10.5.1~I3a066ae039b06beb892a1f9e7b8dadf7aa476742",
  "project": "templates",
  "branch": "mr10.5.1",
  "topic": "alessio_56718_bis_10_5_1",
  "hashtags": [],
  "change_id": "I3a066ae039b06beb892a1f9e7b8dadf7aa476742",
  "subject": "MT#56718 Decrement counter of B in blind transfer",
  "status": "NEW",
  "created": "2023-03-03 08:45:06.000000000",
  "updated": "2023-03-03 09:09:25.000000000",
  "submit_type": "FAST_FORWARD_ONLY",
  "mergeable": true,
  "insertions": 104,
  "deletions": 0,
  "total_comment_count": 0,
  "unresolved_comment_count": 0,
  "has_review_started": true,
  "_number": 67631,
  "owner": {
    "_account_id": 1000069
  },
  "requirements": []
}
"""
value = json.loads(change_info)


class refreshTest(TestCase):
    fixtures = ["test_gerrit_commands"]

    @patch("gerrit.management.commands.gerrit.get_change_info")
    def test_refresh(self, gci):
        gci.return_value = value
        qs = GerritRepoInfo.objects
        self.assertEqual(qs.count(), 3)
        qs_filter = qs.filter(created__date=datetime.date(1977, 1, 1))
        self.assertEqual(qs_filter.count(), 2)
        call_command("gerrit", "refresh")
        self.assertEqual(qs.count(), 3)
        self.assertEqual(qs_filter.count(), 0)

        qs_filter = qs.filter(modified__time=datetime.time(9, 9, 25))
        self.assertEqual(qs_filter.count(), 3)
