# Copyright (C) 2015-2024 The Sipwise Team - http://sipwise.com
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
import glob
import json
import re
from collections import OrderedDict
from datetime import datetime
from datetime import timedelta
from pathlib import Path
from urllib.parse import urlparse

import structlog
from django.db import models
from django.db.models import Q
from django.forms.models import model_to_dict

from ..conf import settings
from debian import deb822

logger = structlog.get_logger(__name__)
workfront_re = re.compile(r"TT#(\d+)")
commit_re = re.compile(r"^(\w{7}) ")


class JenkinsBuildInfoManager(models.Manager):
    def release_projects_full(self, release, release_uuid=None):
        res = dict()
        projects = self.release_projects(release, release_uuid=release_uuid)
        if projects is None:
            return res
        for project in projects:
            res[project] = dict()
            uuids = self.release_project_uuids(
                release, project, release_uuid=release_uuid
            )
            for uuid in uuids:
                res[project][uuid] = OrderedDict()
                jobs = self.jobs_by_uuid(release, project, uuid)
                for job in jobs:
                    key = str(job.date)
                    res[project][uuid][key] = model_to_dict(job)
                    # date is not editable... so not in the result
                    res[project][uuid][key]["date"] = job.date
            uuid = self.latest_uuid(
                release, project, release_uuid=release_uuid
            )
            if uuid:
                res[project][uuid["tag"]]["latest"] = True
        return res

    def releases(self, flat=True):
        qs = self.get_queryset().exclude(
            Q(param_release__contains="trunk")
            | Q(jobname__in=settings.BUILD_RELEASE_JOBS)
        )
        res = qs.filter(tag__isnull=False).values("param_release").distinct()
        if res.exists():
            if flat:
                return res.values_list("param_release", flat=True)
            else:
                return res.values("param_release")
        return []

    def is_release(self, release):
        res = self.get_queryset().filter(
            param_release=release, tag__isnull=False
        )
        return res.exists()

    def release_projects(
        self, release, flat=True, release_uuid=None, failed=None
    ):
        params = {
            "param_release": release,
            "tag__isnull": False,
        }
        exclude_params = {
            "jobname__in": settings.BUILD_RELEASE_JOBS,
        }
        if release_uuid:
            params["param_release_uuid"] = release_uuid
        if failed is not None:
            if failed:
                params["result"] = "FAILURE"
            else:
                params["result__in"] = ["SUCCESS", "UNSTABLE"]
        qs = self.get_queryset().filter(**params)
        if release_uuid:
            qs = qs.exclude(**exclude_params)
        res = qs.values("projectname").distinct()
        if res.exists():
            if flat:
                return res.values_list("projectname", flat=True)
            else:
                return res.values("projectname")

    def is_project(self, release, project, release_uuid=None):
        params = {
            "param_release": release,
            "projectname": project,
            "tag__isnull": False,
        }
        if release_uuid:
            params["param_release_uuid"] = release_uuid
        res = self.get_queryset().filter(**params)
        return res.exists()

    def release_project_uuids_set(self, release, project, release_uuid=None):
        params = {
            "param_release": release,
            "projectname": project,
            "tag__isnull": False,
        }
        if release_uuid:
            params["param_release_uuid"] = release_uuid
        res = self.get_queryset().filter(**params).distinct()
        if res.exists():
            return res.order_by("projectname")

    def release_project_uuids(
        self, release, project, flat=True, release_uuid=None
    ):
        params = {
            "param_release": release,
            "projectname": project,
            "tag__isnull": False,
        }
        if release_uuid:
            params["param_release_uuid"] = release_uuid
        res = self.get_queryset().filter(**params).distinct()
        if flat:
            return res.order_by("projectname").values_list("tag", flat=True)
        else:
            return res.order_by("projectname").values("tag")

    def is_uuid(self, release, project, uuid):
        res = self.get_queryset().filter(
            param_release=release, projectname=project, tag=uuid
        )
        return res.exists()

    def jobs_by_uuid(self, release, project, uuid, release_uuid=None):
        params = {
            "param_release": release,
            "projectname": project,
            "tag": uuid,
        }
        if release_uuid:
            params["param_release_uuid"] = release_uuid
        return self.get_queryset().filter(**params).order_by("date")

    def _latest_uuid(self, release, project, release_uuid=None):
        params = {
            "param_release": release,
            "projectname": project,
            "tag__isnull": False,
        }
        if release_uuid:
            params["param_release_uuid"] = release_uuid
        qs = self.get_queryset()
        res = qs.filter(**params)
        if res.exists():
            return res.latest("date")

    def latest_uuid(self, release, project, release_uuid=None):
        res = self._latest_uuid(release, project, release_uuid=release_uuid)
        if res is not None:
            return {"tag": res.tag, "date": res.date}

    def latest_uuid_js(self, release, project, release_uuid=None):
        res = self._latest_uuid(release, project, release_uuid=release_uuid)
        if res is not None:
            return {"tag": res.tag, "latest": True}

    def is_latest_uuid_js(self, release, project, uuid, release_uuid=None):
        res = self._latest_uuid(release, project, release_uuid=release_uuid)
        latest_uuid = {"tag": uuid, "latest": False}
        if res is not None:
            latest_uuid["latest"] = res.tag == uuid
        return latest_uuid

    def purge_release(self, release, _timedelta=timedelta(weeks=3)):
        _date = datetime.now() - _timedelta
        if release is None:
            self.get_queryset().filter(
                param_release__isnull=True, date__date__lt=_date
            ).delete()
        else:
            self.get_queryset().filter(
                param_release=release, date__date__lt=_date
            ).delete()

    def job_builds(self, jobname):
        res = (
            self.get_queryset()
            .filter(jobname=jobname)
            .values_list("buildnumber", flat=True)
            .order_by("buildnumber")
        )
        return res


