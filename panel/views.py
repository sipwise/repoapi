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

from django.shortcuts import render
from repoapi.models import JenkinsBuildInfo as jbi


def index(request):
    context = {'releases':  jbi.objects.releases()}
    return render(request, 'panel/index.html', context)


def release(request, _release):
    projects = jbi.objects.release_projects_full(_release)
    context = {'release': _release,
               'projects': projects}
    return render(request, 'panel/release.html', context)


def project(request, _release, _project):
    latest_uuid = jbi.objects.latest_uuid_js(_release, _project)
    uuids = jbi.objects.release_project_uuids_set(_release, _project)
    context = {
        'project':  _project,
        'release': _release,
        'uuids': uuids,
        'latest_uuid': latest_uuid}
    return render(request, 'panel/project.html', context)


def uuid(request, _release, _project, _uuid):
    latest_uuid = jbi.objects.is_latest_uuid_js(_release, _project, _uuid)
    context = {
        'project':  _project,
        'release': _release,
        'uuid': _uuid,
        'latest_uuid': latest_uuid,
    }
    return render(request, 'panel/project_uuid.html', context)
