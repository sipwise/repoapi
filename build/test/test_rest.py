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

from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.test import override_settings
from repoapi.test.base import BaseTest
from rest_framework_api_key.models import APIKey
from rest_framework_api_key.helpers import generate_key


class APIAuthenticatedTestCase(BaseTest, APITestCase):

    APP_NAME = 'Project Tests'

    def setUp(self):
        super(APIAuthenticatedTestCase, self).setUp()
        self.app_key = APIKey.objects.create(
            name=self.APP_NAME, key=generate_key())
        self.client.credentials(HTTP_API_KEY=self.app_key.key)


@override_settings(DEBUG=True)
class TestRest(APIAuthenticatedTestCase):

    def setUp(self):
        super(TestRest, self).setUp()
        self.url = reverse('build:list')

    def test_trunk_empty_projects(self):
        data = {
            'uuid': 'fake_uuid',
            'tag': None,
            'branch': 'master',
            'release': 'release-trunk-stretch',
            'distribution': 'stretch',
            'projects': None
        }
        response = self.client.post(self.url, data, format='json')
        self.assertNotEqual(response.status_code, status.HTTP_201_CREATED)

    def test_trunk_wrong_projects(self):
        data = {
            'uuid': 'fake_uuid',
            'tag': None,
            'branch': 'master',
            'release': 'release-trunk-stretch',
            'distribution': 'stretch',
            'projects': ''
        }
        response = self.client.post(self.url, data, format='json')
        self.assertNotEqual(response.status_code, status.HTTP_201_CREATED)

    def test_trunk(self):
        data = {
            'uuid': 'fake_uuid',
            'tag': None,
            'branch': 'master',
            'release': 'release-trunk-stretch',
            'distribution': 'stretch',
            'projects': '  kamailio , sems'
        }
        data_all = {
            'uuid': 'fake_uuid',
            'tag': None,
            'branch': 'master',
            'release': 'release-trunk-stretch',
            'distribution': 'stretch',
            'projects': 'kamailio,sems'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data_all['start_date'] = response.data['start_date']
        data_all['id'] = response.data['id']
        self.assertItemsEqual(response.data, data_all)
