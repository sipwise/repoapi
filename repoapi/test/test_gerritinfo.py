# Copyright (C) 2015-2020 The Sipwise Team - http://sipwise.com
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
from unittest.mock import patch

from repoapi.models import GerritRepoInfo
from repoapi.models import JenkinsBuildInfo
from repoapi.test.base import BaseTest


@patch("repoapi.models.gri.jenkins_remove_project")
@patch("repoapi.models.gri.jenkins_remove_ppa")
class GerritRepoInfoTestCase(BaseTest):
    def get_defaults(self):
        defaults = {
            "tag": "edc90cd9-37f3-4613-9748-ed05a32031c2",
            "projectname": "kamailio",
            "jobname": "kamailio-repos",
            "buildnumber": 897,
            "result": "SUCCESS",
            "job_url": "https://jenkins.mgm.sipwise.com/job/kamailio-repos/",
            "gerrit_patchset": "1",
            "gerrit_change": "2054",
            "gerrit_eventtype": "patchset-created",
            "param_tag": "none",
            "param_branch": "master",
            "param_release": "none",
            "param_distribution": "wheezy",
            "param_ppa": "gerrit_MT10339_review2054",
        }
        return defaults

    def test_creation(self, rppa, rp):
        JenkinsBuildInfo.objects.create(**self.get_defaults())
        gri = GerritRepoInfo.objects.filter(
            param_ppa="gerrit_MT10339_review2054"
        )
        self.assertEqual(gri.count(), 1)
        rppa.assert_not_called()

    def test_creation_deletion(self, rppa, rp):
        param = self.get_defaults()
        param["gerrit_eventtype"] = "change-merged"
        JenkinsBuildInfo.objects.create(**param)

        gri = GerritRepoInfo.objects.filter(
            param_ppa="gerrit_MT10339_review2054"
        )
        self.assertEqual(gri.count(), 0)
        rppa.assert_called_with("gerrit_MT10339_review2054")

    def test_no_creation(self, rppa, rp):
        param = self.get_defaults()
        param["jobname"] = "kamailio-get-code"
        JenkinsBuildInfo.objects.create(**param)

        gri = GerritRepoInfo.objects.filter(
            param_ppa="gerrit_MT10339_review2054"
        )
        self.assertEqual(gri.count(), 0)
        rppa.assert_not_called()

    def test_creation_review(self, rppa, rp):
        param = self.get_defaults()
        param["buildnumber"] = 898
        JenkinsBuildInfo.objects.create(**param)

        gri = GerritRepoInfo.objects.filter(
            param_ppa="gerrit_MT10339_review2054"
        )
        self.assertEqual(gri.count(), 1)
        rppa.assert_not_called()

    def test_creation_multi_review(self, rppa, rp):
        param = self.get_defaults()
        JenkinsBuildInfo.objects.create(**param)
        gri = GerritRepoInfo.objects.filter(
            param_ppa="gerrit_MT10339_review2054"
        )
        self.assertEqual(gri.count(), 1)
        rppa.assert_not_called()

        param["projectname"] = "fake"
        param["jobname"] = "fake-repos"
        param["buildnumber"] = 8
        param["gerrit_change"] = 2
        JenkinsBuildInfo.objects.create(**param)

        gri = GerritRepoInfo.objects.filter(
            param_ppa="gerrit_MT10339_review2054"
        )
        self.assertEqual(gri.count(), 2)
        rppa.assert_not_called()

    def test_creation_multi_review_no_del(self, rppa, rp):
        param = self.get_defaults()
        JenkinsBuildInfo.objects.create(**param)
        gri = GerritRepoInfo.objects.filter(
            param_ppa="gerrit_MT10339_review2054"
        )
        self.assertEqual(gri.count(), 1)
        rppa.assert_not_called()

        param_fake = self.get_defaults()
        param_fake["projectname"] = "fake"
        param_fake["jobname"] = "fake-repos"
        param_fake["buildnumber"] = 8
        param_fake["gerrit_change"] = 2
        JenkinsBuildInfo.objects.create(**param_fake)

        gri = GerritRepoInfo.objects.filter(
            param_ppa="gerrit_MT10339_review2054"
        )
        self.assertEqual(gri.count(), 2)
        rppa.assert_not_called()

        param["gerrit_eventtype"] = "change-merged"
        param["buildnumber"] = 898
        JenkinsBuildInfo.objects.create(**param)

        gri = GerritRepoInfo.objects.filter(
            param_ppa="gerrit_MT10339_review2054"
        )
        self.assertEqual(gri.count(), 1)
        rppa.assert_not_called()

    def test_creation_multi_review_del(self, rppa, rp):
        param = self.get_defaults()
        JenkinsBuildInfo.objects.create(**param)
        gri = GerritRepoInfo.objects.filter(
            param_ppa="gerrit_MT10339_review2054"
        )
        self.assertEqual(gri.count(), 1)
        rppa.assert_not_called()

        param_fake = self.get_defaults()
        param_fake["projectname"] = "fake"
        param_fake["jobname"] = "fake-repos"
        param_fake["buildnumber"] = 8
        param_fake["gerrit_change"] = 2
        JenkinsBuildInfo.objects.create(**param_fake)

        gri = GerritRepoInfo.objects.filter(
            param_ppa="gerrit_MT10339_review2054"
        )
        self.assertEqual(gri.count(), 2)
        rppa.assert_not_called()

        param["gerrit_eventtype"] = "change-merged"
        param["buildnumber"] = 898
        JenkinsBuildInfo.objects.create(**param)

        gri = GerritRepoInfo.objects.filter(
            param_ppa="gerrit_MT10339_review2054"
        )
        self.assertEqual(gri.count(), 1)
        rppa.assert_not_called()

        param_fake["buildnumber"] = 9
        param_fake["gerrit_eventtype"] = "change-merged"
        JenkinsBuildInfo.objects.create(**param_fake)

        gri = GerritRepoInfo.objects.filter(
            param_ppa="gerrit_MT10339_review2054"
        )
        self.assertEqual(gri.count(), 0)
        rppa.assert_called_with("gerrit_MT10339_review2054")

    def test_abandoned_review_del(self, rppa, rp):
        param = self.get_defaults()
        JenkinsBuildInfo.objects.create(**param)
        gri = GerritRepoInfo.objects.filter(
            param_ppa="gerrit_MT10339_review2054"
        )
        self.assertEqual(gri.count(), 1)
        rppa.assert_not_called()

        param["jobname"] = "kamailio-cleanup"
        param["gerrit_eventtype"] = "change-abandoned"
        param["buildnumber"] = 898
        JenkinsBuildInfo.objects.create(**param)

        gri = GerritRepoInfo.objects.filter(
            param_ppa="gerrit_MT10339_review2054"
        )
        self.assertEqual(gri.count(), 0)
        rppa.assert_called_with("gerrit_MT10339_review2054")

    def test_update_projectname(self, rppa, rp):
        GerritRepoInfo.objects.create(
            param_ppa="gerrit_MT10339_review2054",
            gerrit_change="2054",
            projectname="unknown",
        )
        param = self.get_defaults()
        JenkinsBuildInfo.objects.create(**param)
        gri = GerritRepoInfo.objects.filter(
            param_ppa="gerrit_MT10339_review2054",
            projectname=param["projectname"],
        )
        self.assertEqual(gri.count(), 1)
        rppa.assert_not_called()
        rp.assert_not_called()
