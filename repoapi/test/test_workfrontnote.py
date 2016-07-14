# Copyright (C) 2016 The Sipwise Team - http://sipwise.com

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
from repoapi.models import JenkinsBuildInfo, WorkfrontNoteInfo
from mock import patch


class WorkfrontNoteTestCase(TestCase):

    def test_getID(self):
        res = WorkfrontNoteInfo.getIds("jojo TT#0891 whatever")
        self.assertItemsEqual(res, ['0891'])

    def test_getID_multiple(self):
        res = WorkfrontNoteInfo.getIds("jojo TT#0891 whatever TT#0001")
        self.assertItemsEqual(res, ['0891', '0001'])

    def test_getID_multiple_duplicate(self):
        res = WorkfrontNoteInfo.getIds("jojo TT#0891 whatever TT#0001 TT#0891")
        self.assertItemsEqual(res, ['0891', '0001'])

    def test_getCommit(self):
        res = WorkfrontNoteInfo.getCommit("1234567 TT#67676 whatever")
        self.assertEquals(res, "1234567")

    @patch('repoapi.utils.workfront_note_send')
    def test_note_gerrit(self, utils):
        JenkinsBuildInfo.objects.create(
            tag="edc90cd9-37f3-4613-9748-ed05a32031c2",
            projectname="kamailio",
            jobname="kamailio-gerrit",
            buildnumber=897,
            result="SUCCESS",
            job_url="https://jenkins.mgm.sipwise.com/job/kamailio-gerrit/",
            gerrit_patchset="1",
            gerrit_change="2054",
            gerrit_eventtype="patchset-created",
            param_tag="none",
            param_branch="master",
            param_release="none",
            param_distribution="wheezy",
            param_ppa="gerrit_MT10339_review2054",
            git_commit_msg="7fg4567 TT#0001 whatever")

        gri = WorkfrontNoteInfo.objects.filter(
            workfront_id="0001",
            gerrit_change="2054")
        self.assertEquals(gri.count(), 1)

        JenkinsBuildInfo.objects.create(
            tag="edc90cd9-37f3-4613-9748-ed05a32031c2",
            projectname="kamailio",
            jobname="kamailio-get-code",
            buildnumber=897,
            result="SUCCESS",
            job_url="https://jenkins.mgm.sipwise.com/job/kamailio-get-code/",
            gerrit_patchset="1",
            gerrit_change="2054",
            gerrit_eventtype="patchset-created",
            param_tag="none",
            param_branch="master",
            param_release="none",
            param_distribution="wheezy",
            param_ppa="gerrit_MT10339_review2054",
            git_commit_msg="7fg4567 TT#0001 whatever")

        gri = WorkfrontNoteInfo.objects.filter(
            workfront_id="0001",
            gerrit_change="2054")
        self.assertEquals(gri.count(), 1)
        utils.assert_called_once_with("0001", "review created")

    @patch('repoapi.utils.workfront_note_send')
    def test_note_merge(self, utils):
        JenkinsBuildInfo.objects.create(
            tag="edc90cd9-37f3-4613-9748-ed05a32031c2",
            projectname="kamailio",
            jobname="kamailio-gerrit",
            buildnumber=897,
            result="SUCCESS",
            job_url="https://jenkins.mgm.sipwise.com/job/kamailio-gerrit/",
            gerrit_patchset="1",
            gerrit_change="2054",
            gerrit_eventtype="change-merged",
            param_tag="none",
            param_branch="master",
            param_release="none",
            param_distribution="wheezy",
            param_ppa="gerrit_MT10339_review2054",
            git_commit_msg="7fg456 TT#0001 whatever")

        gri = WorkfrontNoteInfo.objects.filter(
            workfront_id="0001",
            gerrit_change="2054")
        self.assertEquals(gri.count(), 1)

        JenkinsBuildInfo.objects.create(
            tag="edc90cd9-37f3-4613-9748-ed05a32031c2",
            projectname="kamailio",
            jobname="kamailio-get-code",
            buildnumber=897,
            result="SUCCESS",
            job_url="https://jenkins.mgm.sipwise.com/job/kamailio-get-code/",
            gerrit_patchset="1",
            gerrit_change="2054",
            gerrit_eventtype="change-merged",
            param_tag="none",
            param_branch="master",
            param_release="none",
            param_distribution="wheezy",
            param_ppa="gerrit_MT10339_review2054",
            git_commit_msg="7fg456 TT#0001 whatever")

        gri = WorkfrontNoteInfo.objects.filter(
            workfront_id="0001",
            gerrit_change="2054")
        self.assertEquals(gri.count(), 1)
        utils.assert_called_once_with("0001", "review merged")

    @patch('repoapi.utils.workfront_note_send')
    def test_note_commit(self, utils):
        JenkinsBuildInfo.objects.create(
            tag="edc90cd9-37f3-4613-9748-ed05a32031c2",
            projectname="kamailio",
            jobname="kamailio-get-code",
            buildnumber=897,
            result="SUCCESS",
            job_url="https://jenkins.mgm.sipwise.com/job/kamailio-get-code/",
            param_tag="none",
            param_branch="master",
            param_release="none",
            param_distribution="wheezy",
            git_commit_msg="7fg4567 TT#0001 whatever")

        gri = WorkfrontNoteInfo.objects.filter(
            workfront_id="0001",
            gerrit_change="7fg4567")
        self.assertEquals(gri.count(), 1)

        JenkinsBuildInfo.objects.create(
            tag="edc90cd9-37f3-4613-9748-ed05a32031c2",
            projectname="kamailio",
            jobname="kamailio-binaries",
            buildnumber=897,
            result="SUCCESS",
            job_url="https://jenkins.mgm.sipwise.com/job/kamailio-binaries/",
            param_tag="none",
            param_branch="master",
            param_release="none",
            param_distribution="wheezy",
            git_commit_msg="7fg4567 TT#0001 whatever")

        gri = WorkfrontNoteInfo.objects.filter(
            workfront_id="0001",
            gerrit_change="7fg4567")
        self.assertEquals(gri.count(), 1)
        utils.assert_called_once_with("0001", "commit created")
