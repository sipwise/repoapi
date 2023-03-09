# Copyright (C) 2022-2023 The Sipwise Team - http://sipwise.com
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
import re

from django.contrib import admin
from django.utils.html import format_html
from import_export import resources
from import_export.admin import ExportActionModelAdmin
from import_export.admin import ImportExportModelAdmin

from . import models


class BuildInfoResource(resources.ModelResource):
    class Meta:
        model = models.BuildInfo


class DurationListFilter(admin.SimpleListFilter):
    title = "duration"
    parameter_name = "range"

    def lookups(self, request, model_admin):
        vals = [120, 60, 30, 15]
        return [(f"{val}s", f"higher than {val} secs") for val in vals]

    def queryset(self, request, queryset):
        if self.value():
            matched = re.match(r"(\d+)s", self.value())
            if matched:
                value = int(matched.group(1)) * 1000
                return queryset.filter(duration__gte=value)


class JobTypeListFilter(admin.SimpleListFilter):
    title = "job type"
    parameter_name = "type"

    def lookups(self, request, model_admin):
        vals = [
            "gerrit",
            "get-code",
            "source-tests",
            "debian-check",
            "manage-docker",
            "source",
            "tap-test",
            "binaries",
            "repos",
            "piuparts",
            "docker-ppa",
            "docker-ppa-dummy",
        ]
        return [(f"{val}", f"*-{val}") for val in vals]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(jobname__endswith=value)


@admin.register(models.BuildInfo)
class BuildInfoAdmin(ImportExportModelAdmin, ExportActionModelAdmin):
    resource_class = BuildInfoResource
    list_filter = (
        DurationListFilter,
        JobTypeListFilter,
        "param_release",
        "projectname",
        "param_distribution",
        "builton",
    )
    readonly_fields = ["jenkins_url"]
    ordering = ["-duration"]

    def jenkins_url(self, obj):
        return format_html("<a href='{url}'>{url}</a>", url=obj.jenkins_url)
