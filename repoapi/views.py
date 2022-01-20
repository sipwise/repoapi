# Copyright (C) 2020-2022 The Sipwise Team - http://sipwise.com
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
from rest_framework import generics
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from . import serializers
from .models import JenkinsBuildInfo as jbi


@api_view(("GET",))
def api_root(request, _format=None):
    return Response(
        {
            "jenkinsbuildinfo": reverse(
                "jenkinsbuildinfo-list", request=request, format=_format
            ),
            "release": reverse(
                "release-list", request=request, format=_format
            ),
            "build": reverse("build:list", request=request, format=_format),
            "release_changed": reverse(
                "release_changed:list", request=request, format=_format
            ),
        }
    )


class JenkinsBuildInfoFilter(django_filters.FilterSet):
    class Meta:
        model = jbi
        fields = ["tag", "projectname", "jobname", "param_release", "date"]
        order_by = ["-date"]


class JenkinsBuildInfoList(generics.ListCreateAPIView):
    queryset = jbi.objects.all()
    serializer_class = serializers.JenkinsBuildInfoSerializer
    filter_class = JenkinsBuildInfoFilter


class JenkinsBuildInfoDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = jbi.objects.all()
    serializer_class = serializers.JenkinsBuildInfoSerializer


class ReleaseList(APIView):
    def get(self, request, _format=None):
        releases = jbi.objects.releases(flat=False)
        if releases is None:
            return Response([])
        for release in releases:
            release["url"] = reverse(
                "project-list",
                args=[release["param_release"]],
                request=request,
            )
        return Response(releases)


class ProjectList(APIView):
    def get(self, request, release):
        params = {"flat": False}
        if "release_uuid" in self.request.query_params:
            params["release_uuid"] = self.request.query_params["release_uuid"]
        projects = jbi.objects.release_projects(release, **params)
        if projects is None:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        for project in projects:
            project["url"] = reverse(
                "projectuuid-list",
                args=[release, project["projectname"]],
                request=request,
            )
        return Response(projects)


class ProjectFullList(APIView):
    def get(self, request, release):
        params = {}
        if "release_uuid" in self.request.query_params:
            params["release_uuid"] = self.request.query_params["release_uuid"]
        projects = jbi.objects.release_projects_full(release, **params)
        return Response(projects)


class ProjectUUIDList(APIView):
    def get(self, request, release, project):
        params = {"flat": False}
        if "release_uuid" in self.request.query_params:
            params["release_uuid"] = self.request.query_params["release_uuid"]
        uuids = jbi.objects.release_project_uuids(release, project, **params)
        params.pop("flat")
        latest = jbi.objects.latest_uuid(release, project, **params)
        for uuid in uuids:
            uuid["url"] = reverse(
                "uuidinfo-list",
                args=[release, project, uuid["tag"]],
                request=request,
            )
            uuid["latest"] = uuid["tag"] == latest["tag"]
        return Response(uuids)


class UUIDInfoList(APIView):
    def get(self, request, release, project, uuid):
        res = list()
        jbis = serializers.JenkinsBuildInfoSerializer
        jobs = jbi.objects.jobs_by_uuid(release, project, uuid)
        for job in jobs:
            serializer = jbis(job, context={"request": request})
            res.append(serializer.data)
        return Response(res)


class LatestUUID(APIView):
    def get(self, request, release, project):
        params = {}
        if "release_uuid" in self.request.query_params:
            params["release_uuid"] = self.request.query_params["release_uuid"]
        res = jbi.objects.latest_uuid(release, project, **params)
        return Response(res)
