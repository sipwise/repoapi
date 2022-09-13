# Copyright (C) 2017-2022 The Sipwise Team - http://sipwise.com
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
import shutil
from pathlib import Path
from tempfile import mkdtemp

from django.apps import apps
from django.test import override_settings
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework_api_key.models import APIKey

JBI_BASEDIR = Path(mkdtemp(dir=os.environ.get("RESULTS")))


@override_settings(DEBUG=True, JBI_BASEDIR=JBI_BASEDIR)
class BaseTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        from repoapi.conf import settings

        cls.path = Path(settings.JBI_BASEDIR)

    def setUp(self):
        RepoAPIConfig = apps.get_app_config("repoapi")
        RepoAPIConfig.ready()
        super(BaseTest, self).setUp()
        self.path.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        if self.path.exists():
            shutil.rmtree(self.path)


class APIAuthenticatedTestCase(BaseTest, APITestCase):

    APP_NAME = "Project Tests"

    def setUp(self):
        super(APIAuthenticatedTestCase, self).setUp()
        self.app_key, key = APIKey.objects.create_key(name=self.APP_NAME)
        self.client.credentials(HTTP_API_KEY=key)
