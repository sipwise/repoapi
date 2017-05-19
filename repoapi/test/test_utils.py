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
# with this program.  If not, see <http://www.gnu.org/licenses/>.

from django.test import TestCase
from repoapi.test.base import BaseTest
from mock import patch

from repoapi import utils


class UtilsTestCase(BaseTest):

    @patch('repoapi.utils.executeAndReturnOutput')
    def test_get_next_release_ko(self, ear):
        ear.return_value = [1, "", ""]
        val = utils.get_next_release("whatever")
        self.assertIsNone(val)

    @patch('repoapi.utils.executeAndReturnOutput')
    def test_get_next_release0(self, ear):
        ear.return_value = [0, "mr5.5.1\n", ""]
        val = utils.get_next_release("master")
        self.assertEquals(val, 'mr5.5.1')

    @patch('repoapi.utils.executeAndReturnOutput')
    def test_get_next_release0(self, ear):
        ear.return_value = [0, "mr5.4.2\n", ""]
        val = utils.get_next_release("mr5.4")
        self.assertEquals(val, 'mr5.4.2')

    @patch('repoapi.utils.executeAndReturnOutput')
    def test_get_next_release0(self, ear):
        ear.return_value = [0, "\n", ""]
        val = utils.get_next_release("mr5.4")
        self.assertEquals(val, None)
