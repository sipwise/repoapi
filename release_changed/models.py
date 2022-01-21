# Copyright (C) 2020 The Sipwise Team - http://sipwise.com
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


class ReleaseChanged(models.Model):
    VMTYPE_CHOICES = (("CE", "spce"), ("PRO", "sppro"), ("CARRIER", "carrier"))
    RESULT_CHOICES = (
        ("ABORTED", "ABORTED"),
        ("FAILURE", "FAILURE"),
        ("NOT_BUILT", "NOT_BUILT"),
        ("SUCCESS", "SUCCESS"),
        ("UNSTABLE", "UNSTABLE"),
    )
    version = models.CharField(max_length=64, null=False)
    vmtype = models.CharField(max_length=7, null=False, choices=VMTYPE_CHOICES)
    label = models.CharField(max_length=128, null=False)
    result = models.CharField(
        max_length=50, null=False, choices=RESULT_CHOICES
    )
    date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("version", "vmtype", "label"),)

    def __str__(self):
        return "{0.label}_{0.vmtype}_{0.version}_{0.result}".format(self)
