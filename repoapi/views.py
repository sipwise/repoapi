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

from repoapi import models, serializers
from rest_framework import filters
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse


@api_view(('GET',))
def api_root(request, format=None):
    return Response({
        'jenkinsbuildinfo': reverse('jenkinsbuildinfo-list',
                                    request=request, format=format),
    })


class JenkinsBuildInfoList(generics.ListCreateAPIView):
    queryset = models.JenkinsBuildInfo.objects.all()
    serializer_class = serializers.JenkinsBuildInfoSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    # allowed fields from model
    filter_fields = ('tag', 'projectname')


class JenkinsBuildInfoDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.JenkinsBuildInfo.objects.all()
    serializer_class = serializers.JenkinsBuildInfoSerializer
