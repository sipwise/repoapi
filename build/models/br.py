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

from build.utils import get_simple_release
from build.utils import ReleaseConfig
from repoapi.models import JenkinsBuildInfo

logger = logging.getLogger(__name__)


class BuildReleaseManager(models.Manager):
    _jbi = JenkinsBuildInfo.objects

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

    def jbi(self, release_uuid):
        qs = self._jbi.get_queryset()
        return qs.filter(param_release_uuid=release_uuid)

    def release_jobs(self, release_uuid, flat=True):
        qs = self._jbi.get_queryset()
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
        qs = self._jbi.get_queryset()
        params = {
            "param_release_uuid": release_uuid,
            "jobname": job,
            "tag__isnull": False,
        }
        res = qs.filter(**params).distinct()
        if res.exists():
            return res.order_by("-date")

    def releases_with_builds(self):
        qs = self.get_queryset()
        res = set()
        for br in qs.all():
            res.add(get_simple_release(br.release))
        return res


class BuildRelease(models.Model):
    uuid = models.CharField(max_length=64, unique=True, null=False)
    start_date = models.DateTimeField(auto_now_add=True)
    tag = models.CharField(max_length=50, null=True, blank=True)
    branch = models.CharField(max_length=50, null=False)
    release = models.CharField(max_length=50, null=False, db_index=True)
    distribution = models.CharField(max_length=50, null=False, editable=False)
    projects = models.TextField(null=False, editable=False)
    built_projects = models.TextField(null=True, editable=False)
    triggered_projects = models.TextField(null=True, editable=False)
    failed_projects = models.TextField(null=True, editable=False)
    pool_size = models.SmallIntegerField(default=0, editable=False)
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

    @property
    def failed_projects_list(self):
        if self.failed_projects is not None:
            return [x.strip() for x in self.failed_projects.split(",")]
        return []

    @property
    def triggered_projects_list(self):
        if self.triggered_projects is not None:
            return [x.strip() for x in self.triggered_projects.split(",")]
        return []

    def append_triggered(self, value):
        fields = ["pool_size", "triggered_projects"]
        if value in self.triggered_projects_list:
            return False
        if self.triggered_projects is None:
            self.triggered_projects = value
        else:
            self.triggered_projects += ",{}".format(value)
        self.pool_size += 1
        self.save(update_fields=fields)
        return True

    def _append_falied(self, value):
        fields = ["failed_projects"]
        if value in self.failed_projects_list:
            return False
        if self.failed_projects is None:
            self.failed_projects = value
        else:
            self.failed_projects += ",{}".format(value)
        if self.pool_size > 0:
            self.pool_size -= 1
            fields.append("pool_size")
        self.save(update_fields=fields)
        return True

    def _append_built(self, value):
        fields = ["built_projects"]
        if value in self.built_projects_list:
            return False
        if self.built_projects is None:
            self.built_projects = value
        else:
            self.built_projects += ",{}".format(value)
        failed_projects = self.failed_projects_list
        if value in failed_projects:
            fields.append("failed_projects")
            failed_projects.remove(value)
            fp = ",".join(failed_projects)
            if len(fp) > 0:
                self.failed_projects = fp
            else:
                self.failed_projects = None
        if self.pool_size > 0:
            self.pool_size -= 1
            fields.append("pool_size")
        self.save(update_fields=fields)
        return True

    def remove_triggered(self, jbi):
        value = jbi.projectname
        triggered_list = self.triggered_projects_list
        if value in triggered_list:
            triggered_list.remove(value)
            tl = ",".join(triggered_list)
            if len(tl) > 0:
                self.triggered_projects = tl
            else:
                self.triggered_projects = None
            self.save(update_fields=["triggered_projects"])

    def append_built(self, jbi):
        jobname = jbi.jobname
        self.remove_triggered(jbi)
        if jbi.result == "FAILURE":
            if jobname.endswith("-piuparts"):
                return False
            return self._append_falied(jbi.projectname)
        if jobname.endswith("-repos") or jobname in settings.RELEASE_JOBS:
            if jbi.result in ["SUCCESS", "UNSTABLE"]:
                return self._append_built(jbi.projectname)
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
        release_jobs_len = len(",".join(settings.RELEASE_JOBS))
        if built_len == release_jobs_len + 1 + len(self.projects):
            return
        t_list = self.triggered_projects_list
        built_list = self.built_projects_list
        for grp in self.build_deps:
            for prj in grp:
                if prj not in built_list and prj not in t_list:
                    return prj
        for prj in self.projects_list:
            if prj not in built_list and prj not in t_list:
                return prj

    @property
    def next(self):
        failed_projects = self.failed_projects_list
        if any(job in failed_projects for job in settings.RELEASE_JOBS):
            logger.info("release has failed release_jobs, stop sending jobs")
            return
        res = self._next()
        if res is not None:
            if res in failed_projects:
                logger.error(
                    "project: %s marked as failed, stop sending jobs", res
                )
            else:
                return res

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
