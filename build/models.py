# Copyright (C) 2017-2022 The Sipwise Team - http://sipwise.com
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
import datetime
import re

import structlog
from django.db import models
from django.db.models import Q
from django.forms.models import model_to_dict
from django.utils import timezone

from .conf import settings
from .exceptions import BuildReleaseUnique
from .exceptions import PreviousBuildNotDone
from .utils import get_simple_release
from .utils import ReleaseConfig
from .utils import remove_from_textlist
from repoapi.models import JenkinsBuildInfo

logger = structlog.get_logger(__name__)

regex_mrXXX = re.compile(r"^mr[0-9]+\.[0-9]+\.[0-9]+$")
regex_mrXX = re.compile(r"^mr[0-9]+\.[0-9]+$")
regex_mrXX_up = re.compile(r"^release-mr[0-9]+\.[0-9]+-update$")

build_release_jobs = ",".join(settings.BUILD_RELEASE_JOBS)
release_jobs_len = len(build_release_jobs) + 1


class BuildReleaseManager(models.Manager):
    _jbi = JenkinsBuildInfo.objects

    def release(self, version, distribution):
        qs = self.get_queryset()
        return qs.filter(
            Q(release=version, distribution=distribution)
            | Q(release="{}-update".format(version), distribution=distribution)
        )

    def create_build_release(self, uuid, release, fake=False):
        log = logger.bind(uuid=str(uuid), release=release, fake=fake)
        config = ReleaseConfig(release)
        qs = self.get_queryset()
        br = qs.filter(
            release=config.release, distribution=config.debian_release
        )
        release_ok = config.release
        if br.exists():
            if regex_mrXXX.match(config.branch):
                msg = "release[mrX.Y.Z]:{} has already a build"
                raise BuildReleaseUnique(msg.format(release))
            elif regex_mrXX.match(config.branch):
                release_ok = "{}-update".format(config.release)
                msg = (
                    "release[mrX.Y]:{} has already a build, "
                    "set {} as release"
                )
                log.info(msg.format(config.branch, release_ok))
            if not br.last().done:
                msg = f"release:{release} is already building"
                log.info(msg)
                raise PreviousBuildNotDone(msg)
        projects = ",".join(config.projects)
        if fake:
            start_date = timezone.make_aware(datetime.datetime(1977, 1, 1))
            built_projects = ",".join(
                list(settings.BUILD_RELEASE_JOBS) + config.projects
            )
        else:
            start_date = timezone.now()
            built_projects = None
        return self.create(
            start_date=start_date,
            uuid=uuid,
            tag=config.tag,
            branch=config.branch,
            release=release_ok,
            distribution=config.debian_release,
            projects=projects,
            built_projects=built_projects,
        )

    def jbi(self, release_uuid):
        qs = self._jbi.get_queryset()
        return qs.filter(param_release_uuid=release_uuid)

    def release_jobs(self, release_uuid, flat=True):
        qs = self._jbi.get_queryset()
        res = qs.filter(
            jobname__in=settings.BUILD_RELEASE_JOBS,
            param_release_uuid=release_uuid,
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
    start_date = models.DateTimeField(
        blank=True, editable=False, default=timezone.now
    )
    tag = models.CharField(max_length=50, null=True, blank=True)
    branch = models.CharField(max_length=50, null=False)
    release = models.CharField(max_length=50, null=False, db_index=True)
    distribution = models.CharField(max_length=50, null=False, editable=False)
    projects = models.TextField(null=False, editable=False)
    built_projects = models.TextField(null=True, editable=False)
    triggered_projects = models.TextField(null=True, editable=False)
    failed_projects = models.TextField(null=True, editable=False)
    pool_size = models.SmallIntegerField(default=0, editable=False)
    triggered_jobs = models.TextField(null=True, editable=False)
    objects = BuildReleaseManager()

    class Meta:
        permissions = [
            ("can_trigger", "can trigger build releases"),
            ("can_trigger_hotfix", "can trigger hotfix builds"),
        ]

    def __str__(self):
        return "%s[%s]" % (self.release, self.uuid)

    def refresh_projects(self):
        old_projects = set(self.projects_list)
        self.projects = ",".join(self.config.projects)
        new_list = set(self.projects_list)
        append_list = [item for item in new_list if item not in old_projects]
        removed_list = [item for item in old_projects if item not in new_list]
        for project in removed_list:
            remove_from_textlist(self, "built_projects", project)
            remove_from_textlist(self, "triggered_projects", project)
            remove_from_textlist(self, "failed_projects", project)
        JenkinsBuildInfo.objects.filter(
            projectname__in=removed_list,
            param_release_uuid=self.uuid,
        ).delete()
        self.save()
        return (append_list, removed_list)

    def resume(self):
        if not self.done:
            from .tasks import build_resume

            build_resume.delay(self.id)

    @property
    def last_update(self):
        job = BuildRelease.objects.jbi(self.uuid).order_by("-date").first()
        if job:
            return job.date

    @property
    def is_update(self):
        return regex_mrXX_up.match(self.release) is not None

    @property
    def done(self):
        if self.built_projects is None:
            return False
        built_len = len(self.built_projects)
        if self.is_update:
            return built_len == len(self.projects)
        else:
            return built_len == release_jobs_len + len(self.projects)

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

    @property
    def triggered_jobs_list(self):
        if self.triggered_jobs is not None:
            return [x.strip() for x in self.triggered_jobs.split(",")]
        return []

    def append_triggered_job(self, value):
        if value in self.triggered_jobs_list:
            return False
        if self.triggered_jobs is None:
            self.triggered_jobs = value
        else:
            self.triggered_jobs += ",{}".format(value)
        self.save()
        return True

    def append_triggered(self, value):
        if value in self.triggered_projects_list:
            return False
        if self.triggered_projects is None:
            self.triggered_projects = value
        else:
            self.triggered_projects += ",{}".format(value)
        self.pool_size += 1
        self.save()
        return True

    def _append_falied(self, value):
        if value in self.failed_projects_list:
            return False
        if self.failed_projects is None:
            self.failed_projects = value
        else:
            self.failed_projects += ",{}".format(value)
        if self.pool_size > 0:
            self.pool_size -= 1
        self.save()
        return True

    def _append_built(self, value):
        if value in self.built_projects_list:
            return False
        if self.built_projects is None:
            self.built_projects = value
        else:
            self.built_projects += ",{}".format(value)
        failed_projects = self.failed_projects_list
        if value in failed_projects:
            failed_projects.remove(value)
            fp = ",".join(failed_projects)
            if len(fp) > 0:
                self.failed_projects = fp
            else:
                self.failed_projects = None
        if self.pool_size > 0:
            self.pool_size -= 1
        self.save()
        return True

    def remove_triggered(self, jbi):
        remove_from_textlist(self, "triggered_projects", jbi.projectname)

    def append_built(self, jbi):
        jobname = jbi.jobname
        if jbi.result == "FAILURE":
            if jobname.endswith("-piuparts"):
                return False
            return self._append_falied(jbi.projectname)
        is_repos = jobname.endswith("-repos")
        is_rj = jobname in settings.BUILD_RELEASE_JOBS
        if is_repos or is_rj:
            if jbi.result in ["SUCCESS", "UNSTABLE"]:
                return self._append_built(jbi.projectname)
        return False

    @property
    def branch_or_tag(self):
        if self.tag:
            return "tag/{}".format(self.tag)
        return "branch/{}".format(self.branch)

    def _next(self):
        log = logger.bind(release=self)
        if self.built_projects is None:
            return self.build_deps[0][0]
        if self.done:
            return
        t_list = self.triggered_projects_list
        built_list = self.built_projects_list
        deps_missing = []
        for grp in self.build_deps:
            for prj in grp:
                if prj not in built_list:
                    if prj not in t_list:
                        return prj
                    else:
                        deps_missing.append(prj)
            else:
                if len(deps_missing) > 0:
                    log.info(
                        "release has build_deps missing",
                        deps_missing=deps_missing,
                    )
                    return None
        for prj in self.projects_list:
            if prj not in built_list and prj not in t_list:
                return prj

    @property
    def next(self):
        failed_projects = self.failed_projects_list
        log = logger.bind(release=self)
        if any(job in failed_projects for job in settings.BUILD_RELEASE_JOBS):
            log.info(
                "release has failed release_jobs, stop sending jobs",
                failed_projects=failed_projects,
            )
            return
        res = self._next()
        if res is not None:
            if res in failed_projects:
                log.error(
                    "project marked as failed, stop sending jobs",
                    project=res,
                )
            else:
                return res

    @property
    def build_deps(self) -> list:
        return self.config.levels_build_deps

    @property
    def config(self):
        if getattr(self, "_config", None) is None:
            self._config = ReleaseConfig(
                self.release, distribution=self.distribution
            )
        return self._config
