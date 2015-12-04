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
from django.shortcuts import render
from django.http import HttpResponseNotFound, JsonResponse
from django.conf import settings
from django.views.decorators.http import require_http_methods
from release_dashboard.models import Project
from .utils import get_tags, get_branches, trigger_hotfix
from .tasks import gerrit_fetch_info, gerrit_fetch_all

rd_settings = settings.RELEASE_DASHBOARD_SETTINGS
logger = logging.getLogger(__name__)
regex_hotfix = re.compile(r'^mr[0-9]+\.[0-9]+\.[0-9]+$')
regex_mr = re.compile(r'^mr.+$')


def index(request):
    context = {}
    return render(request, 'release_dashboard/index.html', context)


def _projects_versions(projects, regex=None, tag_only=False):
    res = []
    for project in projects:
        info = {
            'name': project,
            'tags': get_tags(project, regex),
        }
        if not tag_only:
            info['branches'] = get_branches(project, regex)
        res.append(info)
    logger.debug(res)
    return res


def _common_versions(context):
    common_versions = {'tags': set(), 'branches': set()}

    for project in context['projects']:
        common_versions['tags'] |= set(project['tags'])
        common_versions['branches'] |= set(project['branches'])
    context['common_versions'] = {
        'tags': sorted(common_versions['tags']),
        'branches': sorted(common_versions['branches']),
    }


@require_http_methods(["POST", ])
def hotfix(request, branch, project):
    if project not in rd_settings['projects']:
        error = "repo:%s not valid" % project
        logger.error(error)
        return HttpResponseNotFound(error)
    if not regex_hotfix.match(branch):
        error = "branch:%s not valid. Not mrX.X.X format" % branch
        logger.error(error)
        return HttpResponseNotFound(error)
    proj = Project.objects.get(name=project)
    if branch not in proj.branches_mrXXX():
        error = "branch:%s not valid" % branch
        logger.error(error)
        return HttpResponseNotFound(error)
    logger.warn("Not implemented")
    return JsonResponse({'url': trigger_hotfix(project, branch)})


def build_deps(request):
    regex = re.compile(r'^mr.+$')
    context = {
        'projects': _projects_versions(
            rd_settings['build_deps'],
            regex
        ),
        'debian': rd_settings['debian_supported'],
    }
    _common_versions(context)
    return render(request, 'release_dashboard/build_deps.html', context)


def build_release(request):
    context = {
        'projects': _projects_versions(rd_settings['projects'], regex_mr),
        'debian': rd_settings['debian_supported'],
    }
    _common_versions(context)
    return render(request, 'release_dashboard/build.html', context)


@require_http_methods(["POST", ])
def refresh_all(request):
    res = gerrit_fetch_all.delay()
    return JsonResponse({'url': '/flower/task/%s' % res.id})


@require_http_methods(["POST", ])
def refresh(request, project):
    res = gerrit_fetch_info.delay(project)
    return JsonResponse({'url': '/flower/task/%s' % res.id})
