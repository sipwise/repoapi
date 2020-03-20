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
# with this prograproj.  If not, see <http://www.gnu.org/licenses/>.
import uuid

from django.test import override_settings
from django.test import TestCase
from mock import call
from mock import patch

from .. import tasks
from ..models import DockerImage
from ..models import DockerTag
from ..models import Project

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
    "data-hal-jessie": """{
        "name": "data-hal-jessie",
        "tags":[
            "I3a899",
            "latest"]
        }""",
    "data-hal-selenium-jessie": """{
        "name":"data-hal-selenium-jessie",
        "tags":["If53a9","latest"]
        }""",
}


def fake_tag(url):
    if url == "data-hal-jessie/tags/list":
        return DOCKER_REST_FAKE_TAGS["data-hal-jessie"]
    elif url == "_catalog":
        return DOCKER_REST_CATALOG
    elif url == "data-hal-selenium-jessie/tags/list":
        return DOCKER_REST_FAKE_TAGS["data-hal-selenium-jessie"]
    else:
        return "{}"


def fake_manifest(url):
    return ("{}", uuid.uuid4())


@override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True)
@override_settings(DOCKER_REGISTRY_URL="{}")
@override_settings(DEBUG=False)
class TasksDockerTestCase(TestCase):
    @patch(
        "release_dashboard.utils.docker.get_docker_manifests_info",
        side_effect=fake_manifest,
    )
    @patch(
        "release_dashboard.utils.docker.get_docker_info", side_effect=fake_tag
    )
    def test_docker_fetch_info(self, gdi, gdmi):
        proj = Project.objects.create(name="data-hal")
        self.assertEquals(proj.name, "data-hal")
        image = DockerImage.objects.create(
            name="data-hal-jessie", project=proj
        )
        self.assertCountEqual(proj.dockerimage_set.all(), [image])
        result = tasks.docker_fetch_info.delay("data-hal-jessie")
        self.assertTrue(result.successful())
        image = DockerImage.objects.get(name="data-hal-jessie")
        calls = [
            call("data-hal-jessie/tags/list"),
        ]
        gdi.assert_has_calls(calls)
        calls = [
            call("data-hal-jessie/manifests/I3a899"),
            call("data-hal-jessie/manifests/latest"),
        ]
        gdmi.assert_has_calls(calls)
        self.assertCountEqual(image.tags, ["I3a899", "latest"])

    @patch(
        "release_dashboard.utils.docker.get_docker_manifests_info",
        side_effect=fake_manifest,
    )
    @patch(
        "release_dashboard.utils.docker.get_docker_info", side_effect=fake_tag
    )
    def test_docker_fetch_project(self, gdi, gdmi):
        Project.objects.create(name="data-hal")
        result = tasks.docker_fetch_project.delay("data-hal")
        self.assertTrue(result.successful())
        image = DockerImage.objects.get(name="data-hal-jessie")
        calls = [
            call("_catalog"),
            call("data-hal-jessie/tags/list"),
        ]
        gdi.assert_has_calls(calls)
        calls = [
            call("data-hal-jessie/manifests/I3a899"),
            call("data-hal-jessie/manifests/latest"),
        ]
        gdmi.assert_has_calls(calls)
        self.assertCountEqual(image.tags, ["I3a899", "latest"])

    @patch(
        "release_dashboard.utils.docker.get_docker_manifests_info",
        side_effect=fake_manifest,
    )
    @patch(
        "release_dashboard.utils.docker.get_docker_info", side_effect=fake_tag
    )
    def test_docker_fetch_all(self, gdi, gdmi):
        result = tasks.docker_fetch_all.delay()
        self.assertTrue(result.successful())
        proj = Project.objects.get(name="data-hal")
        images = [
            DockerImage.objects.get(name="data-hal-jessie"),
            DockerImage.objects.get(name="data-hal-selenium-jessie"),
        ]
        self.assertCountEqual(proj.dockerimage_set.all(), images)
        self.assertCountEqual(images[0].tags, ["I3a899", "latest"])
        self.assertCountEqual(images[1].tags, ["If53a9", "latest"])
        calls = [
            call("_catalog"),
            call("data-hal-jessie/tags/list"),
            call("data-hal-selenium-jessie/tags/list"),
        ]
        gdi.assert_has_calls(calls)
        calls = [
            call("data-hal-jessie/manifests/I3a899"),
            call("data-hal-jessie/manifests/latest"),
            call("data-hal-selenium-jessie/manifests/If53a9"),
            call("data-hal-selenium-jessie/manifests/latest"),
        ]
        gdmi.assert_has_calls(calls)

    @patch("release_dashboard.utils.docker.delete_docker_info")
    def test_remove_tag(self, ddi):
        proj = Project.objects.create(name="data-hal")
        image = DockerImage.objects.create(
            name="data-hal-jessie", project=proj
        )
        tag = DockerTag.objects.create(
            name="latest", image=image, reference=uuid.uuid4()
        )
        result = tasks.docker_remove_tag.delay("data-hal-jessie", "latest")
        self.assertTrue(result.successful())
        ddi.assert_called_once_with(
            "%s/manifests/%s" % (image.name, tag.reference)
        )
        self.assertTrue(image not in image.tags)
