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


class GerritRepoInfoTestCase(TestCase):

    def test_creation(self):
        jbi = JenkinsBuildInfo.objects.create(
            tag="edc90cd9-37f3-4613-9748-ed05a32031c2",
            projectname="kamailio",
            jobname="kamailio-repos",
            buildnumber=897,
            result="SUCCESS",
            job_url="https://jenkins.mgm.sipwise.com/job/kamailio-repos/",
            gerrit_patchset="1",
            gerrit_change="2054",
            gerrit_eventtype="patchset-created",
            param_tag="none",
            param_branch="master",
            param_release="none",
            param_distribution="wheezy",
            param_ppa="gerrit_MT10339_review2054")

        gri = GerritRepoInfo.objects.get(param_ppa="gerrit_MT10339_review2054")
        self.assertEquals(gri.count, 1)

    def test_creation_deletion(self):
        jbi = JenkinsBuildInfo.objects.create(
            tag="edc90cd9-37f3-4613-9748-ed05a32031c2",
            projectname="kamailio",
            jobname="kamailio-repos",
            buildnumber=897,
            result="SUCCESS",
            job_url="https://jenkins.mgm.sipwise.com/job/kamailio-repos/",
            gerrit_patchset="1",
            gerrit_change="2054",
            gerrit_eventtype="patchset-created",
            param_tag="none",
            param_branch="master",
            param_release="none",
            param_distribution="wheezy",
            param_ppa="gerrit_MT10339_review2054")

        gri = GerritRepoInfo.objects.get(
            param_ppa="gerrit_MT10339_review2054")
        self.assertEquals(gri.count, 1)

        jbi = JenkinsBuildInfo.objects.create(
            tag="edc90cd9-37f3-4613-9748-ed05a32031c2",
            projectname="kamailio",
            jobname="kamailio-repos",
            buildnumber=897,
            result="SUCCESS",
            job_url="https://jenkins.mgm.sipwise.com/job/kamailio-repos/",
            gerrit_patchset="1",
            gerrit_change="2054",
            gerrit_eventtype="change-merged",
            param_tag="none",
            param_branch="master",
            param_release="none",
            param_distribution="wheezy",
            param_ppa="gerrit_MT10339_review2054")

        gri = GerritRepoInfo.objects.filter(
            param_ppa="gerrit_MT10339_review2054")
        self.assertEquals(gri.count(), 0)

    def test_no_creation(self):
        jbi = JenkinsBuildInfo.objects.create(
            tag="edc90cd9-37f3-4613-9748-ed05a32031c2",
            projectname="kamailio",
            jobname="kamailio-get-code",
            buildnumber=897,
            result="SUCCESS",
            job_url="https://jenkins.mgm.sipwise.com/job/kamailio-repos/",
            gerrit_patchset="1",
            gerrit_change="2054",
            gerrit_eventtype="patchset-created",
            param_tag="none",
            param_branch="master",
            param_release="none",
            param_distribution="wheezy",
            param_ppa="gerrit_MT10339_review2054")

        gri = GerritRepoInfo.objects.filter(
            param_ppa="gerrit_MT10339_review2054")
        self.assertEquals(gri.count(), 0)
