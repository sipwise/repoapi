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
from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from . import models


class JenkinsBuildInfoResource(resources.ModelResource):
    class Meta:
        model = models.JenkinsBuildInfo


class GerritRepoInfoResource(resources.ModelResource):
    class Meta:
        model = models.GerritRepoInfo


@admin.register(models.JenkinsBuildInfo)
class JenkinsBuildInfoAdmin(ImportExportModelAdmin):
    resource_class = JenkinsBuildInfoResource
    list_filter = ("param_release", "projectname")


@admin.register(models.GerritRepoInfo)
class GerritRepoInfoAdmin(ImportExportModelAdmin):
    resource_class = GerritRepoInfoResource
    list_filter = ("param_ppa", "projectname")


class WorkfrontNoteInfoResource(resources.ModelResource):
    class Meta:
        model = models.WorkfrontNoteInfo


@admin.register(models.WorkfrontNoteInfo)
class WorkfrontNoteInfoAdmin(ImportExportModelAdmin):
    resource_class = WorkfrontNoteInfoResource


class MantisNoteInfoResource(resources.ModelResource):
    class Meta:
        model = models.MantisNoteInfo


@admin.register(models.MantisNoteInfo)
class MantisNoteInfoAdmin(ImportExportModelAdmin):
    resource_class = MantisNoteInfoResource
