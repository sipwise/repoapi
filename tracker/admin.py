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
from django.contrib import admin
from import_export import resources
from import_export.admin import ExportActionModelAdmin
from import_export.admin import ImportExportModelAdmin

from . import models


class TrackerMapperResource(resources.ModelResource):
    class Meta:
        model = models.TrackerMapper
        import_id_fields = ["mantis_id"]
        use_bulk = True
        skip_unchanged = True

    def skip_row(self, instance, original, row, import_validation_errors=None):
        try:
            mantis_id = int(original.mantis_id)
        except ValueError:
            return False
        return instance.mantis_id == mantis_id


@admin.register(models.TrackerMapper)
class TrackerMapperAdmin(ImportExportModelAdmin, ExportActionModelAdmin):
    resource_class = TrackerMapperResource
    list_filter = ["mapper_type"]
