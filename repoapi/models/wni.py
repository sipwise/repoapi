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
import re

from django.db import models

from repoapi.conf import settings
from tracker.conf import Tracker
from tracker.exceptions import TrackerNotDefined
from tracker.models import MantisInfo
from tracker.models import TrackerInfo
from tracker.models import WorkfrontInfo

commit_re = re.compile(r"^(\w{7}) ")


class NoteInfo(TrackerInfo):
    gerrit_change = models.CharField(max_length=50, null=False)
    eventtype = models.CharField(max_length=50, null=False)

    class Meta:
        abstract = True

    @staticmethod
    def get_model():
        if settings.TRACKER_PROVIDER == Tracker.MANTIS:
            return MantisNoteInfo
        elif settings.TRACKER_PROVIDER == Tracker.WORKFRONT:
            return WorkfrontNoteInfo
        return NoteInfo

    @classmethod
    def get_or_create(cls, defaults=None, **kwargs):
        field_id = kwargs.pop("field_id")
        if settings.TRACKER_PROVIDER == Tracker.MANTIS:
            model = MantisNoteInfo
            kwargs["mantis_id"] = field_id
        elif settings.TRACKER_PROVIDER == Tracker.WORKFRONT:
            model = WorkfrontNoteInfo
            kwargs["workfront_id"] = field_id
        else:
            raise TrackerNotDefined()
        return model.objects.get_or_create(defaults, **kwargs)

    @staticmethod
    def getCommit(git_comment):
        """
        parses git_commit_msg searching for short GIT_COMMIT
        """
        if git_comment:
            res = commit_re.search(git_comment)
            if res:
                return res.group(1)

    def __str__(self):
        return "%s:%s" % (self.field_id, self.gerrit_change)


class WorkfrontNoteInfo(NoteInfo, WorkfrontInfo):
    class Meta:
        unique_together = ["workfront_id", "gerrit_change", "eventtype"]


class MantisNoteInfo(NoteInfo, MantisInfo):
    class Meta:
        unique_together = ["mantis_id", "gerrit_change", "eventtype"]
