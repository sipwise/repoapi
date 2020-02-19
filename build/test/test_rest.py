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
# with this program.  If not, see <http://www.gnu.org/licenses/>.
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_api_key.helpers import generate_key
from rest_framework_api_key.models import APIKey

from repoapi.test.base import BaseTest


class APIAuthenticatedTestCase(BaseTest, APITestCase):

    APP_NAME = "Project Tests"

    def setUp(self):
        super(APIAuthenticatedTestCase, self).setUp()
        self.app_key = APIKey.objects.create(
            name=self.APP_NAME, key=generate_key()
        )
        self.client.credentials(HTTP_API_KEY=self.app_key.key)


@override_settings(DEBUG=True)
class TestRest(APIAuthenticatedTestCase):
    def setUp(self):
        super(TestRest, self).setUp()
        self.url = reverse("build:list")

    def test_wrong_release(self):
        data = {
            "uuid": "fake_uuid",
            "release": "wrong-release",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertNotEqual(response.status_code, status.HTTP_201_CREATED)

    def test_trunk_wrong_debian_release(self):
        data = {
            "uuid": "fake_uuid",
            "release": "release-trunk-stretch",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["release"], "release-trunk-buster")
        self.assertIsNone(response.data["tag"])
        self.assertEqual(response.data["branch"], "master")

    def test_trunk(self):
        data = {
            "uuid": "fake_uuid",
            "release": "trunk",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["uuid"], data["uuid"])
        self.assertEqual(response.data["release"], "release-trunk-buster")
        self.assertIsNone(response.data["tag"])
        self.assertEqual(response.data["branch"], "master")
        projects = response.data["projects"].split(",")
        self.assertEqual(len(projects), 73)

    def test_mrXX(self):
        data = {
            "uuid": "fake_uuid",
            "release": "mr8.1",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["uuid"], data["uuid"])
        self.assertEqual(response.data["release"], "release-mr8.1")
        self.assertIsNone(response.data["tag"])
        self.assertEqual(response.data["branch"], "mr8.1")
        projects = response.data["projects"].split(",")
        self.assertEqual(len(projects), 73)

    def test_mrXXX(self):
        data = {
            "uuid": "fake_uuid",
            "release": "mr7.5.2",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["uuid"], data["uuid"])
        self.assertEqual(response.data["release"], "release-mr7.5.2")
        self.assertEqual(response.data["tag"], "mr7.5.2.1")
        self.assertEqual(response.data["branch"], "mr7.5.2")
        projects = response.data["projects"].split(",")
        self.assertEqual(len(projects), 75)


@override_settings(DEBUG=True)
class TestBuildRest(APIAuthenticatedTestCase):
    fixtures = [
        "test_models",
    ]
    release = "release-mr8.1"
    release_uuid = "dbe569f7-eab6-4532-a6d1-d31fb559649b"

    def test_build_project(self):
        data = {}
        url = reverse(
            "build:build_project", args=[self.release_uuid, "kamailio"]
        )
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
