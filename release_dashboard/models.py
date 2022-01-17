# Copyright (C) 2016-2022 The Sipwise Team - http://sipwise.com
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
import json
import logging
import re
from datetime import datetime

from django.db import models
from django_extensions.db.fields import ModificationDateTimeField

from .conf import settings

logger = logging.getLogger(__name__)


class Project(models.Model):
    name = models.CharField(max_length=50, unique=True, null=False)
    json_tags = models.JSONField(null=True)
    json_branches = models.JSONField(null=True)
    modified = ModificationDateTimeField(null=True)

    @classmethod
    def _filter_values(cls, values, val_ok_filter, regex=None):
        if values is None:
            return list()
        res = set()

        for value in values:
            match = re.search(val_ok_filter, value["ref"])
            if match:
                val_ok = match.group(1)
                if regex is not None:
                    if re.search(regex, val_ok):
                        res.add(val_ok)
                else:
                    res.add(val_ok)
        return sorted(res, reverse=True)

    @classmethod
    def _get_filtered_json(cls, text):
        """gerrit responds with malformed json
        https://gerrit-review.googlesource.com/Documentation/rest-api.html#output
        """
        return json.loads(text[5:])

    def __str__(self):
        return self.name

    @property
    def tags(self):
        return Project._filter_values(
            self.json_tags, settings.RELEASE_DASHBOARD_FILTER_TAGS
        )

    @tags.setter
    def tags(self, value):
        self.json_tags = Project._get_filtered_json(value)

    @property
    def branches(self):
        return Project._filter_values(
            self.json_branches, settings.RELEASE_DASHBOARD_FILTER_BRANCHES
        )

    @branches.setter
    def branches(self, value):
        self.json_branches = Project._get_filtered_json(value)

    def filter_tags(self, regex):
        return Project._filter_values(
            self.json_tags, settings.RELEASE_DASHBOARD_FILTER_TAGS, regex
        )

    def filter_branches(self, regex):
        return Project._filter_values(
            self.json_branches,
            settings.RELEASE_DASHBOARD_FILTER_BRANCHES,
            regex,
        )

    def filter_docker_images(self, images):
        r = re.compile(self.name)
        return filter(r.search, images)

    def branches_mrXX(self):
        return self.filter_branches(settings.RELEASE_DASHBOARD_FILTER_MRXX)

    def branches_mrXXX(self):
        return self.filter_branches(settings.RELEASE_DASHBOARD_FILTER_MRXXX)


class DockerImageManager(models.Manager):
    def images_with_tags(self, project=None):
        qs = self.get_queryset().filter(dockertag__isnull=False)
        if project:
            qs = qs.filter(project__name=project)
        return qs.distinct()


class DockerImage(models.Model):
    name = models.CharField(max_length=50, unique=True, null=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    objects = DockerImageManager()

    def __str__(self):
        return "%s[%s]" % (self.name, self.project.name)

    @property
    def tags(self):
        res = self.dockertag_set.all().values_list("name", flat=True)
        return res


class DockerTag(models.Model):
    name = models.CharField(max_length=50, null=False)
    manifests = models.JSONField(null=False)
    image = models.ForeignKey(DockerImage, on_delete=models.CASCADE)
    reference = models.CharField(max_length=150, unique=True, null=False)

    class Meta:
        unique_together = (("name", "image"),)

    def __str__(self):
        return "%s:%s" % (self.image.name, self.name)

    @property
    def date(self):
        if self.manifests is None:
            return None
        if isinstance(self.manifests, dict):
            manifests = self.manifests
        else:
            try:
                manifests = json.loads(self.manifests)
            except json.JSONDecodeError:
                return None
        try:
            value = manifests["history"][0]["v1Compatibility"]
            time = json.loads(value)
            created = time["created"].split(".")
            return datetime.strptime(created[0], "%Y-%m-%dT%H:%M:%S")
        except json.JSONDecodeError:
            return None
