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
            tag=config.tag,
            branch=config.branch,
            release=config.release,
            distribution=config.debian_release,
            projects=config.projects,
        )


class BuildRelease(models.Model):
    uuid = models.CharField(max_length=64, unique=True, null=False)
    start_date = models.DateTimeField(auto_now_add=True)
    tag = models.CharField(max_length=50, null=True, blank=True)
    branch = models.CharField(max_length=50, null=False)
    release = models.CharField(max_length=50, null=False, db_index=True)
    distribution = models.CharField(max_length=50, null=False, editable=False)
    projects = models.TextField(null=False, editable=False)
    built_projects = models.TextField(null=True, editable=False)
    objects = BuildReleaseManager()

    def __str__(self):
        return "%s[%s]" % (self.release, self.uuid)

    @property
    def projects_list(self):
        return [x.strip() for x in self.projects.split(",")]

    @property
    def built_projects_list(self):
        return [x.strip() for x in self.built_projects.split(",")]

    def append_built(self, jbi_instance):
        if jbi_instance.result == "SUCCESS":
            self.built_projects += ",{}".format(jbi_instance.projectname)
        self.save()

    @property
    def branch_or_tag(self):
        if self.tag:
            return "tag/{}".format(self.tag)
        return "branch/{}".format(self.branch)

    @property
    def next(self):
        return self._foo

    @property
    def build_deps(self):
        if getattr(self, "_build_deps", None) is None:
            self._build_deps = [
                list(self.config.wanna_build_deps(0)),
                list(self.config.wanna_build_deps(1)),
            ]
        return self._build_deps

    # @property
    # def is_build_deps_done(self):
    #     built_list = self.built_projects_list
    #     if all(prj in built_list for prj in self.build_deps[0])
    #     for prj in :

    @property
    def config(self):
        if getattr(self, "_config", None) is None:
            self._config = ReleaseConfig(self.release)
        return self._config
