# Copyright (C) 2015-2023 The Sipwise Team - http://sipwise.com
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
from django.contrib import admin
from django.utils.html import format_html
from django_admin_filters import DateRange
from import_export import resources
from import_export.admin import ExportActionModelAdmin
from import_export.admin import ImportExportModelAdmin

from . import models


class JenkinsBuildInfoResource(resources.ModelResource):
    class Meta:
        model = models.JenkinsBuildInfo


class GerritRepoInfoResource(resources.ModelResource):
    class Meta:
        model = models.GerritRepoInfo


@admin.register(models.JenkinsBuildInfo)
class JenkinsBuildInfoAdmin(ImportExportModelAdmin, ExportActionModelAdmin):
    resource_class = JenkinsBuildInfoResource
    list_filter = ("param_release", "projectname")


class GRIDateRange(DateRange):
    FILTER_LABEL = "Modified range"
    BUTTON_LABEL = "Select range"
    FROM_LABEL = "From"
    TO_LABEL = "To"
    ALL_LABEL = "All"
    CUSTOM_LABEL = "custom range"
    DATE_FORMAT = "YYYY-MM-DD HH:mm"

    is_null_option = False

    day_val = 60 * 60 * 24
    month_val = day_val * 30
    options = (
        ("1dp", "last 24 hours", -day_val),
        ("1mp", "last 30 days", -month_val),
        ("3mp", "last 3 months", -month_val * 3),
    )


@admin.register(models.GerritRepoInfo)
class GerritRepoInfoAdmin(ImportExportModelAdmin, ExportActionModelAdmin):
    resource_class = GerritRepoInfoResource
    list_filter = (("modified", GRIDateRange), "projectname", "param_ppa")
    readonly_fields = ("gerrit_url",)

    def gerrit_url(self, obj):
        return format_html("<a href='{url}'>{url}</a>", url=obj.gerrit_url)


class WorkfrontNoteInfoResource(resources.ModelResource):
    class Meta:
        model = models.WorkfrontNoteInfo


@admin.register(models.WorkfrontNoteInfo)
class WorkfrontNoteInfoAdmin(ImportExportModelAdmin, ExportActionModelAdmin):
    resource_class = WorkfrontNoteInfoResource


class MantisNoteInfoResource(resources.ModelResource):
    class Meta:
        model = models.MantisNoteInfo


@admin.register(models.MantisNoteInfo)
class MantisNoteInfoAdmin(ImportExportModelAdmin, ExportActionModelAdmin):
    resource_class = MantisNoteInfoResource
