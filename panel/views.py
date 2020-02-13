# Copyright (C) 2015 The Sipwise Team - http://sipwise.com
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
from django.http import HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django.shortcuts import render

from build.models import BuildRelease
from repoapi.models import JenkinsBuildInfo as jbi


def index(request):
    context = {"releases": jbi.objects.releases()}
    return render(request, "panel/index.html", context)


def release_uuid(request, _uuid):
    context = {"build_release": get_object_or_404(BuildRelease, uuid=_uuid)}
    return render(request, "panel/release_uuid.html", context)


def release(request, _release):
    if jbi.objects.is_release(_release):
        projects = jbi.objects.release_projects_full(_release)
        context = {"release": _release, "projects": projects}
        return render(request, "panel/release.html", context)
    else:
        return HttpResponseNotFound("release {} not found".format(_release))


def project(request, _release, _project):
    if jbi.objects.is_project(_release, _project):
        _latest_uuid = jbi.objects.latest_uuid_js(_release, _project)
        uuids = jbi.objects.release_project_uuids_set(_release, _project)
        context = {
            "project": _project,
            "release": _release,
            "uuids": uuids,
            "latest_uuid": _latest_uuid,
        }
        return render(request, "panel/project.html", context)
    else:
        return HttpResponseNotFound("project {} not found".format(_project))


def uuid(request, _release, _project, _uuid):
    if jbi.objects.is_uuid(_release, _project, _uuid):
        _latest_uuid = jbi.objects.is_latest_uuid_js(_release, _project, _uuid)
        context = {
            "project": _project,
            "release": _release,
            "uuid": _uuid,
            "latest_uuid": _latest_uuid,
        }
        return render(request, "panel/project_uuid.html", context)
    else:
        return HttpResponseNotFound("uuid {} not found".format(_uuid))


def latest_uuid(request, _release, _project):
    if jbi.objects.is_project(_release, _project):
        _latest_uuid = jbi.objects.latest_uuid_js(_release, _project)
        if _latest_uuid is not None:
            context = {
                "project": _project,
                "release": _release,
                "uuid": _latest_uuid["tag"],
                "latest_uuid": _latest_uuid,
            }
            return render(request, "panel/project_uuid.html", context)
        else:
            return HttpResponseNotFound("no latest uuid")
    else:
        return HttpResponseNotFound("project {} not found".format(_project))
