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
# with this prograproj.  If not, see <http://www.gnu.org/licenses/>.

from django.test import TestCase, override_settings
from release_dashboard import tasks
from release_dashboard.models import Project, DockerImage
from mock import patch, call

DOCKER_REST_CATALOG = """
{
  "repositories":[
    "data-hal-jessie",
    "data-hal-selenium-jessie",
    "other",
    "one"]
}
"""

DOCKER_REST_FAKE_TAGS = {
    'data-hal-jessie': """{
        "name": "data-hal-jessie",
        "tags":[
            "I3a899",
            "latest"]
        }""",
    'data-hal-selenium-jessie': """{
        "name":"data-hal-selenium-jessie",
        "tags":["If53a9","latest"]
        }"""
}


def fake_tag(url):
    if url == "data-hal-jessie/tags/list":
        return DOCKER_REST_FAKE_TAGS['data-hal-jessie']
    elif url == "_catalog":
        return DOCKER_REST_CATALOG
    elif url == "data-hal-selenium-jessie/tags/list":
        return DOCKER_REST_FAKE_TAGS['data-hal-selenium-jessie']
    else:
        return "{}"


@override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True)
@override_settings(DOCKER_REGISTRY_URL='{}')
@override_settings(DEBUG=False)
class TasksDockerTestCase(TestCase):

    @patch('release_dashboard.utils.docker.get_docker_info',
           side_effect=fake_tag)
    def test_docker_fetch_info(self, gdi):
        proj = Project.objects.create(name="data-hal")
        self.assertEquals(proj.name, "data-hal")
        image = DockerImage.objects.create(
            name='data-hal-jessie', project=proj)
        self.assertItemsEqual(proj.dockerimage_set.all(), [image, ])
        result = tasks.docker_fetch_info.delay('data-hal')
        self.assertTrue(result.successful())
        image = DockerImage.objects.get(name='data-hal-jessie')
        self.assertItemsEqual(image.tags, ["I3a899", "latest"])

    @patch('release_dashboard.utils.docker.get_docker_info',
           side_effect=fake_tag)
    def test_docker_fetch_all(self, dgi):
        result = tasks.docker_fetch_all.delay()
        self.assertTrue(result.successful())
        proj = Project.objects.get(name="data-hal")
        images = [DockerImage.objects.get(name='data-hal-jessie'),
                  DockerImage.objects.get(name='data-hal-selenium-jessie')]
        self.assertItemsEqual(proj.dockerimage_set.all(), images)
        self.assertItemsEqual(images[0].tags, ["I3a899", "latest"])
        self.assertItemsEqual(images[1].tags, ["If53a9", "latest"])
        calls = [
            call("_catalog"),
            call("data-hal-jessie/tags/list"),
            call("data-hal-selenium-jessie/tags/list")
        ]
        dgi.assert_has_calls(calls)
