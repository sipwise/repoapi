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

from django.db import models


class JenkinsBuildInfoManager(models.Manager):

    def releases(self, flat=True):
        res = self.get_queryset().values('param_release').distinct()
        if flat:
            return res.values_list('param_release', flat=True)
        else:
            return res.values('param_release')

    def release_uuids_by_project(self, release, project, flat=True):
        res = self.get_queryset().filter(
            param_release=release, projectname__startswith=project).distinct()
        if flat:
            return res.values_list('tag', flat=True)
        else:
            return res.values('tag')

    def projects_by_uuid(self, release, project, uuid, flat=True):
        res = self.get_queryset().filter(tag=uuid, param_release=release,
                                         projectname__startswith=project)
        if flat:
            return res.order_by('-date').values_list('projectname', flat=True)
        else:
            return res.order_by('-date').values('projectname')


class JenkinsBuildInfo(models.Model):
    tag = models.CharField(max_length=64, null=True)
    projectname = models.CharField(max_length=100)
    buildnumber = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    result = models.CharField(max_length=50)
    job_url = models.URLField()

    gerrit_patchset = models.CharField(max_length=50, null=True)
    gerrit_change = models.CharField(max_length=50, null=True)
    gerrit_eventtype = models.CharField(max_length=50, null=True)

    param_tag = models.CharField(max_length=50, null=True)
    param_branch = models.CharField(max_length=50, null=True)
    param_release = models.CharField(max_length=50, null=True)
    param_distribution = models.CharField(max_length=50, null=True)
    param_ppa = models.CharField(max_length=50, null=True)

    repo_name = models.CharField(max_length=50, null=True)

    objects = JenkinsBuildInfoManager()

    def __str__(self):
        return "%s:%d[%s]" % (self.projectname,
                              self.buildnumber, self.tag)
