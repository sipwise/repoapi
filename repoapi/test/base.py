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

import os
import shutil
from tempfile import mkdtemp

from django.test import TestCase, override_settings
from django.conf import settings
JBI_BASEDIR = mkdtemp(dir=settings.RESULTS_DIR)


@override_settings(JBI_BASEDIR=JBI_BASEDIR)
class BaseTest(TestCase):

    def setUp(self):
        if not os.path.exists(settings.JBI_BASEDIR):
            os.makedirs(settings.JBI_BASEDIR)

    def tearDown(self):
        if os.path.exists(settings.JBI_BASEDIR):
            shutil.rmtree(settings.JBI_BASEDIR)
