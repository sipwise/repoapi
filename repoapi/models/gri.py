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
from django.db import models
from django_extensions.db.fields import CreationDateTimeField
from django_extensions.db.fields import ModificationDateTimeField


class GerritRepoInfo(models.Model):
    param_ppa = models.CharField(max_length=50, null=False)
    gerrit_change = models.CharField(max_length=50, null=False)
    projectname = models.CharField(max_length=100)
    created = CreationDateTimeField()
    modified = ModificationDateTimeField()

    class Meta:
        unique_together = ["param_ppa", "gerrit_change"]

    def __str__(self):
        return "{}:{}:{}".format(
            self.param_ppa, self.gerrit_change, self.projectname
        )
