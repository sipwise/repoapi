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

from django.test import TestCase
from repoapi.models import JenkinsBuildInfo
from django.test import override_settings
from repoapi.test.base import BaseTest
from mock import patch

JBI_HOST = "https://%s/job/fake-gerrit/"


class JenkinsBuildInfoTestCase(BaseTest):

    def test_creation_no_tag(self):
        jbi = JenkinsBuildInfo.objects.create(
            projectname='fake',
            jobname='fake-get-code',
            buildnumber=1,
            result='OK')
        self.assertIsNone(jbi.tag)

    def test_empty_tag_with_release(self):
        jbi = JenkinsBuildInfo.objects.create(
            projectname='fake',
            jobname='fake-get-code',
            buildnumber=1,
            result='OK',
            param_release='release-mr4.0')
        self.assertIsNone(jbi.tag)

    @override_settings(JBI_ALLOWED_HOSTS=['jenkins-dev.local'])
    def test_job_url_not_allowed(self):
        base = "https://%s/job/fake-gerrit/"
        job = JenkinsBuildInfo.objects.create(
            projectname='fake',
            jobname='fake-get-code',
            buildnumber=1,
            result='OK',
            param_release='release-mr4.0')
        self.assertFalse(job.is_job_url_allowed())
        job.job_url = JBI_HOST % 'jenkins.mgm.sipwise.com'
        self.assertFalse(job.is_job_url_allowed())

    @override_settings(JBI_ALLOWED_HOSTS=[])
    def test_job_url_not_allowed_empty(self):
        base = "https://%s/job/fake-gerrit/"
        job = JenkinsBuildInfo.objects.create(
            projectname='fake',
            jobname='fake-get-code',
            buildnumber=1,
            result='OK',
            param_release='release-mr4.0')
        self.assertFalse(job.is_job_url_allowed())
        job.job_url = JBI_HOST % 'jenkins.mgm.sipwise.com'
        self.assertFalse(job.is_job_url_allowed())
        job.job_url = None
        self.assertFalse(job.is_job_url_allowed())

    @override_settings(JBI_ALLOWED_HOSTS=['jenkins-dev.local',
                                          'jenkins.local'])
    def test_job_url_allowed(self):
        job = JenkinsBuildInfo.objects.create(
            projectname='fake',
            jobname='fake-get-code',
            buildnumber=1,
            result='OK',
            param_release='release-mr4.0')
        job.job_url = JBI_HOST % 'jenkins-dev.local'
        self.assertTrue(job.is_job_url_allowed())
        job.job_url = JBI_HOST % 'jenkins.local'
        self.assertTrue(job.is_job_url_allowed())
