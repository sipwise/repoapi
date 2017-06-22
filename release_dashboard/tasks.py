# Copyright (C) 2016 The Sipwise Team - http://sipwise.com

# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.

# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import absolute_import

import logging
from celery import shared_task
from release_dashboard.models import Project, DockerImage
from django.conf import settings
from .utils.build import get_gerrit_tags, get_gerrit_branches
from .utils.docker import get_docker_tags, get_docker_repositories

logger = logging.getLogger(__name__)
rd_settings = settings.RELEASE_DASHBOARD_SETTINGS


@shared_task(ignore_result=True)
def gerrit_fetch_info(projectname):
    project, _ = Project.objects.get_or_create(name=projectname)
    project.tags = get_gerrit_tags(projectname)
    project.branches = get_gerrit_branches(projectname)
    project.save()


@shared_task(ignore_result=True)
def gerrit_fetch_all():
    for project in rd_settings['docker_projects']:
        gerrit_fetch_info.delay(project)


@shared_task(ignore_result=True)
def docker_fetch_info(projectname):
    project, _ = Project.objects.get_or_create(name=projectname)
    for image in project.dockerimage_set.all():
        image.tags = get_docker_tags(image.name)
        logger.debug("%s[%s]: %s" % (projectname,
                                     image.name, image.tags))
        image.save()
    project.save()


@shared_task(ignore_result=True)
def docker_fetch_all():
    DockerImage.objects.all().delete()
    images = get_docker_repositories()
    logger.debug("images: %s" % images)
    projects = set()
    for projectname in rd_settings['docker_projects']:
        project, _ = Project.objects.get_or_create(name=projectname)
        for imagename in project.filter_docker_images(images):
            image = DockerImage.objects.create(name=imagename,
                                               project=project)
            logger.debug("%s created" % image)
            projects.add(projectname)
    logger.debug('projects: %s' % projects)
    for projectname in projects:
        docker_fetch_info.delay(projectname)
