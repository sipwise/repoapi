# Copyright (C) 2020 The Sipwise Team - http://sipwise.com

# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.

# You should have received a copy of the GNU General Public License along
# with this prograproj.  If not, see <http://www.gnu.org/licenses/>.

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class TestHotfix(TestCase):
    def test_no_login(self):
        res = self.client.get(reverse("release_dashboard:hotfix"))
        self.assertNotEqual(res.status_code, 200)

    def test_login_ok(self):
        user = User.objects.create_user(username="test")
        self.client.force_login(user)
        res = self.client.get(reverse("release_dashboard:hotfix"))
        self.assertEqual(res.status_code, 200)


class TestDocker(TestCase):
    def test_no_login(self):
        res = self.client.get(reverse("release_dashboard:docker_images"))
        self.assertNotEqual(res.status_code, 200)

    def test_login_ok(self):
        user = User.objects.create_user(username="test")
        self.client.force_login(user)
        res = self.client.get(reverse("release_dashboard:docker_images"))
        self.assertEqual(res.status_code, 200)
