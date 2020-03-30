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
from django.http import JsonResponse
from rest_framework.views import APIView

from .. import tasks
from build.views import BuildAccess


class RefreshGerritInfo(APIView):
    permission_classes = (BuildAccess,)

    def post(self, request):
        res = tasks.gerrit_fetch_all.delay()
        return JsonResponse({"url": "/flower/task/%s" % res.id}, status=202)
