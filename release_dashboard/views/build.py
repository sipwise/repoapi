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
import json
import logging
import uuid

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from . import _common_versions
from . import _hash_versions
from . import _projects_versions
from . import regex_hotfix
from . import regex_master
from . import regex_mr
from build.models import BuildRelease
from build.utils import ReleaseConfig
from release_dashboard.forms import rd_settings
from release_dashboard.forms import trunk_build_deps
from release_dashboard.forms import trunk_projects
from release_dashboard.forms.build import BuildDepForm
from release_dashboard.forms.build import BuildReleaseForm
from release_dashboard.forms.build import BuildTrunkDepForm
from release_dashboard.forms.build import BuildTrunkReleaseForm
from release_dashboard.models import Project
from release_dashboard.tasks import gerrit_fetch_all
from release_dashboard.tasks import gerrit_fetch_info
from release_dashboard.utils import build

logger = logging.getLogger(__name__)


@login_required
def index(request):
    context = {"releases": ReleaseConfig.supported_releases()}
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
        context = {
            "config": release_config,
            "build_releases": BuildRelease.objects.filter(
                release=release_config.release
            ),
            "build_deps": list(release_config.build_deps.keys()),
        }
        return render(request, "release_dashboard/build_release.html", context)


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
def build_deps_old(request, tag_only=False):
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
def build_release_old(request, tag_only=False):

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
def build_trunk_deps_old(request):
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
def build_trunk_release_old(request):
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
