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

    def releases(self):
        res = self.get_queryset().values('tag').distinct()
        return res.values_list('tag', flat=True)

    def projects(self, release):
        res = self.get_queryset().filter(tag=release).distinct()
        return res


class JenkinsBuildInfo(models.Model):
    tag = models.CharField(max_length=32, null=True)
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

    def save(self, *args, **kwargs):
        """ use release parameter if no tag is set """
        if self.param_release and self.tag is None:
            self.tag = self.param_release
        super(JenkinsBuildInfo, self).save(*args, **kwargs)

    def __str__(self):
        return "%s:%d[%s]" % (self.projectname,
                              self.buildnumber, self.tag)
