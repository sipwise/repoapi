# Copyright (C) 2017-2020 The Sipwise Team - http://sipwise.com
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
import os
from distutils.dir_util import mkpath
from distutils.dir_util import remove_tree
from tempfile import mkdtemp

from django.test import override_settings
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework_api_key.helpers import generate_key
from rest_framework_api_key.models import APIKey

JBI_BASEDIR = mkdtemp(dir=os.environ.get("RESULTS"))


@override_settings(DEBUG=True, JBI_BASEDIR=JBI_BASEDIR)
class BaseTest(TestCase):
    def setUp(self):
        from repoapi.conf import settings

        mkpath(settings.JBI_BASEDIR, verbose=True)

    def tearDown(self):
        from repoapi.conf import settings

        if os.path.exists(settings.JBI_BASEDIR):
            remove_tree(settings.JBI_BASEDIR, verbose=True)


class APIAuthenticatedTestCase(BaseTest, APITestCase):

    APP_NAME = "Project Tests"

    def setUp(self):
        super(APIAuthenticatedTestCase, self).setUp()
        self.app_key = APIKey.objects.create(
            name=self.APP_NAME, key=generate_key()
        )
        self.client.credentials(HTTP_API_KEY=self.app_key.key)
