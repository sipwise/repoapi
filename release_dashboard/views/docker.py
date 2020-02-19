# Copyright (C) 2015 The Sipwise Team - http://sipwise.com
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
import logging
import re

from django.conf import settings
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
from release_dashboard import serializers
from release_dashboard import tasks
from release_dashboard.forms import docker_projects
from release_dashboard.forms.docker import BuildDockerForm
from release_dashboard.models import DockerImage
from release_dashboard.models import DockerTag
from release_dashboard.models import Project
from release_dashboard.utils import docker

logger = logging.getLogger(__name__)


def _get_docker_tags(project, tag=None):
    repos = docker.get_docker_repositories()
    r = re.compile(".*%s.*" % project)
    project_repos = filter(r.match, repos)
    logger.debug("%s: %s" % (project, project_repos))
    docker_tags = []
    for image in project_repos:
        res = {"name": image}
        tags = docker.get_docker_tags(image)
        if tag:
            logger.degug("non filtered tags: %s" % tags)
            tags = filter(re.compile(tag).match, tags)
        res["tags"] = tags
        docker_tags.append(res)
    logger.debug("docker_tags: %s" % docker_tags)
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
            msg = "Houston, we have a problem with trigger for %s"
            logger.error(msg, pro)
            context["projects"].append({"name": pro, "url": None})
    return context


@login_required
def build_docker_images(request):
    if request.method == "POST":
        form = BuildDockerForm(request.POST)
        if form.is_valid():
            context = _build_docker_logic(form, docker_projects)
        else:
            context = {"error": "form validation error"}
        return render(request, "release_dashboard/build_result.html", context)
    else:
        context = {
            "projects": _projects_versions(
                docker_projects, regex_mr, False, True, True,
            ),
            "common_versions": {"tags": [], "branches": ["master"]},
            "docker": True,
        }
        _common_versions(context, False, True)
        return render(request, "release_dashboard/build_docker.html", context)


@login_required
def refresh_all(request):
    if request.method == "POST":
        res = tasks.docker_fetch_all.delay()
        return JsonResponse({"url": "/flower/task/%s" % res.id}, status=201)
    else:
        template = "release_dashboard/refresh_docker.html"
        projects = []
        for project in docker_projects:
            info = {"name": project, "tags": None}
            projects.append(info)
        return render(request, template, {"projects": projects})


@login_required
@require_http_methods(["POST"])
def refresh(request, project):
    res = tasks.docker_fetch_project.delay(project)
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
        tasks.docker_remove_tag.delay(instance.image.name, instance.name)
        return Response(status=status.HTTP_202_ACCEPTED)
