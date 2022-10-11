# Copyright (C) 2022 The Sipwise Team - http://sipwise.com
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


class WorkfrontNoteInfoResource(resources.ModelResource):
    class Meta:
        model = models.WorkfrontNoteInfo


@admin.register(models.WorkfrontNoteInfo)
class WorkfrontNoteInfoAdmin(ImportExportModelAdmin):
    resource_class = WorkfrontNoteInfoResource
    list_filter = ("projectname",)


class MantisNoteInfoResource(resources.ModelResource):
    class Meta:
        model = models.MantisNoteInfo


@admin.register(models.MantisNoteInfo)
class MantisNoteInfoAdmin(ImportExportModelAdmin):
    resource_class = MantisNoteInfoResource
    list_filter = ("projectname",)
