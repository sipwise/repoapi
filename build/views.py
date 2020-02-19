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
# with this program.  If not, see <http://www.gnu.org/licenses/>.
import django_filters
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIAccess

from . import models
from . import serializers
from . import tasks


class BuildReleaseFilter(django_filters.FilterSet):
    class Meta:
        model = models.BuildRelease
        fields = ["release", "start_date"]
        order_by = [
            "-start_date",
        ]


class BuildReleaseList(generics.ListCreateAPIView):
    if settings.BUILD_KEY_AUTH:
        permission_classes = (HasAPIAccess,)
    queryset = models.BuildRelease.objects.all()
    serializer_class = serializers.BuildReleaseSerializer
    filter_class = BuildReleaseFilter


class BuildReleaseDetail(generics.RetrieveAPIView):
    queryset = models.BuildRelease.objects.all()
    serializer_class = serializers.BuildReleaseSerializer


class BuildProject(APIView):
    def get(self, request, release_uuid, project):
        br = get_object_or_404(models.BuildRelease, uuid=release_uuid)
        tasks.build_project.delay(br.id, project)
        return Response({})
