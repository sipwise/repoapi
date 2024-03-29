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
import re

from django.db import models
from django.db.models import Q

from . import utils
from .conf import MapperType
from .conf import Tracker
from .conf import TrackerConf

tracker_settings = TrackerConf()


class TrackerInfo(models.Model):
    tracker_re = re.compile(tracker_settings.REGEX[Tracker.NONE])

    class Meta:
        abstract = True

    @classmethod
    def getIds(cls, change):
        """
        parses text searching for tracker occurrences
        returns a list of IDs
        """
        res = ()
        if change:
            res = cls.tracker_re.findall(change)
        return set(res)

    @property
    def field_id(self):
        return getattr(self, self.field_id_name)


class WorkfrontInfo(TrackerInfo):
    workfront_id = models.CharField(max_length=50, null=False)
    tracker_re = re.compile(tracker_settings.REGEX[Tracker.WORKFRONT])
    field_id_name = "workfront_id"

    class Meta:
        abstract = True

    def send(self, msg: str):
        return utils.workfront_note_send(self.workfront_id, msg)

    def set_target_release(self, release):
        return utils.workfront_set_release_target(self.workfront_id, release)


class MantisInfo(TrackerInfo):
    mantis_id = models.CharField(max_length=50, null=False)
    tracker_re = re.compile(tracker_settings.REGEX[Tracker.MANTIS])
    field_id_name = "mantis_id"

    class Meta:
        abstract = True

    @classmethod
    def getIds(cls, change):
        from tracker.conf import settings

        res = super().getIds(change)
        if change and settings.TRACKER_WORKFRONT_MAPPER_IDS:
            old_ids = WorkfrontInfo.getIds(change)
            qs = TrackerMapper.objects.get_wf_qs(old_ids)
            for wf in qs:
                res.add(wf.mantis_id)
        return res

    def send(self, msg: str):
        return utils.mantis_note_send(self.mantis_id, msg)

    def set_target_release(self, release):
        return utils.mantis_set_release_target(self.mantis_id, release)


class TrackerMapperManager(models.Manager):
    def get_wf_qs(self, _ids):
        return (
            self.get_queryset()
            .filter(workfront_id__in=_ids)
            .order_by("mantis_id")
        )

    def get_workfront_issue_qs(self, _id):
        return self.get_queryset().filter(
            Q(workfront_id=_id) | Q(workfront_uuid=_id),
            mapper_type=MapperType.ISSUE,
        )

    def get_workfront_task_qs(self, _id):
        return self.get_queryset().filter(
            Q(workfront_id=_id) | Q(workfront_uuid=_id),
            mapper_type=MapperType.TASK,
        )


class TrackerMapper(models.Model):
    mapper_type = models.CharField(
        max_length=50, choices=[(tag, tag.value) for tag in MapperType]
    )
    mantis_id = models.CharField(max_length=50, null=False, unique=True)
    workfront_id = models.CharField(max_length=50, null=False, unique=True)
    workfront_uuid = models.CharField(max_length=50, null=False, unique=True)
    objects = TrackerMapperManager()

    def __str__(self):
        return f"{self.mapper_type}:TT#{self.workfront_id}:MT#{self.mantis_id}"