class JenkinsBuildInfo(models.Model):
    tag = models.CharField(max_length=64, null=True)
    projectname = models.CharField(max_length=100)
    jobname = models.CharField(max_length=100)
    buildnumber = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    result = models.CharField(max_length=50)
    job_url = models.URLField()

    gerrit_patchset = models.CharField(max_length=50, null=True, blank=True)
    gerrit_change = models.CharField(max_length=50, null=True, blank=True)
    gerrit_eventtype = models.CharField(max_length=50, null=True, blank=True)

    param_tag = models.CharField(max_length=50, null=True, blank=True)
    param_branch = models.CharField(max_length=50, null=True, blank=True)
    param_release = models.CharField(max_length=50, null=True, db_index=True)
    param_release_uuid = models.CharField(max_length=64, null=True, blank=True)
    param_distribution = models.CharField(max_length=50, null=True, blank=True)
    param_ppa = models.CharField(max_length=50, null=True, blank=True)

    repo_name = models.CharField(max_length=50, null=True, blank=True)
    git_commit_msg = models.TextField(null=True, blank=True)

    objects = JenkinsBuildInfoManager()

    class Meta:
        index_together = [
            ["param_release", "projectname"],
            ["param_release", "projectname", "tag"],
            ["param_release_uuid", "tag"],
        ]

    def is_job_url_allowed(self):
        if self.job_url:
            parsed = urlparse(self.job_url)
            if parsed.netloc in settings.JBI_ALLOWED_HOSTS:
                return True
        return False

    def __str__(self):
        return "[%s]%s:%d[%s]" % (
            self.param_release_uuid,
            self.jobname,
            self.buildnumber,
            self.tag,
        )

    @property
    def has_ppa(self):
        return self.param_ppa not in ["$ppa", None]

    @property
    def build_path(self) -> Path:
        return settings.JBI_BASEDIR.joinpath(
            self.jobname, str(self.buildnumber)
        )

    @property
    def build_info(self):
        path = self.build_path.joinpath("build.json")
        try:
            with open(path, "r") as data_file:
                data = json.load(data_file)
            return data
        except FileNotFoundError:
            logger.warn("file not found", path=path)
            return None

    @property
    def artifacts(self):
        build_info = self.build_info
        if build_info is None:
            return []
        return [x["fileName"] for x in build_info["artifacts"]]

    @property
    def source(self):
        try:
            return getattr(self, "_source")
        except AttributeError:
            pass
        path = self.build_path.joinpath("artifact")
        dscs = glob.glob(str(path.joinpath("*.dsc")))
        if len(dscs) != 1:
            logger.error("more than one dsc file on artifact dir", path=path)
            return None
        with open(dscs[0]) as f:
            d = deb822.Dsc(f)
        self._source = d["Source"]
        return self._source
