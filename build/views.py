# Copyright (C) 2017-2022 The Sipwise Team - http://sipwise.com
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
import django_filters
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.parsers import JSONParser
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework_yaml.parsers import YAMLParser

from . import models
from . import serializers
from . import tasks
from . import utils
from repoapi.serializers import JenkinsBuildInfoSerializer as JBISerializer


class BuildReleaseFilter(django_filters.FilterSet):
    class Meta:
        model = models.BuildRelease
        fields = ["release", "start_date"]
        order_by = [
            "-start_date",
        ]


class BuildReleaseList(generics.ListCreateAPIView):
    permission_classes = [HasAPIKey | DjangoModelPermissions]
    queryset = models.BuildRelease.objects.all().order_by("id")
    serializer_class = serializers.BuildReleaseSerializer
    filter_class = BuildReleaseFilter


class BuildReleaseCleanup(APIView):
    permission_classes = [HasAPIKey | DjangoModelPermissions]

    def delete(self, request, version, format=None):
        if not version.startswith("release-trunk-"):
            return JsonResponse(
                {"error": f"{version} can not be removed"}, status=403
            )
        qs = models.BuildRelease.objects.filter(release=version).order_by(
            "-start_date"
        )
        build = qs.first()
        if not build or build.done:
            return JsonResponse({}, status=200)
        res = model_to_dict(build)
        qs.delete()
        return JsonResponse(res, status=202)


class BuildReleaseDetail(generics.RetrieveDestroyAPIView):
    permission_classes = [HasAPIKey | DjangoModelPermissions]
    queryset = models.BuildRelease.objects.all().order_by("id")
    serializer_class = serializers.BuildReleaseSerializer

    def perform_destroy(self, instance):
        models.BuildRelease.objects.jbi(instance.uuid).delete()
        instance.delete()

    def patch(self, request, *args, **kwargs):
        action = request.data.get("action")
        if action is None:
            return JsonResponse({"error": "No action"}, status=400)
        instance = self.get_object()
        if action == "refresh":
            instance.refresh_projects()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        elif action == "resume":
            instance.resume()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        return JsonResponse({"error": "Action unknown"}, status=400)


class BuildProject(APIView):
    permission_classes = [HasAPIKey | DjangoModelPermissions]
    queryset = models.BuildRelease.objects.all().order_by("id")

    def post(self, request, release_uuid, project):
        br = get_object_or_404(models.BuildRelease, uuid=release_uuid)
        res = tasks.build_project.delay(br.id, project)
        return JsonResponse({"url": "/flower/task/%s" % res.id}, status=201)


class ReleaseJobs(APIView):
    def get(self, request, release_uuid, format=None):
        br = get_object_or_404(models.BuildRelease, uuid=release_uuid)
        res = models.BuildRelease.objects.release_jobs(br.uuid)
        if res is None:
            return Response([])
        return Response(res)


class ReleaseJobsFull(APIView):
    def get(self, request, release_uuid, format=None):
        br = get_object_or_404(models.BuildRelease, uuid=release_uuid)
        res = models.BuildRelease.objects.release_jobs_full(br.uuid)
        if res is None:
            return Response([])
        return Response(res)


class ReleaseJobsUUID(APIView):
    def get(self, request, release_uuid, job, format=None):
        br = get_object_or_404(models.BuildRelease, uuid=release_uuid)
        jbis = models.BuildRelease.objects.release_jobs_uuids(br.uuid, job)
        if jbis is None:
            return Response([])
        res = list()
        for jbi in jbis:
            serializer = JBISerializer(jbi, context={"request": request})
            res.append(serializer.data)
        return Response(res)


class CheckConfig(APIView):
    parser_classes = [YAMLParser, JSONParser]

    def post(self, request, format=None):
        try:
            utils.ReleaseConfig("fake", config=request.data)
            return JsonResponse({"result": "All ok"}, status=200)
        except Exception as e:
            return JsonResponse({"error": f"{e}"}, status=406)
