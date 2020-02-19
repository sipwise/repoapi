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
# with this prograproj.  If not, see <http://www.gnu.org/licenses/>.
from django.test import override_settings
from django.test import TestCase
from django.urls import reverse


@override_settings(DEBUG=True)
class ReleaseTest(TestCase):
    fixtures = ["test_model_queries_uuid"]

    def test_no_release(self):
        res = self.client.get(
            reverse("panel:release-uuid", args=["whatever_uuid"])
        )
        self.assertEqual(res.status_code, 404)

    def test_release(self):
        res = self.client.get(
            reverse("panel:release-uuid", args=["UUID_mr8.1"])
        )
        self.assertIsNotNone(res.context["projects"]["kamailio"])
        self.assertEqual(res.status_code, 200)
