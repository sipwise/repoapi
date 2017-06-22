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
from release_dashboard.models import Project, DockerImage


class DockerImageTestCase(TestCase):

    def setUp(self):
        self.proj = Project.objects.create(name="fake")

    def test_create(self):
        image = DockerImage.objects.create(
            name='fake-jessie', project=self.proj)
        self.assertItemsEqual(self.proj.dockerimage_set.all(),
                              [image, ])

    def test_remove_image(self):
        image = DockerImage.objects.create(
            name='fake-jessie', project=self.proj)
        self.assertItemsEqual(self.proj.dockerimage_set.all(),
                              [image, ])
        image.delete()
        self.assertTrue(Project.objects.filter(name="fake").exists())

    def test_remove_project(self):
        image = DockerImage.objects.create(
            name='fake-jessie', project=self.proj)
        self.assertItemsEqual(self.proj.dockerimage_set.all(), [image, ])
        self.proj.delete()
        self.assertFalse(Project.objects.filter(name="fake").exists())
        self.assertFalse(DockerImage.objects.filter(name="fake").exists())

    def test_filter_images(self):
        images = ['fake-jessie', 'other', 'ngcp-fake', 'fake-more']
        images_ok = ['fake-jessie', 'ngcp-fake', 'fake-more']
        self.assertItemsEqual(
            self.proj.filter_docker_images(images), images_ok)
