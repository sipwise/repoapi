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
import unittest

from django.test import override_settings
from django.test import SimpleTestCase


class SettingsTest(SimpleTestCase):
    def test_debug_from_test(self):
        from ..settings.test import DEBUG

        self.assertTrue(DEBUG)

    @unittest.expectedFailure
    def test_debug(self):
        from django.conf import settings

        self.assertTrue(settings.DEBUG)

    @override_settings(DEBUG=False)
    def test_debug_override(self):
        from django.conf import settings

        self.assertFalse(settings.DEBUG)

    def test_common_value_from_django(self):
        from django.conf import settings

        self.assertEqual(settings.LANGUAGE_CODE, "en-us")

    def test_common_value(self):
        from django.conf import settings

        self.assertEqual(settings.JENKINS_TOKEN, "sipwise_jenkins_ci")
