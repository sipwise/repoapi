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

from . import serializers
from .models import JenkinsBuildInfo as jbi
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
import django_filters


@api_view(('GET',))
def api_root(request, format=None):
    return Response({
        'jenkinsbuildinfo': reverse('jenkinsbuildinfo-list',
                                    request=request, format=format),
        'release': reverse('release-list',
                           request=request, format=format),
    })


class JenkinsBuildInfoFilter(django_filters.FilterSet):

    class Meta:
        model = jbi
        fields = ['tag', 'projectname', 'jobname', 'param_release', 'date']
        order_by = ['-date', ]


class JenkinsBuildInfoList(generics.ListCreateAPIView):
    queryset = jbi.objects.all()
    serializer_class = serializers.JenkinsBuildInfoSerializer
    filter_class = JenkinsBuildInfoFilter


class JenkinsBuildInfoDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = jbi.objects.all()
    serializer_class = serializers.JenkinsBuildInfoSerializer


class ReleaseList(APIView):

    def get(self, request, format=None):
        res = jbi.objects.releases(flat=False)
        for r in res:
            r['url'] = reverse(
                'project-list',
                args=[r['param_release']],
                request=request)
        return Response(res)


class ProjectList(APIView):

    def get(self, request, release, format=None):
        res = jbi.objects.release_projects(
            release, flat=False)
        for r in res:
            r['url'] = reverse(
                'projectuuid-list',
                args=[release, r['projectname']],
                request=request)
        return Response(res)


class ProjectUUIDList(APIView):

    def get(self, request, release, project, format=None):
        res = jbi.objects.release_project_uuids(
            release, project, flat=False)
        latest = jbi.objects.latest_uuid(release, project)
        for r in res:
            r['url'] = reverse(
                'uuidinfo-list',
                args=[release, project, r['tag']],
                request=request)
            if r['tag'] == latest['tag']:
                r['latest'] = True
            else:
                r['latest'] = False
        return Response(res)


class UUIDInfoList(APIView):

    def get(self, request, release, project, uuid, format=None):
        res = list()
        jobs = jbi.objects.jobs_by_uuid(release, project, uuid)
        for job in jobs:
            serializer = serializers.JenkinsBuildInfoSerializer(job,
                context={'request': request})
            res.append(serializer.data)
        return Response(res)

class LatestUUID(APIView):

    def get(self, request, release, project, format=None):
        res = jbi.objects.latest_uuid(release, project)
        return Response(res)
