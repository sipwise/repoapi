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
from django.db import models


class BuildInfo(models.Model):
    builton = models.CharField(max_length=50, null=False)
    timestamp = models.PositiveBigIntegerField(null=False)
    duration = models.PositiveSmallIntegerField(null=False)

    projectname = models.CharField(max_length=100, null=False)
    buildnumber = models.IntegerField()
    jobname = models.CharField(max_length=100, null=False)
    param_tag = models.CharField(max_length=50, null=True, blank=True)
    param_branch = models.CharField(max_length=50, null=True, blank=True)
    param_release = models.CharField(max_length=50, null=True, db_index=True)
    param_release_uuid = models.CharField(max_length=64, null=True, blank=True)
    param_distribution = models.CharField(max_length=50, null=True, blank=True)
    param_ppa = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return (
            f"{self.jobname}:{self.buildnumber}:"
            f"{self.param_branch}:{self.param_release}"
        )
