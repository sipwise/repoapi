# Copyright (C) 2015-2022 The Sipwise Team - http://sipwise.com
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
import json
import uuid

import structlog
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from . import _projects_versions
from . import regex_hotfix
from ..conf import settings
from ..models import Project
from ..tasks import gerrit_fetch_all
from ..tasks import gerrit_fetch_info
from ..utils import build
from build.models import BuildRelease
from build.utils import ReleaseConfig

logger = structlog.get_logger(__name__)


@login_required
def index(request):
    context = {
        "releases": ReleaseConfig.supported_releases_dict(),
        "builds": BuildRelease.objects.releases_with_builds(),
    }
    return render(
        request, "release_dashboard/build_supported_releases.html", context
    )


@login_required
def build_release(request, release):
    release_config = ReleaseConfig(release)
    if request.method == "POST":
        release_uuid = uuid.uuid4()
        BuildRelease.objects.create_build_release(release_uuid, release)
        return HttpResponseRedirect(
            reverse("panel:release-uuid", args=(release_uuid,))
        )
    else:
        build_releases = BuildRelease.objects.release(
            release_config.release, release_config.debian_release
        ).order_by("-start_date")
        if build_releases.count() == 0:
            done = True
        else:
            done = build_releases.first().done
        context = {
            "gerrit_url": settings.GERRIT_URL.format("gitweb?p="),
            "config": release_config,
            "build_releases": build_releases,
            "build_deps": list(release_config.build_deps.keys()),
            "done": done,
        }
        return render(request, "release_dashboard/build_release.html", context)


@login_required
@require_http_methods(["POST"])
def hotfix_build(request, branch, project):
    if project not in settings.RELEASE_DASHBOARD_PROJECTS:
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

    json_data = json.loads(request.body.decode("utf-8"))
    push = json_data.get("push", "no")
    empty = json_data.get("empty", False)
    if push == "no":
        logger.warn("dry-run for %s:%s", project, branch)
    urls = build.trigger_hotfix(project, branch, request.user, push, empty)
    return JsonResponse({"urls": urls})


@login_required
def hotfix(request):
    prj_list = _projects_versions(
        settings.RELEASE_DASHBOARD_PROJECTS, regex_hotfix
    )
    context = {"projects": prj_list}
    return render(request, "release_dashboard/hotfix.html", context)


@login_required
def refresh_all(request):
    if request.method == "POST":
        res = gerrit_fetch_all.delay()
        return JsonResponse({"url": "/flower/task/%s" % res.id})
    else:
        template = "release_dashboard/refresh.html"
        projects = []
        for project in settings.RELEASE_DASHBOARD_PROJECTS:
            info = {"name": project, "tags": None}
            projects.append(info)
        return render(request, template, {"projects": projects})


@require_http_methods(["POST"])
def refresh(request, project):
    res = gerrit_fetch_info.delay(project)
    return JsonResponse({"url": "/flower/task/%s" % res.id})
