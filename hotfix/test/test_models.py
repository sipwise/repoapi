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
from hotfix import models
from repoapi.test.base import BaseTest


class TestNoteInfo(BaseTest):
    def test_output(self):
        obj, create = models.MantisNoteInfo.objects.get_or_create(
            mantis_id=1234, projectname="ngcp-project", version="1.2.3-1"
        )
        self.assertTrue(create)
        self.assertEqual(f"{obj}", "1234:ngcp-project:1.2.3-1")

        obj, create = models.WorkfrontNoteInfo.objects.get_or_create(
            workfront_id=1234, projectname="ngcp-project", version="1.2.3-1"
        )
        self.assertTrue(create)
        self.assertEqual(f"{obj}", "1234:ngcp-project:1.2.3-1")
