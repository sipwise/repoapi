# Copyright (C) 2020 The Sipwise Team - http://sipwise.com
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
from io import StringIO
from unittest.mock import call
from unittest.mock import patch

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from .test_utils import FakeResponse
from .test_utils import FakeResponseFile
from .test_utils import set_target_release_value
from tracker import utils
from tracker.conf import MapperType
from tracker.exceptions import IssueNotFound
from tracker.models import TrackerMapper

FIXTURES_PATH = settings.BASE_DIR.joinpath("tracker", "fixtures")
DB_FILE = FIXTURES_PATH.joinpath("mapper.db")
MANTIS_ISSUE_JSON = FIXTURES_PATH.joinpath("mantis_issue.json")
MANTIS_ISSUE_ID = 36018
ISSUE_URL = "https://support.local/api/rest/issues/36018"


class mapperImportTest(TestCase):
    fixtures = ["test_models"]

    def test_ok(self):
        out = StringIO()
        call_command("mapper_import", DB_FILE, stdout=out)
        self.assertIn("('new', 20)", out.getvalue())
        self.assertIn("('error', 0)", out.getvalue())
        qs = TrackerMapper.objects
        val = qs.filter(mapper_type=MapperType.ISSUE).count()
        self.assertEqual(val, 10)
        val = qs.filter(mapper_type=MapperType.TASK).count()
        self.assertEqual(val, 10)


class mantisTest(TestCase):
    def setUp(self):
        self.out = StringIO()

    def test_get_issue_ko(self):
        with self.assertRaises(CommandError):
            call_command("mantis", stdout=self.out)

    @patch(
        "tracker.utils.mantis_query",
        return_value=FakeResponseFile(MANTIS_ISSUE_JSON),
    )
    def test_get_issue_wrong_id(self, mq):
        wrong_id = 36017
        with self.assertRaises(IssueNotFound):
            call_command(
                "mantis", "get-issue", "--mantis-id", wrong_id, stdout=self.out
            )
        calls = [
            call("GET", f"https://support.local/api/rest/issues/{wrong_id}")
        ]
        mq.assert_has_calls(calls)

    @patch(
        "tracker.utils.mantis_query",
        return_value=FakeResponseFile(MANTIS_ISSUE_JSON),
    )
    def test_get_issue(self, mq):
        call_command(
            "mantis",
            "get-issue",
            "--mantis-id",
            MANTIS_ISSUE_ID,
            stdout=self.out,
        )
        calls = [
            call(
                "GET",
                ISSUE_URL,
            )
        ]
        mq.assert_has_calls(calls)

    @patch("tracker.utils.mantis_query")
    def test_get_target_release(self, mq):
        fake_issue_patched = utils.mantis_get_issue_id(
            FakeResponseFile(MANTIS_ISSUE_JSON).json(), MANTIS_ISSUE_ID
        )
        fake_issues = {"issues": [fake_issue_patched]}
        set_target_release_value(fake_issue_patched, "mr10.1,mr10.1.1")
        mq.configure_mock(return_value=FakeResponse(fake_issues))
        call_command(
            "mantis",
            "get-target-release",
            "--mantis-id",
            MANTIS_ISSUE_ID,
            stdout=self.out,
        )
        calls = [
            call(
                "GET",
                ISSUE_URL,
            )
        ]
        mq.assert_has_calls(calls)
        mq.assert_called_once_with("GET", ISSUE_URL)
        self.assertRegex(self.out.getvalue(), "[mr10.1, ,r10.1.1]")
