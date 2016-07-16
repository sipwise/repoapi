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
from repoapi.models import JenkinsBuildInfo, GerritRepoInfo
from mock import patch


class GerritRepoInfoTestCase(TestCase):

    def get_defaults(self):
        defaults = {
            'tag': "edc90cd9-37f3-4613-9748-ed05a32031c2",
            'projectname': "kamailio",
            'jobname': "kamailio-repos",
            'buildnumber': 897,
            'result': "SUCCESS",
            'job_url': "https://jenkins.mgm.sipwise.com/job/kamailio-repos/",
            'gerrit_patchset': "1",
            'gerrit_change': "2054",
            'gerrit_eventtype': "patchset-created",
            'param_tag': "none",
            'param_branch': "master",
            'param_release': "none",
            'param_distribution': "wheezy",
            'param_ppa': "gerrit_MT10339_review2054"
        }
        return defaults

    @patch('repoapi.utils.jenkins_remove_ppa')
    def test_creation(self, utils):
        JenkinsBuildInfo.objects.create(**self.get_defaults())
        gri = GerritRepoInfo.objects.filter(
            param_ppa="gerrit_MT10339_review2054")
        self.assertEquals(gri.count(), 1)
        utils.assert_not_called()

    @patch('repoapi.utils.jenkins_remove_ppa')
    def test_creation_deletion(self, utils):
        param = self.get_defaults()
        param['gerrit_eventtype'] = "change-merged"
        JenkinsBuildInfo.objects.create(**param)

        gri = GerritRepoInfo.objects.filter(
            param_ppa="gerrit_MT10339_review2054")
        self.assertEquals(gri.count(), 0)
        utils.assert_called_with("gerrit_MT10339_review2054")

    @patch('repoapi.utils.jenkins_remove_ppa')
    def test_no_creation(self, utils):
        param = self.get_defaults()
        param['jobname'] = "kamailio-get-code"
        JenkinsBuildInfo.objects.create(**param)

        gri = GerritRepoInfo.objects.filter(
            param_ppa="gerrit_MT10339_review2054")
        self.assertEquals(gri.count(), 0)
        utils.assert_not_called()

    @patch('repoapi.utils.jenkins_remove_ppa')
    def test_creation_review(self, utils):
        param = self.get_defaults()
        param['buildnumber'] = 898
        JenkinsBuildInfo.objects.create(**param)

        gri = GerritRepoInfo.objects.filter(
            param_ppa="gerrit_MT10339_review2054")
        self.assertEquals(gri.count(), 1)
        utils.assert_not_called()

    @patch('repoapi.utils.jenkins_remove_ppa')
    def test_creation_multi_review(self, utils):
        param = self.get_defaults()
        JenkinsBuildInfo.objects.create(**param)
        gri = GerritRepoInfo.objects.filter(
            param_ppa="gerrit_MT10339_review2054")
        self.assertEquals(gri.count(), 1)
        utils.assert_not_called()

        param['projectname'] = "fake"
        param['jobname'] = "fake-repos"
        param['buildnumber'] = 8
        param['gerrit_change'] = 2
        JenkinsBuildInfo.objects.create(**param)

        gri = GerritRepoInfo.objects.filter(
            param_ppa="gerrit_MT10339_review2054")
        self.assertEquals(gri.count(), 2)
        utils.assert_not_called()

    @patch('repoapi.utils.jenkins_remove_ppa')
    def test_creation_multi_review_no_del(self, utils):
        param = self.get_defaults()
        JenkinsBuildInfo.objects.create(**param)
        gri = GerritRepoInfo.objects.filter(
            param_ppa="gerrit_MT10339_review2054")
        self.assertEquals(gri.count(), 1)
        utils.assert_not_called()

        param_fake = self.get_defaults()
        param_fake['projectname'] = "fake"
        param_fake['jobname'] = "fake-repos"
        param_fake['buildnumber'] = 8
        param_fake['gerrit_change'] = 2
        JenkinsBuildInfo.objects.create(**param_fake)

        gri = GerritRepoInfo.objects.filter(
            param_ppa="gerrit_MT10339_review2054")
        self.assertEquals(gri.count(), 2)
        utils.assert_not_called()

        param['gerrit_eventtype'] = "change-merged"
        param['buildnumber'] = 898
        JenkinsBuildInfo.objects.create(**param)

        gri = GerritRepoInfo.objects.filter(
            param_ppa="gerrit_MT10339_review2054")
        self.assertEquals(gri.count(), 1)
        utils.assert_not_called()

    @patch('repoapi.utils.jenkins_remove_ppa')
    def test_creation_multi_review_del(self, utils):
        param = self.get_defaults()
        JenkinsBuildInfo.objects.create(**param)
        gri = GerritRepoInfo.objects.filter(
            param_ppa="gerrit_MT10339_review2054")
        self.assertEquals(gri.count(), 1)
        utils.assert_not_called()

        param_fake = self.get_defaults()
        param_fake['projectname'] = "fake"
        param_fake['jobname'] = "fake-repos"
        param_fake['buildnumber'] = 8
        param_fake['gerrit_change'] = 2
        JenkinsBuildInfo.objects.create(**param_fake)

        gri = GerritRepoInfo.objects.filter(
            param_ppa="gerrit_MT10339_review2054")
        self.assertEquals(gri.count(), 2)
        utils.assert_not_called()

        param['gerrit_eventtype'] = "change-merged"
        param['buildnumber'] = 898
        JenkinsBuildInfo.objects.create(**param)

        gri = GerritRepoInfo.objects.filter(
            param_ppa="gerrit_MT10339_review2054")
        self.assertEquals(gri.count(), 1)
        utils.assert_not_called()

        param_fake['buildnumber'] = 9
        param_fake['gerrit_eventtype'] = "change-merged"
        JenkinsBuildInfo.objects.create(**param_fake)

        gri = GerritRepoInfo.objects.filter(
            param_ppa="gerrit_MT10339_review2054")
        self.assertEquals(gri.count(), 0)
        utils.assert_called_with("gerrit_MT10339_review2054")

    @patch('repoapi.utils.jenkins_remove_ppa')
    def test_abandoned_review_del(self, utils):
        param = self.get_defaults()
        JenkinsBuildInfo.objects.create(**param)
        gri = GerritRepoInfo.objects.filter(
            param_ppa="gerrit_MT10339_review2054")
        self.assertEquals(gri.count(), 1)
        utils.assert_not_called()

        param['jobname'] = "kamailio-cleanup"
        param['gerrit_eventtype'] = "change-abandoned"
        param['buildnumber'] = 898
        JenkinsBuildInfo.objects.create(**param)

        gri = GerritRepoInfo.objects.filter(
            param_ppa="gerrit_MT10339_review2054")
        self.assertEquals(gri.count(), 0)
        utils.assert_called_with("gerrit_MT10339_review2054")
