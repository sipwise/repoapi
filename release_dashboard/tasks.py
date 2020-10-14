# Copyright (C) 2016-2020 The Sipwise Team - http://sipwise.com
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
from celery import shared_task
from celery.utils.log import get_task_logger

from .conf import settings
from .models import DockerImage
from .models import DockerTag
from .models import Project
from .utils import build
from .utils import docker

logger = get_task_logger(__name__)


@shared_task(ignore_result=True)
def gerrit_fetch_info(projectname):
    build.fetch_gerrit_info(projectname)


@shared_task(ignore_result=True)
def gerrit_fetch_all():
    for project in settings.RELEASE_DASHBOARD_PROJECTS:
        gerrit_fetch_info.delay(project)


@shared_task(ignore_result=True)
def docker_fetch_info(imagename):
    image = DockerImage.objects.get(name=imagename)
    tags = docker.get_docker_tags(imagename)
    for tagname in tags:
        manifest, digest = docker.get_docker_manifests(image.name, tagname)
        if digest:
            DockerTag.objects.create(
                name=tagname, image=image, manifests=manifest, reference=digest
            )


@shared_task(ignore_result=True)
def docker_fetch_project(projectname):
    DockerImage.objects.filter(project__name=projectname).delete()
    images = docker.get_docker_repositories()
    project = Project.objects.get(name=projectname)
    for imagename in project.filter_docker_images(images):
        image = DockerImage.objects.create(name=imagename, project=project)
        logger.debug("%s created" % image)
        docker_fetch_info.delay(image.name)


@shared_task(ignore_result=True)
def docker_fetch_all():
    DockerImage.objects.all().delete()
    images = docker.get_docker_repositories()
    logger.debug("images: %s" % images)
    for projectname in settings.RELEASE_DASHBOARD_DOCKER_PROJECTS:
        project, _ = Project.objects.get_or_create(name=projectname)
        for imagename in project.filter_docker_images(images):
            image = DockerImage.objects.create(name=imagename, project=project)
            logger.debug("%s created" % image)
            docker_fetch_info.delay(image.name)


@shared_task(ignore_result=True)
def docker_remove_tag(image_name, tag_name):
    tag = DockerTag.objects.get(name=tag_name, image__name=image_name)
    docker.delete_tag(image_name, tag.reference, tag_name)
    tag.delete()
