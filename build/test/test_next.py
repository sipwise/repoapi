# Copyright (C) 2024 The Sipwise Team - http://sipwise.com
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

from django.test import override_settings
from django.test import SimpleTestCase

from build.conf import settings
from build.models import BuildRelease
from build.models import ReleaseConfig
from build.utils import get_simple_release
from build.utils import guess_trunk_filename
from repoapi.models import JenkinsBuildInfo
from repoapi.test.base import BaseTest

FIXTURES_PATH = settings.BASE_DIR.joinpath("build", "fixtures")


@override_settings(
    BUILD_REPOS_SCRIPTS_CONFIG_DIR=FIXTURES_PATH.joinpath("config.next")
)
class BuildReleaseTestCase(BaseTest):
    fixtures = ["test_trunk_next"]
    release_uuid = "53f9e166-4271-4581-ae3d-b3c1bb0bb081"

    def test_distribution(self):
        br = BuildRelease.objects.get(uuid=self.release_uuid)
        self.assertEqual(br.distribution, "bookworm")

    def test_build_release(self):
        br = BuildRelease.objects.get(uuid=self.release_uuid)
        self.assertEqual(br.release, "trunk-next")
        self.assertEqual(br.build_release, "trunk")


@override_settings(
    BUILD_REPOS_SCRIPTS_CONFIG_DIR=FIXTURES_PATH.joinpath("config.next"),
    JBI_ALLOWED_HOSTS=["fake.local"],
)
@patch("repoapi.utils.dlfile")
@patch("build.tasks.trigger_build")
class BuildReleaseBuilds(BaseTest):
    fixtures = ["test_trunk_next"]
    release = "trunk"
    release_uuid = "53f9e166-4271-4581-ae3d-b3c1bb0bb081"
    project = "ngcpcfg"

    def test_jbi_manage_ok_release_job(self, tb, _):
        br = BuildRelease.objects.get(uuid=self.release_uuid)
        self.assertEqual(br.pool_size, 0)
        JenkinsBuildInfo.objects.create(
            job_url="http://fake.local/job/release-copy-debs-yml/",
            projectname="release-copy-debs-yml",
            jobname="release-copy-debs-yml",
            tag="UUIDA",
            param_release=self.release,
            param_release_uuid=self.release_uuid,
            buildnumber=1,
            result="SUCCESS",
        )
        params = {
            "project": f"{self.project}-get-code",
            "release_uuid": self.release_uuid,
            "trigger_release": self.release,
            "trigger_branch_or_tag": "branch/master",
            "trigger_distribution": "bookworm",
        }
        tb.assert_called_once_with(**params)


@override_settings(
    BUILD_REPOS_SCRIPTS_CONFIG_DIR=FIXTURES_PATH.joinpath("config.next")
)
class ReleaseConfigNext(SimpleTestCase):
    @override_settings(
        BUILD_REPOS_SCRIPTS_CONFIG_DIR=FIXTURES_PATH.joinpath("config")
    )
    def test_trunk_next_check(self):
        """
        No trunk-next.yml in config

        validate() works fine but
        release gets detected as trunk
        since there is no trunk-next.yml in config!!
        """
        ok = FIXTURES_PATH.joinpath("config.next", "trunk-next.yml")
        data = ReleaseConfig.load_config(ok)
        cfg = ReleaseConfig("fake", config=data)
        self.assertEqual(cfg.branch, "master")
        self.assertEqual(cfg.config_file, "fake.yml")
        self.assertEqual(cfg.debian_release, "bookworm")
        self.assertEqual(cfg.release, "trunk")
        self.assertEqual(cfg.distribution, None)

    def test_guess_trunk_filename(self):
        res = guess_trunk_filename("release-trunk-bullseye")
        self.assertEqual(res, "trunk")
        res = guess_trunk_filename("release-trunk-bookworm")
        self.assertEqual(res, "trunk-next")

    @override_settings(BUILD_RELEASES_SKIP=["mr0.1"])
    def test_supported_releases(self):
        supported = [
            "release-trunk-bullseye",
            "release-trunk-bookworm",
        ]
        res = ReleaseConfig.supported_releases()
        self.assertListEqual(res, supported)

    def test_trunk_next(self):
        rc = ReleaseConfig("trunk-next")
        self.assertIsNotNone(rc.config)
        self.assertEqual(rc.debian_release, "bookworm")
        self.assertNotIn("rainbow-misc", rc.projects)

        rc = ReleaseConfig("release-trunk-bookworm")
        self.assertEqual(rc.debian_release, "bookworm")
        self.assertNotIn("rainbow-misc", rc.projects)


@override_settings(
    BUILD_REPOS_SCRIPTS_CONFIG_DIR=FIXTURES_PATH.joinpath("config.next")
)
class BuildReleaseCreate(BaseTest):
    @patch("build.tasks.trigger_copy_deps")
    @patch("build.signals.build_resume")
    def test_create_build_release(self, build_resume, trigger_copy_deps):
        br = BuildRelease.objects.create_build_release(
            "UUID1",
            "release-trunk-bookworm",
        )
        self.assertEqual(br.release, "trunk-next")
        self.assertEqual(br.distribution, "bookworm")
        build_resume.delay.assert_not_called()
        trigger_copy_deps.assert_called_once_with(
            internal=True,
            release="release-trunk-bookworm",
            release_uuid=br.uuid,
        )

    def test_get_simple_release(self):
        val = get_simple_release("release-trunk-bookworm")
        self.assertEqual(val, "trunk-next")

    def test_is_trunk_next(self):
        self.assertTrue(ReleaseConfig.is_trunk_next("release-trunk-bookworm"))

    @override_settings(
        BUILD_REPOS_SCRIPTS_CONFIG_DIR=FIXTURES_PATH.joinpath("config")
    )
    def test_is_trunk_next_no_cfg(self):
        self.assertFalse(ReleaseConfig.is_trunk_next("release-trunk-bookworm"))

    def test_config(self):
        cfg = ReleaseConfig("release-trunk-bookworm")
        self.assertEqual(cfg.branch, "master")
        self.assertEqual(cfg.distribution, "bookworm")
        self.assertEqual(cfg.config_file, "trunk-next.yml")
        self.assertEqual(cfg.debian_release, "bookworm")
        self.assertEqual(cfg.release, "trunk-next")
