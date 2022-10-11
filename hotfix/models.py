# Copyright (C) 2015-2022 The Sipwise Team - http://sipwise.com
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

import structlog
from django.db import models

from .conf import settings
from tracker.conf import Tracker
from tracker.exceptions import TrackerNotDefined
from tracker.models import MantisInfo
from tracker.models import TrackerInfo
from tracker.models import WorkfrontInfo

hotfix_re_release = re.compile(r".+~(mr[0-9]+\.[0-9]+\.[0-9]+.[0-9]+)$")
logger = structlog.get_logger(__name__)


class NoteInfo(TrackerInfo):
    projectname = models.CharField(max_length=50, null=False)
    version = models.CharField(max_length=50, null=False)

    class Meta:
        abstract = True

    @staticmethod
    def get_target_release(version):
        match = hotfix_re_release.search(version)
        if match:
            return match.group(1)

    @property
    def target_release(self):
        return NoteInfo.get_target_release(self.version)

    @staticmethod
    def get_model():
        if settings.TRACKER_PROVIDER == Tracker.MANTIS:
            return MantisNoteInfo
        elif settings.TRACKER_PROVIDER == Tracker.WORKFRONT:
            return WorkfrontNoteInfo
        return NoteInfo

    @staticmethod
    def create(wid, projectname, version, force=False):
        note, created = NoteInfo.get_or_create(
            field_id=wid, projectname=projectname, version=version
        )
        if created or force:
            msg = "hotfix %s.git %s triggered" % (
                note.projectname,
                note.version,
            )
            note.send(msg)
            target_release = note.target_release
            structlog.contextvars.bind_contextvars(
                target_release=target_release
            )
            if target_release:
                logger.info("set_target_release")
                note.set_target_release()

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

    def __str__(self):
        return f"{self.field_id}:{self.projectname}:{self.version}"


class WorkfrontNoteInfo(NoteInfo, WorkfrontInfo):
    class Meta:
        unique_together = ["workfront_id", "projectname", "version"]

    def set_target_release(self):
        return super(WorkfrontNoteInfo, self).set_target_release(
            self.target_release
        )


class MantisNoteInfo(NoteInfo, MantisInfo):
    class Meta:
        unique_together = ["mantis_id", "projectname", "version"]

    def set_target_release(self):
        return super(MantisNoteInfo, self).set_target_release(
            self.target_release
        )
