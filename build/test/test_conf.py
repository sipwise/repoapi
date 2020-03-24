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
from repoapi.test.base import BaseTest


class TestBuildConf(BaseTest):
    def test_django_settings(self):
        from django.conf import settings

        self.assertEqual(settings.BUILD_KEY_AUTH, True)

    def test_build_settings(self):
        from build.conf import settings

        self.assertEqual(settings.BUILD_KEY_AUTH, True)
