# Copyright (C) 2017 The Sipwise Team - http://sipwise.com
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

from . import models


@admin.register(models.BuildRelease)
class BuildReleaseAdmin(admin.ModelAdmin):
    list_filter = ("release",)
    readonly_fields = ("projects",)
    modify_readonly_fields = (
        "uuid",
        "release",
        "projects",
    )

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return self.readonly_fields
        return self.modify_readonly_fields

    def save_model(self, request, obj, form, change):
        if change:
            super(BuildReleaseAdmin, self).save_model(
                request, obj, form, change
            )
        else:
            new_obj = models.BuildRelease.objects.create_build_release(
                uuid=obj.uuid, release=obj.release
            )
            obj.pk = new_obj.pk
