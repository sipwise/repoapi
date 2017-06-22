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

from django.test import TestCase
from django.test import override_settings
from release_dashboard.utils import docker
from mock import patch, call

DOCKER_REST_CATALOG = """
{
  "repositories":[
    "fake-jessie",
    "fake-selenium-jessie",
    "other",
    "one"]
}
"""

DOCKER_REST_FAKE_TAGS = {
    'fake-jessie': """{
        "name": "fake-jessie",
        "tags":[
            "I3a899b8945688c2ef3a4be6ba6c4c1d4cbf6d548",
            "latest"]
        }""",
    'other': """{"name": "other", "tags":[]}""",
}


def fake_tag(url):
    if url == "fake-jessie/tags/list":
        return DOCKER_REST_FAKE_TAGS['fake-jessie']
    elif url == "other/tags/list":
        return DOCKER_REST_FAKE_TAGS['other']


@override_settings(DOCKER_REGISTRY_URL='{}')
@override_settings(DEBUG=False)
class UtilsDockerTestCase(TestCase):

    @patch('release_dashboard.utils.docker.get_docker_info')
    def test_get_docker_repositories(self, gdi):
        gdi.return_value = DOCKER_REST_CATALOG
        self.assertItemsEqual(
            docker.get_docker_repositories(),
            ['fake-jessie',
             'fake-selenium-jessie',
             'other',
             'one']
        )

    @patch('release_dashboard.utils.docker.get_docker_info',
           side_effect=fake_tag)
    def test_get_docker_tags(self, gdi):
        self.assertItemsEqual(
            docker.get_docker_tags('fake-jessie'),
            ["I3a899b8945688c2ef3a4be6ba6c4c1d4cbf6d548",
             "latest"])
        calls = [
            call("fake-jessie/tags/list"),
        ]
        gdi.assert_has_calls(calls)

    @patch('release_dashboard.utils.docker.get_docker_info',
           side_effect=fake_tag)
    def test_get_docker_tags_empty(self, gdi):
        self.assertItemsEqual(docker.get_docker_tags('other'), [])
        calls = [
            call("other/tags/list"),
        ]
        gdi.assert_has_calls(calls)
