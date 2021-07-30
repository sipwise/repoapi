# Copyright (C) 2020 The Sipwise Team - http://sipwise.com
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
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from . import models
from .serializers import ReleaseChangedSerializer


class ReleaseChangedFilter(django_filters.FilterSet):
    class Meta:
        model = models.ReleaseChanged
        fields = ["label", "vmtype", "version", "result"]
        order_by = ["label", "version", "vmtype"]


class ReleaseChangedList(generics.ListCreateAPIView):
    queryset = models.ReleaseChanged.objects.all().order_by(
        "label", "version", "vmtype"
    )
    serializer_class = ReleaseChangedSerializer
    filterset_class = ReleaseChangedFilter


class ReleaseChangedDetail(generics.RetrieveAPIView):
    queryset = models.ReleaseChanged.objects.all().order_by(
        "label", "version", "vmtype"
    )
    serializer_class = ReleaseChangedSerializer


class ReleaseChangedCheck(APIView):
    def get(self, request, label, vmtype, release):
        r = get_object_or_404(
            models.ReleaseChanged, label=label, vmtype=vmtype, version=release
        )
        if r.result != "SUCCESS":
            raise NotFound(
                "VM {}_{}_{} has to be built".format(label, vmtype, release)
            )
        serializer = ReleaseChangedSerializer(r, context={"request": request})
        return Response(serializer.data)
