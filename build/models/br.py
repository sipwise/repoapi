# Copyright (C) 2017 The Sipwise Team - http://sipwise.com

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

from django.db import models

from build.utils import ReleaseConfig


class BuildReleaseManager(models.Manager):
    def create_build_release(self, uuid, release):
        config = ReleaseConfig(release)
        return self.create(
            uuid=uuid,
            release=config.release,
            distribution=config.debian_release,
            projects=config.projects,
        )


class BuildRelease(models.Model):
    uuid = models.CharField(max_length=64, unique=True, null=False)
    start_date = models.DateTimeField(auto_now_add=True)
    tag = models.CharField(
        max_length=50, null=True, blank=True, editable=False
    )
    branch = models.CharField(max_length=50, null=False, editable=False)
    release = models.CharField(max_length=50, null=False, db_index=True)
    distribution = models.CharField(max_length=50, null=False, editable=False)
    projects = models.TextField(null=False, editable=False)
    objects = BuildReleaseManager()

    def __str__(self):
        return "%s[%s]" % (self.release, self.uuid)

    @property
    def projects_list(self):
        return [x.strip() for x in self.projects.split(",")]
