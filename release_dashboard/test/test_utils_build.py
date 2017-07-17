# Copyright (C) 2017 The Sipwise Team - http://sipwise.com
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
# with this prograproj.  If not, see <http://www.gnu.org/licenses/>.

from django.test import TestCase
from release_dashboard.utils import build


class UtilsBuildTestCase(TestCase):

    def test_is_ngcp_project(self):
        self.assertFalse(build.is_ngcp_project('fake'))
        self.assertTrue(build.is_ngcp_project('kamailio'))
