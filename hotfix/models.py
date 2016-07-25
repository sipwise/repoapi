# Copyright (C) 2015 The Sipwise Team - http://sipwise.com

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
import logging
import re

from django.db import models
from django.db.models.signals import post_save
from django.conf import settings

logger = logging.getLogger(__name__)
workfront_re = re.compile(r"TT#(\d+)")


class WorkfrontNoteInfo(models.Model):
    workfront_id = models.CharField(max_length=50, null=False)
    projectname = models.CharField(max_length=50, null=False)
    version = models.CharField(max_length=50, null=False)

    class Meta:
        unique_together = [
            "workfront_id",
            "projectname",
            "version"
        ]

    @staticmethod
    def getIds(change):
        """
        parses text searching for Workfront TT# ocurrences
        returns a list of IDs
        """
        if change:
            res = workfront_re.findall(change)
            return set(res)
        else:
            return set()
