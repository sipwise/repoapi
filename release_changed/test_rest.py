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
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from repoapi.test.base import BaseTest


class TestRest(BaseTest, APITestCase):
    fixtures = ["test_release_changed"]

    url = "release_changed:check"

    def setUp(self):
        super(TestRest, self).setUp()

    def test_get_success(self):
        url = reverse(self.url, args=["base", "PRO", "mr8.4"])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_not_success(self):
        url = reverse(self.url, args=["base", "CE", "mr8.4"])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_not_exist(self):
        url = reverse(self.url, args=["base", "CE", "mr8.5"])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
