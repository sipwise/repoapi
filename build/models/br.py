# Copyright (C) 2017 The Sipwise Team - http://sipwise.com
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
import logging

from django.conf import settings
from django.db import models
from django.forms.models import model_to_dict

from build.utils import ReleaseConfig
from repoapi.models import JenkinsBuildInfo

logger = logging.getLogger(__name__)


class BuildReleaseManager(models.Manager):
    jbi = JenkinsBuildInfo.objects

    def create_build_release(self, uuid, release):
        config = ReleaseConfig(release)
        return self.create(
            uuid=uuid,
            tag=config.tag,
            branch=config.branch,
            release=config.release,
            distribution=config.debian_release,
            projects=",".join(config.projects),
        )

    def release_jobs(self, release_uuid, flat=True):
        qs = self.jbi.get_queryset()
        res = qs.filter(
            jobname__in=settings.RELEASE_JOBS, param_release_uuid=release_uuid,
        ).distinct()
        if res.exists():
            if flat:
                return res.values_list("jobname", flat=True)
            else:
                return res.values("jobname")

    def release_jobs_full(self, release_uuid):
        res = dict()
        jobs = self.release_jobs(release_uuid)
        if jobs is None:
            return res
        for job in jobs:
            uuids = self.release_jobs_uuids(release_uuid, job)
            res[job] = [model_to_dict(x) for x in uuids]
        return res

    def release_jobs_uuids(self, release_uuid, job):
        qs = self.jbi.get_queryset()
        params = {
            "param_release_uuid": release_uuid,
            "jobname": job,
            "tag__isnull": False,
        }
        res = qs.filter(**params).distinct()
        if res.exists():
            return res.order_by("-date")


class BuildRelease(models.Model):
    uuid = models.CharField(max_length=64, unique=True, null=False)
    start_date = models.DateTimeField(auto_now_add=True)
    tag = models.CharField(max_length=50, null=True, blank=True)
    branch = models.CharField(max_length=50, null=False)
    release = models.CharField(max_length=50, null=False, db_index=True)
    distribution = models.CharField(max_length=50, null=False, editable=False)
    projects = models.TextField(null=False, editable=False)
    built_projects = models.TextField(null=True, editable=False)
    failed_projects = models.TextField(null=True, editable=False)
    objects = BuildReleaseManager()

    def __str__(self):
        return "%s[%s]" % (self.release, self.uuid)

    @property
    def projects_list(self):
        return [x.strip() for x in self.projects.split(",")]

    @property
    def built_projects_list(self):
        if self.built_projects is not None:
            return [x.strip() for x in self.built_projects.split(",")]
        return []

    @property
    def queued_projects_list(self):
        return [
            x for x in self.projects_list if x not in self.built_projects_list
        ]

    def _append_falied(self, value):
        if self.failed_projects is None:
            self.failed_projects = value
        else:
            self.failed_projects += ",{}".format(value)
        self.save()

    def _append_built(self, value):
        if self.built_projects is None:
            self.built_projects = value
        else:
            self.built_projects += ",{}".format(value)
        self.save()

    def append_built(self, jbi):
        if jbi.result == "FAILURE":
            self._append_falied(jbi.projectname)
            return True
        if jbi.jobname.endswith("-repos"):
            if jbi.result in ["SUCCESS", "UNSTABLE"]:
                self._append_built(jbi.projectname)
                return True
        return False

    @property
    def branch_or_tag(self):
        if self.tag:
            return "tag/{}".format(self.tag)
        return "branch/{}".format(self.branch)

    def _next(self):
        if self.built_projects is None:
            return self.build_deps[0][0]
        built_len = len(self.built_projects)
        if built_len == len(self.projects):
            return
        built_list = self.built_projects_list
        build_deps_size = len(",".join(self.config.build_deps.keys()))
        if built_len < build_deps_size:
            for grp in self.build_deps:
                for prj in grp:
                    if prj not in built_list:
                        return prj
        else:
            for prj in self.projects_list:
                if prj not in built_list:
                    return prj

    @property
    def next(self):
        res = self._next()
        if res is not None:
            if res in self.failed_projects_list:
                logger.info("project: %s marked as failed, stop sending jobs")

    @property
    def failed_projects_list(self):
        projects = JenkinsBuildInfo.objects.release_projects(
            self.release, release_uuid=self.uuid, failed=True
        )
        if projects:
            return [x for x in projects]
        return []

    @property
    def build_deps(self):
        if getattr(self, "_build_deps", None) is None:
            self._build_deps = [
                list(self.config.wanna_build_deps(0)),
                list(self.config.wanna_build_deps(1)),
            ]
        return self._build_deps

    @property
    def config(self):
        if getattr(self, "_config", None) is None:
            self._config = ReleaseConfig(self.release)
        return self._config
