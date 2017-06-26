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
from release_dashboard.models import Project, DockerImage, DockerTag
import datetime

diobj = DockerImage.objects


class DockerImageTestCase(TestCase):

    def setUp(self):
        self.proj = Project.objects.create(name="fake")

    def test_create(self):
        image = diobj.create(
            name='fake-jessie', project=self.proj)
        self.assertItemsEqual(self.proj.dockerimage_set.all(),
                              [image, ])

    def test_remove_image(self):
        image = diobj.create(
            name='fake-jessie', project=self.proj)
        self.assertItemsEqual(self.proj.dockerimage_set.all(),
                              [image, ])
        image.delete()
        self.assertTrue(Project.objects.filter(name="fake").exists())

    def test_remove_project(self):
        image = diobj.create(
            name='fake-jessie', project=self.proj)
        self.assertItemsEqual(self.proj.dockerimage_set.all(), [image, ])
        self.proj.delete()
        self.assertFalse(Project.objects.filter(name="fake").exists())
        self.assertFalse(diobj.filter(name="fake").exists())

    def test_filter_images(self):
        images = ['fake-jessie', 'other', 'ngcp-fake', 'fake-more']
        images_ok = ['fake-jessie', 'ngcp-fake', 'fake-more']
        self.assertItemsEqual(
            self.proj.filter_docker_images(images), images_ok)

    def test_image_tags(self):
        image = diobj.create(
            name='fake-jessie', project=self.proj)
        self.assertItemsEqual(image.tags, [])
        DockerTag.objects.create(
            name='latest',
            image=image,
            manifests='{}')
        self.assertItemsEqual(image.tags, ['latest', ])
        DockerTag.objects.create(
            name='mr5.4',
            image=image,
            manifests='{}',
            reference='whatever')
        self.assertItemsEqual(image.tags, ['latest', 'mr5.4'])


class DockerImageTest2Case(TestCase):
    fixtures = ['test_model_fixtures', ]

    def setUp(self):
        self.images_with_tags = [
            diobj.get(name='data-hal-jessie'),
            diobj.get(name='documentation-jessie'),
            diobj.get(name='ngcp-panel-selenium'),
            diobj.get(name='ngcp-panel-tests-rest-api-jessie'),
            diobj.get(name='ngcp-panel-tests-selenium-jessie'),
        ]

    def test_images_with_tags(self):
        self.assertItemsEqual(
            diobj.images_with_tags(),
            self.images_with_tags)

    def test_project_images_with_tags(self):
        self.assertItemsEqual(
            diobj.images_with_tags('data-hal'),
            [diobj.get(name='data-hal-jessie'), ])
        self.assertItemsEqual(
            diobj.images_with_tags('ngcp-panel'),
            [diobj.get(name='ngcp-panel-selenium'),
             diobj.get(name='ngcp-panel-tests-rest-api-jessie'),
             diobj.get(name='ngcp-panel-tests-selenium-jessie'), ])
        self.assertItemsEqual(diobj.images_with_tags('libtcap'), [])

    def test_date(self):
        tag = DockerTag.objects.get(
            name='latest',
            image__name='ngcp-panel-tests-selenium-jessie')
        self.assertEqual(
            tag.date,
            datetime.datetime(2016, 11, 07, 20, 30, 25))
