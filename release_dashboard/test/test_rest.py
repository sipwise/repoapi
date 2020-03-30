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
from django.conf import settings
from django.test import override_settings
from django.urls import reverse
from mock import call
from mock import patch
from rest_framework import status
from rest_framework.test import APITestCase

from release_dashboard import models
from repoapi.test.base import APIAuthenticatedTestCase


class TestDockerRest(APITestCase):
    fixtures = [
        "test_model_fixtures",
    ]

    @patch("release_dashboard.utils.docker.delete_docker_info")
    def test_deletion(self, ddi):
        image_name = "ngcp-panel-tests-rest-api-jessie"
        tag = models.DockerTag.objects.get(
            name="latest", image__name=image_name
        )
        response = self.client.delete(
            reverse("dockertag-detail", args=[tag.pk]), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertFalse(
            models.DockerTag.objects.filter(
                name="latest", image__name=image_name
            ).exists()
        )
        ddi.assert_called_once_with(
            settings.DOCKER_REGISTRY_URL.format(
                "%s/manifests/%s" % (image_name, tag.reference)
            )
        )


@override_settings(RELEASE_DASHBOARD_PROJECTS=("asterisk", "kamailio"))
class TestGerritRest(APIAuthenticatedTestCase):
    @patch("release_dashboard.utils.build.fetch_gerrit_info")
    def test_refresh(self, fgi):
        response = self.client.post(reverse("gerrit-refresh"), format="json")
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        calls = [call("asterisk"), call("kamailio")]
        self.assertListEqual(fgi.mock_calls, calls)
