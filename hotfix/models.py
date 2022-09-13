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

from django.db import models
from natsort import humansorted

from .conf import settings
from .conf import Tracker
from .exceptions import TrackerNotDefined

hotfix_re_release = re.compile(r".+~(mr[0-9]+\.[0-9]+\.[0-9]+.[0-9]+)$")


class NoteInfo(models.Model):
    projectname = models.CharField(max_length=50, null=False)
    version = models.CharField(max_length=50, null=False)
    tracker_re = re.compile(settings.HOTFIX_REGEX[Tracker.NONE])

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
        if settings.REPOAPI_TRACKER == Tracker.MANTIS:
            return MantisNoteInfo
        elif settings.REPOAPI_TRACKER == Tracker.WORKFRONT:
            return WorkfrontNoteInfo
        return NoteInfo

    @staticmethod
    def create(wid, projectname, version):
        note, created = NoteInfo.get_or_create(
            field_id=wid, projectname=projectname, version=version
        )
        if created:
            msg = "hotfix %s.git %s triggered" % (
                note.projectname,
                note.version,
            )
            note.send(msg)
            target_release = note.target_release
            if target_release:
                note.set_target_release()

    @classmethod
    def get_or_create(cls, defaults=None, **kwargs):
        field_id = kwargs.pop("field_id")
        if settings.REPOAPI_TRACKER == Tracker.MANTIS:
            model = MantisNoteInfo
            kwargs["mantis_id"] = field_id
        elif settings.REPOAPI_TRACKER == Tracker.WORKFRONT:
            model = WorkfrontNoteInfo
            kwargs["workfront_id"] = field_id
        else:
            raise TrackerNotDefined()
        return model.objects.get_or_create(defaults, **kwargs)

    @classmethod
    def getIds(cls, change):
        """
        parses text searching for tracker occurrences
        returns a list of IDs
        """
        if change:
            res = cls.tracker_re.findall(change)
            return set(res)
        else:
            return set()


class WorkfrontNoteInfo(NoteInfo):
    workfront_id = models.CharField(max_length=50, null=False)
    tracker_re = re.compile(settings.HOTFIX_REGEX[Tracker.WORKFRONT])

    class Meta:
        unique_together = ["workfront_id", "projectname", "version"]

    def send(self, msg: str):
        from repoapi import utils

        utils.workfront_note_send(self.workfront_id, msg)

    def set_target_release(self):
        from repoapi import utils

        utils.workfront_set_release_target(
            self.workfront_id, self.target_release
        )


class MantisNoteInfo(NoteInfo):
    mantis_id = models.CharField(max_length=50, null=False)
    tracker_re = re.compile(settings.HOTFIX_REGEX[Tracker.MANTIS])

    class Meta:
        unique_together = ["mantis_id", "projectname", "version"]

    def send(self, msg: str):
        from repoapi import utils

        utils.mantis_note_send(self.mantis_id, msg)

    def set_target_release(self):
        """reconstruct value without asking for previous value"""
        from repoapi import utils

        qs = MantisNoteInfo.objects.filter(mantis_id=self.mantis_id)
        values = qs.values_list("version", flat=True)
        versions = set()
        for val in values:
            target_release = self.get_target_release(val)
            if target_release:
                versions.add(target_release)
        if len(versions) > 0:
            utils.mantis_set_release_target(
                self.mantis_id, ",".join(humansorted(versions))
            )
