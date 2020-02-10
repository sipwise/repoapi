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
import json
import uuid
from django.shortcuts import render
from django.http import HttpResponseNotFound, JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from release_dashboard.models import Project
from release_dashboard.utils import build
from release_dashboard.tasks import gerrit_fetch_info, gerrit_fetch_all
from release_dashboard.forms.build import BuildDepForm, BuildReleaseForm
from release_dashboard.forms.build import BuildTrunkDepForm
from release_dashboard.forms.build import BuildTrunkReleaseForm
from release_dashboard.forms import trunk_projects, trunk_build_deps
from release_dashboard.forms import rd_settings
from . import _projects_versions, _common_versions, _hash_versions
from . import regex_hotfix, regex_master, regex_mr

logger = logging.getLogger(__name__)


def index(request):
    context = {}
    return render(request, "release_dashboard/index.html", context)


@login_required
@require_http_methods(["POST"])
def hotfix_build(request, branch, project):
    if project not in rd_settings["projects"]:
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
    if json_data["push"] == "no":
        logger.warn("dryrun for %s:%s", project, branch)
    url = build.trigger_hotfix(project, branch, json_data["push"])
    return JsonResponse({"url": url})


def _build_logic(form, projects):
    version_release = form.cleaned_data["version_release"]
    distribution = form.cleaned_data["distribution"]
    result = _hash_versions(form.cleaned_data, projects)
    context = {"projects": [], "release": version_release}
    flow_uuid = uuid.uuid4()
    msg = "trying to trigger release %s, project %s"
    for pro in projects:
        try:
            logger.debug(msg, version_release, pro)
            url = build.trigger_build(
                "%s-get-code" % pro,
                version_release,
                result[pro],
                distribution,
                flow_uuid,
            )
            context["projects"].append({"name": pro, "url": url})
        except KeyError:
            msg = "Houston, we have a problem with trigger for %s"
            logger.error(msg, pro)
            context["projects"].append({"name": pro, "url": None})
    return context


@login_required
def build_deps(request, tag_only=False):
    if request.method == "POST":
        form = BuildDepForm(request.POST)
        if form.is_valid():
            context = _build_logic(form, rd_settings["build_deps"])
        else:
            context = {"error": "form validation error"}
        return render(request, "release_dashboard/build_result.html", context)
    else:
        context = {
            "projects": _projects_versions(
                rd_settings["build_deps"], regex_mr, True, not tag_only,
            ),
            "debian": rd_settings["debian_supported"],
        }
        _common_versions(context, True, not tag_only)
        return render(request, "release_dashboard/build_deps.html", context)


@login_required
def hotfix(request):
    prj_list = _projects_versions(rd_settings["projects"], regex_hotfix)
    context = {"projects": prj_list}
    return render(request, "release_dashboard/hotfix.html", context)


@login_required
def build_release(request, tag_only=False):
    if request.method == "POST":
        form = BuildReleaseForm(request.POST)
        if form.is_valid():
            context = _build_logic(form, rd_settings["projects"])
        else:
            context = {"error": "form validation error"}
        return render(request, "release_dashboard/build_result.html", context)
    else:
        context = {
            "projects": _projects_versions(
                rd_settings["projects"], regex_mr, True, not tag_only,
            ),
            "debian": rd_settings["debian_supported"],
        }
        _common_versions(context, True, not tag_only)
        if tag_only:
            return render(request, "release_dashboard/build_tag.html", context)
        return render(request, "release_dashboard/build.html", context)


@login_required
def refresh_all(request):
    if request.method == "POST":
        res = gerrit_fetch_all.delay()
        return JsonResponse({"url": "/flower/task/%s" % res.id})
    else:
        template = "release_dashboard/refresh.html"
        projects = []
        for project in rd_settings["projects"]:
            info = {"name": project, "tags": None}
            projects.append(info)
        return render(request, template, {"projects": projects})


@require_http_methods(["POST"])
def refresh(request, project):
    res = gerrit_fetch_info.delay(project)
    return JsonResponse({"url": "/flower/task/%s" % res.id})


@login_required
def build_trunk_deps(request):
    if request.method == "POST":
        form = BuildTrunkDepForm(request.POST)
        if form.is_valid():
            context = _build_logic(form, rd_settings["build_deps"])
        else:
            context = {"error": "form validation error"}
        return render(request, "release_dashboard/build_result.html", context)
    else:
        template = "release_dashboard/build_trunk_deps.html"
        context = {
            "projects": _projects_versions(trunk_build_deps, regex_master,),
            "common_versions": {"tags": [], "branches": ["master"]},
            "debian": rd_settings["debian_supported"],
        }
        return render(request, template, context)


@login_required
def build_trunk_release(request):
    if request.method == "POST":
        form = BuildTrunkReleaseForm(request.POST)
        if form.is_valid():
            context = _build_logic(form, trunk_projects)
        else:
            context = {"error": "form validation error"}
        return render(request, "release_dashboard/build_result.html", context)
    else:
        context = {
            "projects": _projects_versions(trunk_projects, regex_master,),
            "common_versions": {"tags": [], "branches": ["master"]},
            "debian": rd_settings["debian_supported"],
        }
        return render(request, "release_dashboard/build_trunk.html", context)
