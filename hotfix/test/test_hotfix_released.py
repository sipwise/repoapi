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

from django.test import override_settings
from mock import patch, call, mock_open
from hotfix import tasks, utils, models
from repoapi.models import JenkinsBuildInfo
from repoapi.test.base import BaseTest

debian_changelog = """ngcp-fake (3.8.7.4+0~mr3.8.7.4) unstable; urgency=medium

  [ Kirill Solomko ]
  * [ee3c706] MT#21499 add mysql replication options

  [ Victor Seva ]
  * [aabb345] TT#345 fake comment
  * [aabb123] MT#8989 TT#123 fake comment

  [ Sipwise Jenkins Builder ]

 -- whatever <jenkins@sipwise.com>  Fri, 22 Jul 2016 17:29:27 +0200
"""


@override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True)
class TestHotfixReleased(BaseTest):

    def get_defaults(self):
        defaults = {
            'tag': "edc90cd9-37f3-4613-9748-ed05a32031c2",
            'projectname': "fake",
            'jobname': "release-tools-runner",
            'buildnumber': 1,
            'result': "SUCCESS",
            'job_url': "https://jenkins.mgm.sipwise.com/job/real-fake-gerrit/",
            'param_tag': "none",
            'param_branch': "mr4.5",
            'param_release': "none",
            'param_distribution': "wheezy",
            'param_ppa': "gerrit_MT10339_review2054",
            'git_commit_msg': "7fg4567 TT#0001 whatever",
        }
        return defaults

    @patch('__builtin__.open', mock_open(read_data=debian_changelog))
    def test_parse_changelog(self):
        ids, changelog = utils.parse_changelog("/tmp/fake.txt")
        self.assertCountEqual(ids, ["345", "123"])
        self.assertEquals(changelog.full_version, "3.8.7.4+0~mr3.8.7.4")
        self.assertEquals(changelog.package, "ngcp-fake")

    def test_get_target_release(self):
        val = utils.get_target_release("3.8.7.4+0~mr3.8.7.4")
        self.assertEquals(val, "mr3.8.7.4")

    def test_get_target_release_ko(self):
        val = utils.get_target_release("3.8.7.4-1")
        self.assertIsNone(val)

    @patch('__builtin__.open', mock_open(read_data=debian_changelog))
    @patch('repoapi.utils.dlfile')
    @patch('repoapi.utils.workfront_set_release_target')
    @patch('repoapi.utils.workfront_note_send')
    def test_hotfixreleased(self, wns, wsrt, dlfile):
        param = self.get_defaults()
        jbi = JenkinsBuildInfo.objects.create(**param)
        tasks.hotfix_released.delay(jbi.pk, "/tmp/fake.txt")
        projectname = "fake"
        version = "3.8.7.4+0~mr3.8.7.4"
        gri = models.WorkfrontNoteInfo.objects.filter(
            projectname=projectname,
            version=version)
        self.assertEquals(gri.count(), 2)
        gri = models.WorkfrontNoteInfo.objects.filter(
            workfront_id="345",
            projectname=projectname,
            version=version)
        self.assertEquals(gri.count(), 1)
        msg = "hotfix %s.git %s triggered" % (projectname, version)
        calls = [call("345", msg), ]
        gri = models.WorkfrontNoteInfo.objects.filter(
            workfront_id="123",
            projectname=projectname,
            version=version)
        self.assertEquals(gri.count(), 1)
        msg = "hotfix %s.git %s triggered" % (projectname, version)
        calls.append(call("123", msg))
        wns.assert_has_calls(calls)
        wsrt.assert_has_calls(
            [call("345", "mr3.8.7.4"), call("123", "mr3.8.7.4")])
