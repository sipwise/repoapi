# Copyright (C) 2017 The Sipwise Team - http://sipwise.com

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

from rest_framework import serializers
from . import models


class BuildReleaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.BuildRelease

    def validate_projects(self, value):
        projects = [x.strip() for x in value.split(',')]
        if len(projects) <= 0:
            raise serializers.ValidationError(
                "projects is not a list of coma separate elements")
        return ','.join(projects)
