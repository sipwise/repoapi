# Copyright (C) 2015-2022 The Sipwise Team - http://sipwise.com
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
import re

import structlog
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response

from . import _common_versions
from . import _hash_versions
from . import _projects_versions
from . import regex_mr
from .. import serializers
from ..conf import settings
from ..forms.docker import BuildDockerForm
from ..models import DockerImage
from ..models import DockerTag
from ..models import Project
from ..tasks import docker_fetch_all
from ..tasks import docker_fetch_project
from ..tasks import docker_remove_tag
from ..utils import docker

logger = structlog.get_logger(__name__)


def _get_docker_tags(project, tag=None):
    repos = docker.get_docker_repositories()
    r = re.compile(f".*{project}.*")
    project_repos = filter(r.match, repos)
    logger.debug(f"{project}: {project_repos}")
    docker_tags = []
    for image in project_repos:
        res = {"name": image}
        tags = docker.get_docker_tags(image)
        if tag:
            logger.debug(f"non filtered tags: {tags}")
            tags = filter(re.compile(tag).match, tags)
        res["tags"] = tags
        docker_tags.append(res)
    logger.debug(f"docker_tags: {docker_tags}")
    return docker_tags


def _build_docker_logic(form, projects):
    result = _hash_versions(form.cleaned_data, projects)
    context = {"projects": []}
    for pro in projects:
        try:
            logger.debug(
                "trying to trigger docker image at branch %s for project %s",
                result[pro],
                pro,
            )
            url = docker.trigger_docker_build(pro, result[pro])
            context["projects"].append({"name": pro, "url": url})
        except KeyError:
            msg = f"Houston, we have a problem with trigger for {pro}"
            logger.error(msg)
            context["projects"].append({"name": pro, "url": None})
    return context


@login_required
def build_docker_images(request):
    if request.method == "POST":
        form = BuildDockerForm(request.POST)
        if form.is_valid():
            context = _build_docker_logic(
                form, settings.RELEASE_DASHBOARD_DOCKER_PROJECTS
            )
        else:
            context = {"error": "form validation error"}
        return render(request, "release_dashboard/docker_result.html", context)
    else:
        context = {
            "projects": _projects_versions(
                settings.RELEASE_DASHBOARD_DOCKER_PROJECTS,
                regex_mr,
                False,
                True,
                True,
            ),
            "common_versions": {"tags": [], "branches": ["master"]},
            "docker": True,
        }
        _common_versions(context, False, True)
        return render(request, "release_dashboard/build_docker.html", context)


@login_required
def refresh_all(request):
    if request.method == "POST":
        res = docker_fetch_all.delay()
        return JsonResponse({"url": "/flower/task/%s" % res.id}, status=201)
    else:
        template = "release_dashboard/refresh_docker.html"
        projects = []
        for project in settings.RELEASE_DASHBOARD_DOCKER_PROJECTS:
            info = {"name": project, "tags": None}
            projects.append(info)
        return render(request, template, {"projects": projects})


@login_required
@require_http_methods(["POST"])
def refresh(request, project):
    res = docker_fetch_project.delay(project)
    return JsonResponse({"url": "/flower/task/%s" % res.id}, status=201)


@login_required
@require_http_methods(["GET"])
def docker_images(request):
    images = DockerImage.objects.images_with_tags
    context = {
        "images": images,
        "URL_BASE": settings.DOCKER_REGISTRY_URL.format(""),
    }
    return render(request, "release_dashboard/docker_images.html", context)


@login_required
@require_http_methods(["GET"])
def docker_project_images(request, project):
    try:
        Project.objects.get(name=project)
    except Project.DoesNotExist:
        raise Http404("Project does not exist")
    images = DockerImage.objects.images_with_tags(project)
    context = {
        "images": images,
        "URL_BASE": settings.DOCKER_REGISTRY_URL.format(""),
    }
    return render(request, "release_dashboard/docker_images.html", context)


@login_required
@require_http_methods(["GET"])
def docker_image_tags(request, project, image):
    try:
        proj = Project.objects.get(name=project)
        image = DockerImage.objects.get(name=image, project=proj)
    except Project.DoesNotExist:
        raise Http404("Project does not exist")
    except DockerImage.DoesNotExist:
        raise Http404("Project does not exist")
    context = {
        "images": [image],
        "URL_BASE": settings.DOCKER_REGISTRY_URL.format(""),
    }
    return render(request, "release_dashboard/docker_image.html", context)


class DockerImageList(generics.ListAPIView):
    queryset = DockerImage.objects.all()
    serializer_class = serializers.DockerImageSerializer


class DockerImageDetail(generics.RetrieveDestroyAPIView):
    queryset = DockerImage.objects.all()
    serializer_class = serializers.DockerImageSerializer


class DockerTagList(generics.ListAPIView):
    queryset = DockerTag.objects.all()
    serializer_class = serializers.DockerTagSerializer


class DockerTagDetail(generics.RetrieveDestroyAPIView):
    queryset = DockerTag.objects.all()
    serializer_class = serializers.DockerTagSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        docker_remove_tag.delay(instance.image.name, instance.name)
        return Response(status=status.HTTP_202_ACCEPTED)
