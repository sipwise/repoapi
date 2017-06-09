# Copyright (C) 2015 The Sipwise Team - http://sipwise.com

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
import logging
import re
from collections import OrderedDict

from django.db import models
from django.forms.models import model_to_dict
from django.conf import settings
from repoapi.tasks import get_jbi_files
from urlparse import urlparse

logger = logging.getLogger(__name__)
workfront_re = re.compile(r"TT#(\d+)")
commit_re = re.compile(r"^(\w{7}) ")


class JenkinsBuildInfoManager(models.Manager):

    def release_projects_full(self, release):
        res = dict()
        for project in self.release_projects(release):
            res[project] = dict()
            uuids = self.release_project_uuids(release, project)
            for uuid in uuids:
                res[project][uuid] = OrderedDict()
                jobs = self.jobs_by_uuid(release, project, uuid)
                for job in jobs:
                    key = str(job.date)
                    res[project][uuid][key] = model_to_dict(job)
                    # date is not editable... so not in the result
                    res[project][uuid][key]['date'] = job.date
            uuid = self.latest_uuid(release, project)
            if uuid:
                res[project][uuid['tag']]['latest'] = True
        return res

    def releases(self, flat=True):
        qs = self.get_queryset().filter(tag__isnull=False)
        res = qs.values('param_release').distinct()
        if res.exists():
            if flat:
                return res.values_list('param_release', flat=True)
            else:
                return res.values('param_release')

    def is_release(self, release):
        res = self.get_queryset().filter(
            param_release=release,
            tag__isnull=False)
        return res.exists()

    def release_projects(self, release, flat=True):
        res = self.get_queryset().filter(
            param_release=release,
            tag__isnull=False).values('projectname').distinct()
        if res.exists():
            if flat:
                return res.values_list('projectname', flat=True)
            else:
                return res.values('projectname')

    def is_project(self, release, project):
        res = self.get_queryset().filter(
            param_release=release,
            projectname=project,
            tag__isnull=False)
        return res.exists()

    def release_project_uuids_set(self, release, project):
        res = self.get_queryset().filter(
            param_release=release,
            projectname=project,
            tag__isnull=False).distinct()
        if res.exists():
            return res.order_by('projectname')

    def release_project_uuids(self, release, project, flat=True):
        res = self.get_queryset().filter(
            param_release=release,
            projectname=project,
            tag__isnull=False).distinct()
        if flat:
            return res.order_by('projectname').values_list('tag', flat=True)
        else:
            return res.order_by('projectname').values('tag')

    def is_uuid(self, release, project, uuid):
        res = self.get_queryset().filter(
            param_release=release,
            projectname=project,
            tag=uuid)
        return res.exists()

    def jobs_by_uuid(self, release, project, uuid):
        return self.get_queryset().filter(tag=uuid, param_release=release,
                                          projectname=project).order_by('date')

    def _latest_uuid(self, release, project):
        qs = self.get_queryset()
        res = qs.filter(
            param_release=release,
            projectname=project,
            tag__isnull=False)
        if res.exists():
            return res.latest('date')

    def latest_uuid(self, release, project):
        res = self._latest_uuid(release, project)
        if res is not None:
            return {'tag': res.tag, 'date': res.date}

    def latest_uuid_js(self, release, project):
        res = self._latest_uuid(release, project)
        if res is not None:
            return {'tag': res.tag, 'latest': True}

    def is_latest_uuid_js(self, release, project, uuid):
        res = self._latest_uuid(release, project)
        latest_uuid = {'tag': uuid, 'latest': False}
        if res is not None:
            latest_uuid['latest'] = (res.tag == uuid)
        return latest_uuid


class JenkinsBuildInfo(models.Model):
    tag = models.CharField(max_length=64, null=True)
    projectname = models.CharField(max_length=100)
    jobname = models.CharField(max_length=100)
    buildnumber = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    result = models.CharField(max_length=50)
    job_url = models.URLField()

    gerrit_patchset = models.CharField(max_length=50, null=True)
    gerrit_change = models.CharField(max_length=50, null=True)
    gerrit_eventtype = models.CharField(max_length=50, null=True)

    param_tag = models.CharField(max_length=50, null=True)
    param_branch = models.CharField(max_length=50, null=True)
    param_release = models.CharField(max_length=50, null=True,
                                     db_index=True)
    param_release_uuid = models.CharField(max_length=64, null=True)
    param_distribution = models.CharField(max_length=50, null=True)
    param_ppa = models.CharField(max_length=50, null=True)

    repo_name = models.CharField(max_length=50, null=True)
    git_commit_msg = models.TextField(null=True)

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
        return "[%s]%s:%d[%s]" % (self.param_release_uuid, self.jobname,
                                  self.buildnumber, self.tag)


def jbi_manage(sender, **kwargs):
    if kwargs["created"]:
        instance = kwargs["instance"]
        if instance.is_job_url_allowed():
            get_jbi_files.delay(instance.pk,
                                instance.jobname,
                                instance.buildnumber)
