# Copyright (C) 2020-2022 The Sipwise Team - http://sipwise.com
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
from unittest.mock import patch

from django.contrib.auth.models import Permission
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import override_settings
from django.test import TestCase
from django.urls import reverse

from build.models import BuildRelease
from repoapi.test.base import BaseTest


def add_perm(user, model, codename):
    ct = ContentType.objects.get_for_model(model)
    perm = Permission.objects.get(content_type=ct, codename=codename)
    user.user_permissions.add(perm)


class TestHotfix(TestCase):
    def test_no_login(self):
        res = self.client.get(reverse("release_dashboard:hotfix"))
        self.assertNotEqual(res.status_code, 200)

    def test_login_no_perm(self):
        user = User.objects.create_user(username="test")
        self.client.force_login(user)
        res = self.client.get(reverse("release_dashboard:hotfix"))
        self.assertEqual(res.status_code, 403)

    def test_login_ok(self):
        user = User.objects.create_user(username="test")
        add_perm(user, BuildRelease, "can_trigger_hotfix")
        self.client.force_login(user)
        res = self.client.get(reverse("release_dashboard:hotfix"))
        self.assertEqual(res.status_code, 200)

    @override_settings(RELEASE_DASHBOARD_PROJECTS=["fake"])
    @patch("release_dashboard.views.get_tags")
    @patch("release_dashboard.views.get_branches")
    def test_natural_sort(self, gb, gt):
        user = User.objects.create_user(username="test")
        add_perm(user, BuildRelease, "can_trigger_hotfix")
        self.client.force_login(user)
        gt.return_value = []
        gb.return_value = [
            "branch/mr5.1",
            "branch/mr8.1.1",
            "branch/mr8.1.2",
            "branch/mr8.1.10",
            "branch/mr7.5.1",
            "branch/mr6.10.1",
        ]
        res = self.client.get(reverse("release_dashboard:hotfix"))
        self.assertEqual(res.status_code, 200)
        expected = [
            {
                "name": "fake",
                "tags": [],
                "branches": [
                    "branch/mr8.1.10",
                    "branch/mr8.1.2",
                    "branch/mr8.1.1",
                    "branch/mr7.5.1",
                    "branch/mr6.10.1",
                    "branch/mr5.1",
                ],
            },
        ]
        self.assertEqual(res.context["projects"], expected)


class TestHotfixRelease(TestCase):
    def test_no_login(self):
        res = self.client.get(
            reverse(
                "release_dashboard:hotfix_release", args=["release-mr7.5.2"]
            )
        )
        self.assertNotEqual(res.status_code, 200)

    def test_login_no_perm(self):
        user = User.objects.create_user(username="test")
        self.client.force_login(user)
        res = self.client.get(
            reverse(
                "release_dashboard:hotfix_release", args=["release-mr7.5.2"]
            )
        )
        self.assertEqual(res.status_code, 403)

    def test_login_ok(self):
        user = User.objects.create_user(username="test")
        add_perm(user, BuildRelease, "can_trigger_hotfix")
        self.client.force_login(user)
        res = self.client.get(
            reverse(
                "release_dashboard:hotfix_release", args=["release-mr7.5.2"]
            )
        )
        self.assertEqual(res.status_code, 200)

    def test_no_mrXXX(self):
        user = User.objects.create_user(username="test")
        add_perm(user, BuildRelease, "can_trigger_hotfix")
        self.client.force_login(user)
        res = self.client.get(
            reverse("release_dashboard:hotfix_release", args=["release-mr7.5"])
        )
        self.assertNotEqual(res.status_code, 200)

        res = self.client.get(
            reverse(
                "release_dashboard:hotfix_release",
                args=["release-trunk-buster"],
            )
        )
        self.assertNotEqual(res.status_code, 200)

    def test_project_ok(self):
        user = User.objects.create_user(username="test")
        add_perm(user, BuildRelease, "can_trigger_hotfix")
        self.client.force_login(user)
        res = self.client.post(
            reverse(
                "release_dashboard:hotfix_release_build",
                args=["release-mr7.5.2", "data-hal"],
            ),
            {"push": "no"},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)

    def test_project_wrong(self):
        user = User.objects.create_user(username="test")
        add_perm(user, BuildRelease, "can_trigger_hotfix")
        self.client.force_login(user)
        res = self.client.post(
            reverse(
                "release_dashboard:hotfix_release_build",
                args=["release-mr7.5.2", "fake-project"],
            ),
            {"push": "no"},
            content_type="application/json",
        )
        self.assertNotEqual(res.status_code, 200)


class TestDocker(TestCase):
    def test_no_login(self):
        res = self.client.get(reverse("release_dashboard:docker_images"))
        self.assertNotEqual(res.status_code, 200)

    def test_login_ok(self):
        user = User.objects.create_user(username="test")
        self.client.force_login(user)
        res = self.client.get(reverse("release_dashboard:docker_images"))
        self.assertEqual(res.status_code, 200)


class TestBuildRelease(BaseTest):
    fixtures = ["test_build_release"]

    def test_no_login(self):
        url = reverse("release_dashboard:build_release", args=["trunk"])
        res = self.client.get(url)
        self.assertNotEqual(res.status_code, 200)

    def test_login_ok(self):
        user = User.objects.create_user(username="test")
        self.client.force_login(user)
        url = reverse("release_dashboard:build_release", args=["trunk"])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    def test_context_done(self):
        user = User.objects.create_user(username="test")
        self.client.force_login(user)
        # no build yet
        url = reverse("release_dashboard:build_release", args=["mr8.1"])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.context["done"])

    def test_context_not_done(self):
        user = User.objects.create_user(username="test")
        self.client.force_login(user)
        br = BuildRelease.objects.get(
            uuid="9058dce5-e865-420c-8b10-757e0412e22a"
        )
        br.built_projects = None
        br.save()
        url = reverse("release_dashboard:build_release", args=["trunk"])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertFalse(res.context["done"])
