# Copyright (C) 2016-2023 The Sipwise Team - http://sipwise.com
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
from import_export.admin import ExportActionModelAdmin
from import_export.admin import ImportExportModelAdmin

from . import models


class ProjectResource(resources.ModelResource):
    class Meta:
        model = models.Project


class DockerTagResource(resources.ModelResource):
    class Meta:
        model = models.DockerTag


class DockerImageResource(resources.ModelResource):
    class Meta:
        model = models.DockerImage


@admin.register(models.DockerTag)
class DockerTagAdmin(ImportExportModelAdmin, ExportActionModelAdmin):
    resource_class = DockerTagResource


@admin.register(models.DockerImage)
class DockerImageAdmin(ImportExportModelAdmin, ExportActionModelAdmin):
    resource_class = DockerImageResource


@admin.register(models.Project)
class ProjectAdmin(ImportExportModelAdmin, ExportActionModelAdmin):
    resource_class = ProjectResource
