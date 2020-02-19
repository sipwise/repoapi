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
from rest_framework import serializers

from . import exceptions as err
from . import models
from .utils import ReleaseConfig


class BuildReleaseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.BuildRelease
        fields = "__all__"
        read_only_fields = ["tag", "branch", "distribution", "projects"]
        extra_kwargs = {"url": {"view_name": "build:detail"}}

    def validate_release(self, value):
        try:
            self.release_config = ReleaseConfig(value)
        except err.NoConfigReleaseFile:
            raise serializers.ValidationError("{} unknown".format(value))
        except err.NoJenkinsJobsInfo:
            raise serializers.ValidationError(
                "{} has no jenkins-job info".format(value)
            )
        return self.release_config.release

    def create(self, validate_data):
        return self.Meta.model.objects.create_build_release(
            validate_data["uuid"], validate_data["release"]
        )
