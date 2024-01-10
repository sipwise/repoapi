# Copyright (C) 2017-2024 The Sipwise Team - http://sipwise.com
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
from unittest.mock import Mock
from unittest.mock import patch

from django.test import override_settings

from repoapi import utils
from repoapi.test.base import BaseTest


class UtilsTestCase(BaseTest):
    @patch("repoapi.utils.executeAndReturnOutput")
    def test_get_next_release_ko(self, ear):
        ear.return_value = [1, "", ""]
        val = utils.get_next_release("whatever")
        self.assertIsNone(val)

    @patch("repoapi.utils.executeAndReturnOutput")
    def test_get_next_release0(self, ear):
        ear.return_value = [0, "mr5.5.1\n", ""]
        val = utils.get_next_release("master")
        self.assertEqual(val, "mr5.5.1")

    @patch("repoapi.utils.executeAndReturnOutput")
    def test_get_next_release1(self, ear):
        ear.return_value = [0, "mr5.4.2\n", ""]
        val = utils.get_next_release("mr5.4")
        self.assertEqual(val, "mr5.4.2")

    @patch("repoapi.utils.executeAndReturnOutput")
    def test_get_next_release2(self, ear):
        ear.return_value = [0, "\n", ""]
        val = utils.get_next_release("mr5.4")
        self.assertEqual(val, None)

    @override_settings(
        REPOAPI_ARTIFACT_JOB_REGEX=[".*-repos$"],
        JBI_ARTIFACT_JOBS=["fake-release-tools-runner"],
    )
    def test__is_download_artifacts(self):
        self.assertFalse(utils.is_download_artifacts("whatever-binaries"))
        self.assertTrue(
            utils.is_download_artifacts("fake-release-tools-runner")
        )
        self.assertTrue(utils.is_download_artifacts("whatever-repos"))

    @patch("repoapi.utils.shutil")
    def test_cleanup_build_ko(self, sh):
        dst_path = Mock()
        dst_path.exists.return_value = True
        build_path = Mock()
        build_path.exists.return_value = False
        utils.cleanup_build(build_path, dst_path)
        sh.move.assert_not_called()

    @patch("repoapi.utils.shutil")
    def test_cleanup_build_no_dst(self, sh):
        dst_path = Mock()
        dst_path.exists.return_value = False
        build_path = Mock()
        build_path.exists.return_value = True
        utils.cleanup_build(build_path, dst_path)
        dst_path.mkdir.assert_called_once()
        sh.move.assert_called_once_with(build_path, dst_path)

    @patch("repoapi.utils.shutil")
    def test_cleanup_build(self, sh):
        dst_path = Mock()
        dst_path.exists.return_value = True
        build_path = Mock()
        build_path.exists.return_value = True
        utils.cleanup_build(build_path, dst_path)
        dst_path.mkdir.assert_not_called()
        sh.move.assert_called_once_with(build_path, dst_path)
