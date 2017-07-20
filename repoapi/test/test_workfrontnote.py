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

from django.conf import settings
from repoapi.models import JenkinsBuildInfo, WorkfrontNoteInfo
from repoapi.test.base import BaseTest
from mock import patch


class WorkfrontNoteTestCase(BaseTest):

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
        self.assertCountEqual(res, "1234567")

    def get_defaults(self):
        defaults = {
            'tag': "edc90cd9-37f3-4613-9748-ed05a32031c2",
            'projectname': "kamailio",
            'jobname': "kamailio-gerrit",
            'buildnumber': 897,
            'result': "SUCCESS",
            'job_url': "https://jenkins.mgm.sipwise.com/job/kamailio-gerrit/",
            'gerrit_patchset': "1",
            'gerrit_change': "2054",
            'gerrit_eventtype': "patchset-created",
            'param_tag': "none",
            'param_branch': "master",
            'param_release': "none",
            'param_distribution': "wheezy",
            'param_ppa': "gerrit_MT10339_review2054",
            'git_commit_msg': "7fg4567 TT#0001 whatever",
        }
        return defaults

    def get_non_gerrit_defaults(self):
        defaults = self.get_defaults()
        del defaults['gerrit_patchset']
        del defaults['gerrit_change']
        del defaults['gerrit_eventtype']
        return defaults

    @patch('repoapi.utils.workfront_set_release_target')
    @patch('repoapi.utils.get_next_release')
    @patch('repoapi.utils.workfront_note_send')
    def test_note_gerrit(self, wns, gnr, wsrt):
        param = self.get_defaults()
        JenkinsBuildInfo.objects.create(**param)

        gri = WorkfrontNoteInfo.objects.filter(
            workfront_id="0001",
            gerrit_change="2054")
        self.assertCountEqual(gri.count(), 0)

        param['jobname'] = "kamailio-get-code"
        param['buildnumber'] = 897
        JenkinsBuildInfo.objects.create(**param)

        gri = WorkfrontNoteInfo.objects.filter(
            workfront_id="0001",
            gerrit_change="2054")
        self.assertCountEqual(gri.count(), 1)
        msg = "%s.git[%s] review created %s " % (
            param['projectname'],
            param['param_branch'],
            settings.GERRIT_URL.format("2054"))
        wsrt.assert_not_called()
        gnr.assert_not_called()
        wns.assert_called_once_with("0001", msg)

    @patch('repoapi.utils.workfront_set_release_target')
    @patch('repoapi.utils.get_next_release')
    @patch('repoapi.utils.workfront_note_send')
    def test_note_merge(self, wns, gnr, wsrt):
        param = self.get_defaults()
        JenkinsBuildInfo.objects.create(**param)

        gri = WorkfrontNoteInfo.objects.filter(
            workfront_id="0001",
            gerrit_change="2054")
        self.assertCountEqual(gri.count(), 0)

        param['jobname'] = "kamailio-get-code"
        param['buildnumber'] = 897
        JenkinsBuildInfo.objects.create(**param)

        gri = WorkfrontNoteInfo.objects.filter(
            workfront_id="0001",
            gerrit_change="2054",
            eventtype='patchset-created')
        self.assertCountEqual(gri.count(), 1)
        gri = WorkfrontNoteInfo.objects.filter(
            workfront_id="0001",
            gerrit_change="7fg4567")
        self.assertCountEqual(gri.count(), 0)
        msg = "%s.git[%s] review created %s " % (
            param['projectname'],
            param['param_branch'],
            settings.GERRIT_URL.format("2054"))
        wsrt.assert_not_called()
        gnr.assert_not_called()
        wns.assert_called_once_with("0001", msg)

        param['jobname'] = "kamailio-get-code"
        param['buildnumber'] = 898
        param['gerrit_eventtype'] = "change-merged"
        gnr.return_value = "mr5.5.1"
        JenkinsBuildInfo.objects.create(**param)

        gri = WorkfrontNoteInfo.objects.filter(
            workfront_id="0001",
            gerrit_change="2054",
            eventtype='change-merged')
        self.assertCountEqual(gri.count(), 1)
        gri = WorkfrontNoteInfo.objects.filter(
            workfront_id="0001",
            gerrit_change="2054")
        self.assertCountEqual(gri.count(), 2)
        msg = "%s.git[%s] review merged %s " % (
            param['projectname'],
            param['param_branch'],
            settings.GERRIT_URL.format("2054"))
        wsrt.assert_called_once_with("0001", "mr5.5.1")
        gnr.assert_called_once_with("master")
        wns.assert_called_with("0001", msg)

    @patch('repoapi.utils.workfront_set_release_target')
    @patch('repoapi.utils.get_next_release')
    @patch('repoapi.utils.workfront_note_send')
    def test_note_commit(self, wns, gnr, wsrt):
        param = self.get_non_gerrit_defaults()
        param['jobname'] = 'kamailio-get-code'
        gnr.return_value = "mr5.5.1"
        JenkinsBuildInfo.objects.create(**param)

        gri = WorkfrontNoteInfo.objects.filter(
            workfront_id="0001",
            gerrit_change="7fg4567")
        self.assertCountEqual(gri.count(), 1)

        param['jobname'] = "kamailio-binaries"
        param['buildnumber'] = 897
        JenkinsBuildInfo.objects.create(**param)

        gri = WorkfrontNoteInfo.objects.filter(
            workfront_id="0001",
            gerrit_change="7fg4567")
        self.assertCountEqual(gri.count(), 1)
        msg = "%s.git[%s] commit created %s " % (
            param['projectname'],
            param['param_branch'],
            settings.GITWEB_URL.format("kamailio", "7fg4567"))
        wsrt.assert_called_once_with("0001", "mr5.5.1")
        gnr.assert_called_once_with("master")
        wns.assert_called_once_with("0001", msg)

    @patch('repoapi.utils.workfront_set_release_target')
    @patch('repoapi.utils.get_next_release')
    @patch('repoapi.utils.workfront_note_send')
    def test_note_commit_mrXX(self, wns, gnr, wsrt):
        param = self.get_non_gerrit_defaults()
        param['jobname'] = 'kamailio-get-code'
        param['param_branch'] = 'mr5.5'
        param['param_release'] = 'release-mr5.5-update'
        gnr.return_value = "mr5.5.2"
        JenkinsBuildInfo.objects.create(**param)

        gri = WorkfrontNoteInfo.objects.filter(
            workfront_id="0001",
            gerrit_change="7fg4567")
        self.assertCountEqual(gri.count(), 1)

        param['jobname'] = "kamailio-binaries"
        param['buildnumber'] = 897
        JenkinsBuildInfo.objects.create(**param)

        gri = WorkfrontNoteInfo.objects.filter(
            workfront_id="0001",
            gerrit_change="7fg4567")
        self.assertCountEqual(gri.count(), 1)
        msg = "%s.git[%s] commit created %s " % (
            param['projectname'],
            param['param_branch'],
            settings.GITWEB_URL.format("kamailio", "7fg4567"))
        wsrt.assert_called_once_with("0001", "mr5.5.2")
        gnr.assert_called_once_with("mr5.5")
        wns.assert_called_once_with("0001", msg)

    @patch('repoapi.utils.workfront_set_release_target')
    @patch('repoapi.utils.get_next_release')
    @patch('repoapi.utils.workfront_note_send')
    def test_note_commit_mrXXX(self, wns, gnr, wsrt):
        param = self.get_non_gerrit_defaults()
        param['jobname'] = 'kamailio-get-code'
        param['param_branch'] = 'mr5.5.2'
        JenkinsBuildInfo.objects.create(**param)

        gri = WorkfrontNoteInfo.objects.filter(
            workfront_id="0001",
            gerrit_change="7fg4567")
        self.assertCountEqual(gri.count(), 1)

        param['jobname'] = "kamailio-binaries"
        param['buildnumber'] = 897
        JenkinsBuildInfo.objects.create(**param)

        gri = WorkfrontNoteInfo.objects.filter(
            workfront_id="0001",
            gerrit_change="7fg4567")
        self.assertCountEqual(gri.count(), 1)
        msg = "%s.git[%s] commit created %s " % (
            param['projectname'],
            param['param_branch'],
            settings.GITWEB_URL.format("kamailio", "7fg4567"))
        wsrt.assert_called_once_with("0001", "mr5.5.2")
        gnr.assert_not_called()
        wns.assert_called_once_with("0001", msg)

    @patch('repoapi.utils.workfront_set_release_target')
    @patch('repoapi.utils.get_next_release')
    @patch('repoapi.utils.workfront_note_send')
    def test_note_commit_next_distri(self, wns, gnr, wsrt):
        param = self.get_non_gerrit_defaults()
        param['jobname'] = 'kamailio-get-code'
        param['param_branch'] = 'stretch/master'
        param['param_distribution'] = 'stretch'
        gnr.return_value = ''
        JenkinsBuildInfo.objects.create(**param)

        gri = WorkfrontNoteInfo.objects.filter(
            workfront_id="0001",
            gerrit_change="7fg4567")
        self.assertCountEqual(gri.count(), 1)

        param['jobname'] = "kamailio-binaries"
        param['buildnumber'] = 897
        JenkinsBuildInfo.objects.create(**param)

        gri = WorkfrontNoteInfo.objects.filter(
            workfront_id="0001",
            gerrit_change="7fg4567")
        self.assertCountEqual(gri.count(), 1)
        msg = "%s.git[%s] commit created %s " % (
            param['projectname'],
            param['param_branch'],
            settings.GITWEB_URL.format("kamailio", "7fg4567"))
        gnr.assert_called_once_with("stretch/master")
        self.assertItemsEqual(wsrt.mock_calls, [])
        wsrt.assert_not_called()
        wns.assert_called_once_with("0001", msg)

    @patch('repoapi.utils.workfront_set_release_target')
    @patch('repoapi.utils.get_next_release')
    @patch('repoapi.utils.workfront_note_send')
    def test_note_commit_non_ngcp(self, wns, gnr, wsrt):
        param = self.get_non_gerrit_defaults()
        param['projectname'] = 'fake'
        param['jobname'] = 'fake-get-code'
        param['param_branch'] = 'mr5.5.2'
        JenkinsBuildInfo.objects.create(**param)

        gri = WorkfrontNoteInfo.objects.filter(
            workfront_id="0001",
            gerrit_change="7fg4567")
        self.assertCountEqual(gri.count(), 1)

        param['jobname'] = "fake-binaries"
        param['buildnumber'] = 897
        JenkinsBuildInfo.objects.create(**param)

        gri = WorkfrontNoteInfo.objects.filter(
            workfront_id="0001",
            gerrit_change="7fg4567")
        self.assertCountEqual(gri.count(), 1)
        msg = "%s.git[%s] commit created %s " % (
            param['projectname'],
            param['param_branch'],
            settings.GITWEB_URL.format("fake", "7fg4567"))
        wsrt.assert_not_called()
        gnr.assert_not_called()
        wns.assert_called_once_with("0001", msg)
