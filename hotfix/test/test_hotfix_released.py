# Copyright (C) 2015-2022 The Sipwise Team - http://sipwise.com
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
from unittest.mock import call
from unittest.mock import mock_open
from unittest.mock import patch

from django.test import override_settings

from hotfix import models
from hotfix import utils
from hotfix.conf import Tracker
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


class TestHotfixReleased(BaseTest):
    def get_defaults(self):
        defaults = {
            "tag": "edc90cd9-37f3-4613-9748-ed05a32031c2",
            "projectname": "fake",
            "jobname": "release-tools-runner",
            "buildnumber": 1,
            "result": "SUCCESS",
            "job_url": "https://jenkins.mgm.sipwise.com/job/real-fake-gerrit/",
            "param_tag": "none",
            "param_branch": "mr4.5",
            "param_release": "none",
            "param_distribution": "wheezy",
            "param_ppa": "gerrit_MT10339_review2054",
            "git_commit_msg": "7fg4567 TT#0001 whatever",
        }
        return defaults

    @override_settings(REPOAPI_TRACKER=Tracker.WORKFRONT)
    @patch("builtins.open", mock_open(read_data=debian_changelog))
    @patch("repoapi.utils.dlfile")
    @patch("repoapi.utils.workfront_set_release_target")
    @patch("repoapi.utils.workfront_note_send")
    def test_hotfixreleased_wf(self, wns, wsrt, dlfile):
        param = self.get_defaults()
        jbi = JenkinsBuildInfo.objects.create(**param)
        utils.process_hotfix(str(jbi), jbi.projectname, "/tmp/fake.txt")
        projectname = "fake"
        version = "3.8.7.4+0~mr3.8.7.4"
        gri = models.WorkfrontNoteInfo.objects.filter(
            projectname=projectname, version=version
        )
        self.assertEqual(gri.count(), 2)
        gri = models.WorkfrontNoteInfo.objects.filter(
            workfront_id="345", projectname=projectname, version=version
        )
        self.assertEqual(gri.count(), 1)
        msg = "hotfix %s.git %s triggered" % (projectname, version)
        calls = [
            call("345", msg),
        ]
        gri = models.WorkfrontNoteInfo.objects.filter(
            workfront_id="123", projectname=projectname, version=version
        )
        self.assertEqual(gri.count(), 1)
        msg = "hotfix %s.git %s triggered" % (projectname, version)
        calls.append(call("123", msg))
        wns.assert_has_calls(calls, any_order=True)
        wsrt.assert_has_calls(
            [call("345", "mr3.8.7.4"), call("123", "mr3.8.7.4")],
            any_order=True,
        )

    @override_settings(REPOAPI_TRACKER=Tracker.MANTIS)
    @patch("builtins.open", mock_open(read_data=debian_changelog))
    @patch("repoapi.utils.dlfile")
    @patch("repoapi.utils.mantis_set_release_target")
    @patch("repoapi.utils.mantis_note_send")
    def test_hotfixreleased_mantis(self, mns, msrt, dlfile):
        param = self.get_defaults()
        jbi = JenkinsBuildInfo.objects.create(**param)
        utils.process_hotfix(str(jbi), jbi.projectname, "/tmp/fake.txt")
        projectname = "fake"
        version = "3.8.7.4+0~mr3.8.7.4"
        gri = models.MantisNoteInfo.objects.filter(
            projectname=projectname, version=version
        )
        self.assertEqual(gri.count(), 2)
        gri = models.MantisNoteInfo.objects.filter(
            mantis_id="8989", projectname=projectname, version=version
        )
        self.assertEqual(gri.count(), 1)
        msg = "hotfix %s.git %s triggered" % (projectname, version)
        calls = [
            call("8989", msg),
        ]
        gri = models.MantisNoteInfo.objects.filter(
            mantis_id="21499", projectname=projectname, version=version
        )
        self.assertEqual(gri.count(), 1)
        msg = "hotfix %s.git %s triggered" % (projectname, version)
        calls.append(call("21499", msg))
        mns.assert_has_calls(calls, any_order=True)
        msrt.assert_has_calls(
            [call("8989", "mr3.8.7.4"), call("21499", "mr3.8.7.4")],
            any_order=True,
        )

    @override_settings(REPOAPI_TRACKER=Tracker.MANTIS)
    @patch("builtins.open", mock_open(read_data=debian_changelog))
    @patch("repoapi.utils.dlfile")
    @patch("repoapi.utils.mantis_set_release_target")
    @patch("repoapi.utils.mantis_note_send")
    def test_hotfixreleased_mantis_versions(self, mns, msrt, dlfile):
        param = self.get_defaults()
        jbi = JenkinsBuildInfo.objects.create(**param)
        projectname = "fake"
        version = "3.8.7.4+0~mr3.8.7.4"
        other_version = "5.8.7.4+0~mr5.8.7.4"
        gri = models.MantisNoteInfo.objects.create(
            mantis_id="8989", projectname=projectname, version=other_version
        )
        utils.process_hotfix(str(jbi), jbi.projectname, "/tmp/fake.txt")
        gri = models.MantisNoteInfo.objects.filter(
            mantis_id="8989", projectname=projectname
        )
        self.assertEqual(gri.count(), 2)
        msg = "hotfix %s.git %s triggered" % (projectname, version)
        calls = [
            call("8989", msg),
        ]
        gri = models.MantisNoteInfo.objects.filter(
            mantis_id="21499", projectname=projectname, version=version
        )
        self.assertEqual(gri.count(), 1)
        msg = "hotfix %s.git %s triggered" % (projectname, version)
        calls.append(call("21499", msg))
        mns.assert_has_calls(calls, any_order=True)
        msrt.assert_has_calls(
            [
                call("8989", "mr3.8.7.4,mr5.8.7.4"),
                call("21499", "mr3.8.7.4"),
            ],
            any_order=True,
        )
