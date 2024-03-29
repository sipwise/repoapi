# Copyright (C) 2022 The Sipwise Team - http://sipwise.com
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
import json
from pathlib import Path
from unittest.mock import call
from unittest.mock import patch

from django.conf import settings
from django.test import SimpleTestCase

from tracker import utils
from tracker.conf import TrackerConf

FIXTURES_PATH = settings.BASE_DIR.joinpath("tracker", "fixtures")
MANTIS_ISSUE_JSON = FIXTURES_PATH.joinpath("mantis_issue.json")
MANTIS_ISSUE_ID = 36018

tracker_settings = TrackerConf()


class FakeResponse:
    def __init__(self, _json: dict):
        self._json = _json

    def json(self):
        return self._json

    def raise_for_status(self):
        return False


class FakeResponseFile:
    def __init__(self, filepath: Path):
        self.filepath = filepath

    def json(self):
        with self.filepath.open() as f:
            res = json.load(f)
        return res


class TestFakeResponseFile(SimpleTestCase):
    def test_json(self):
        fake = FakeResponseFile(MANTIS_ISSUE_JSON)
        res = fake.json()
        self.assertTrue(len(res["issues"]), 1)
        self.assertEqual(res["issues"][0]["id"], MANTIS_ISSUE_ID)


class TestFakeResponse(SimpleTestCase):
    def test_json(self):
        fake = FakeResponse(FakeResponseFile(MANTIS_ISSUE_JSON).json())
        res = fake.json()
        self.assertTrue(len(res["issues"]), 1)
        self.assertEqual(res["issues"][0]["id"], MANTIS_ISSUE_ID)


def set_target_release_value(issue, value):
    cf = issue["custom_fields"]
    for val in cf:
        if val["field"]["id"] == tracker_settings.MANTIS_TARGET_RELEASE["id"]:
            val["value"] = value
            return val


def get_target_release_value(issue):
    cf = issue["custom_fields"]
    for val in cf:
        if val["field"]["id"] == tracker_settings.MANTIS_TARGET_RELEASE["id"]:
            return val["value"]


class TestUtils(SimpleTestCase):
    ISSUE_URL = "https://support.local/api/rest/issues/36018"

    @patch(
        "tracker.utils.mantis_query",
        return_value=FakeResponseFile(MANTIS_ISSUE_JSON),
    )
    def test_mantis_get_issue_ok(self, mq):
        res = utils.mantis_get_issue(MANTIS_ISSUE_ID)
        self.assertEqual(res["id"], MANTIS_ISSUE_ID)
        mq.assert_called_once_with("GET", self.ISSUE_URL)

    def test_mantis_get_issue_id(self):
        fake = FakeResponseFile(MANTIS_ISSUE_JSON)
        res = utils.mantis_get_issue_id(fake.json(), MANTIS_ISSUE_ID)
        self.assertEqual(res["id"], MANTIS_ISSUE_ID)

    def test_mantis_get_issue_id_str(self):
        fake = FakeResponseFile(MANTIS_ISSUE_JSON)
        res = utils.mantis_get_issue_id(fake.json(), str(MANTIS_ISSUE_ID))
        self.assertEqual(res["id"], MANTIS_ISSUE_ID)

    def test_mantis_get_target_releases(self):
        fake = FakeResponseFile(MANTIS_ISSUE_JSON)
        issue = utils.mantis_get_issue_id(fake.json(), MANTIS_ISSUE_ID)
        set_target_release_value(issue, "mr10.1")
        res = utils.mantis_get_target_releases(issue)
        self.assertListEqual(res, ["mr10.1"])

        set_target_release_value(issue, "mr10.1, mr8.5.1")
        res = utils.mantis_get_target_releases(issue)
        self.assertListEqual(res, ["mr8.5.1", "mr10.1"])

        set_target_release_value(issue, "mr10.1, mr8.5.1,,")
        res = utils.mantis_get_target_releases(issue)
        self.assertListEqual(res, ["mr8.5.1", "mr10.1"])

    @patch(
        "tracker.utils.mantis_query",
        return_value=FakeResponseFile(MANTIS_ISSUE_JSON),
    )
    def test_mantis_set_release_targets(self, mq):
        fake_issue_patched = utils.mantis_get_issue_id(
            FakeResponseFile(MANTIS_ISSUE_JSON).json(), MANTIS_ISSUE_ID
        )
        value = set_target_release_value(fake_issue_patched, "mr10.1")
        payload = {"custom_fields": [value]}

        utils.mantis_set_release_target(MANTIS_ISSUE_ID, "mr10.1")
        calls = [
            call("GET", self.ISSUE_URL),
            call("PATCH", self.ISSUE_URL, json.dumps(payload)),
        ]
        mq.assert_has_calls(calls)

    @patch("tracker.utils.mantis_query")
    def test_mantis_set_release_target_ko(self, mq):
        """value is already there"""
        fake_issue_patched = utils.mantis_get_issue_id(
            FakeResponseFile(MANTIS_ISSUE_JSON).json(), MANTIS_ISSUE_ID
        )
        fake_issues = {"issues": [fake_issue_patched]}
        set_target_release_value(fake_issue_patched, "mr10.1,mr10.1.1")
        mq.configure_mock(return_value=FakeResponse(fake_issues))
        utils.mantis_set_release_target(MANTIS_ISSUE_ID, "mr10.1.1")
        mq.assert_called_once_with("GET", self.ISSUE_URL)
