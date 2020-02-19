# Copyright (C) 2017 The Sipwise Team - http://sipwise.com
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
from unittest.mock import MagicMock
from unittest.mock import patch

from django.test import override_settings
from django.test import TestCase

from build.models import BuildRelease
from build.models import jbi_manage
from repoapi.models import JenkinsBuildInfo


@override_settings(DEBUG=True)
class BuildReleaseManagerTestCase(TestCase):
    def test_create_trunk(self):
        br = BuildRelease.objects.create_build_release("AAA", "trunk")
        self.assertEqual(br.release, "release-trunk-buster")
        self.assertEqual(br.distribution, "buster")
        self.assertIsNone(br.tag)
        self.assertEqual(br.branch, "master")
        self.assertNotEqual(len(br.projects), 0)
        self.assertIn("sipwise-base", br.projects)


@override_settings(DEBUG=True)
class BuildReleaseTestCase(TestCase):
    fixtures = [
        "test_models",
    ]

    def test_projects_list(self):
        build = BuildRelease.objects.get(
            uuid="dbe569f7-eab6-4532-a6d1-d31fb559649b"
        )
        self.assertCountEqual(
            build.projects_list,
            ["kamailio", "lua-ngcp-kamailio", "ngcp-panel"],
        )

    def test_built_projects_list(self):
        build = BuildRelease.objects.get(
            uuid="dbe569f7-eab6-4532-a6d1-d31fb559649b"
        )
        self.assertCountEqual(
            build.built_projects_list, ["kamailio", "lua-ngcp-kamailio"],
        )

    def test_queued_projects_list(self):
        build = BuildRelease.objects.get(
            uuid="dbe569f7-eab6-4532-a6d1-d31fb559649b"
        )
        self.assertCountEqual(
            build.queued_projects_list, ["ngcp-panel"],
        )

    def test_config(self):
        build = BuildRelease.objects.get(
            uuid="dbe569f7-eab6-4532-a6d1-d31fb559649b"
        )
        config = build.config
        self.assertIsNotNone(config)
        self.assertIs(config, build.config)

    def test_branch_or_tag_trunk(self):
        build = BuildRelease.objects.create_build_release("AAA", "trunk")
        self.assertEqual(build.branch_or_tag, "branch/master")

    def test_branch_or_tag_mrXX(self):
        build = BuildRelease.objects.get(
            uuid="dbe569f7-eab6-4532-a6d1-d31fb559649b"
        )
        self.assertEqual(build.branch_or_tag, "branch/mr8.1")

    def test_branch_or_tag_mrXXX(self):
        build = BuildRelease.objects.create_build_release("AAA", "mr7.5.2")
        self.assertEqual(build.branch_or_tag, "tag/mr7.5.2.1")

    def test_build_deps(self):
        build_deps = [
            [
                "data-hal",
                "libinewrate",
                "libswrate",
                "libtcap",
                "sipwise-base",
                "check-tools",
            ],
            ["ngcp-schema"],
        ]
        build = BuildRelease.objects.create_build_release("AAA", "trunk")
        self.assertListEqual(build.build_deps, build_deps)


@override_settings(DEBUG=True)
class BuildReleaseStepsTest(TestCase):
    def setUp(self):
        self.br = BuildRelease.objects.create_build_release("AAA", "trunk")
        self.jbi = MagicMock()
        self.jbi.result = "SUCCESS"

    def test_append_built_empty(self):
        self.jbi.projectname = "data-hal"
        self.br.append_built(self.jbi)
        self.assertEqual(self.br.built_projects, "data-hal")

    def test_append_built(self):
        self.br.built_projects = "data-hal"
        self.jbi.projectname = "libinewrate"
        self.br.append_built(self.jbi)
        self.assertEqual(self.br.built_projects, "data-hal,libinewrate")

    def test_next_empty(self):
        self.assertEqual(self.br.next, "data-hal")

    def test_next_build_deps(self):
        build_deps = [
            [
                "data-hal",
                "libinewrate",
                "libswrate",
                "libtcap",
                "sipwise-base",
                "check-tools",
            ],
            ["ngcp-schema"],
        ]
        self.assertEqual(len(self.br.config.build_deps.keys()), 7)
        i = 1
        for prj in build_deps[0]:
            self.jbi.projectname = prj
            self.br.append_built(self.jbi)
            _next = self.br.next
            try:
                self.assertEqual(_next, build_deps[0][i])
                i += 1
            except IndexError:
                self.assertEqual(_next, "ngcp-schema")
        self.jbi.projectname = "ngcp-schema"
        self.br.append_built(self.jbi)
        self.assertEqual(self.br.next, "asterisk-voicemail")

    def test_next_last(self):
        self.br.built_projects = ",".join(self.br.projects_list[:-1])
        self.jbi.projectname = self.br.projects_list[-1]
        self.br.append_built(self.jbi)
        self.assertIsNone(self.br.next)

    def test_next_stop(self):
        self.br.built_projects = self.br.projects
        self.assertIsNone(self.br.next)


@override_settings(
    DEBUG=True,
    JBI_ALLOWED_HOSTS=["fake.local"],
    CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
)
@patch("repoapi.utils.dlfile")
class JBIManageTest(TestCase):
    @patch("build.models.trigger_build")
    def test_jbi_manage_ko(self, tb, dl):
        BuildRelease.objects.create_build_release("AAA", "trunk")
        jbi = JenkinsBuildInfo.objects.create(
            job_url="http://fake.local/job/release-copy-debs-yml/",
            projectname="release-copy-debs-yml",
            jobname="release-copy-debs-yml",
            param_tag="UUIDA",
            param_release="mr8.2",
            param_release_uuid="UUID_mr8.2",
            buildnumber=1,
            result="SUCCESS",
        )
        params = {"instance": jbi, "created": True}
        jbi_manage(JenkinsBuildInfo, **params)
        tb.assert_not_called()

    @patch("build.models.trigger_build")
    def test_jbi_manage_ok(self, tb, dl):
        br = BuildRelease.objects.create_build_release("UUID_mr8.1", "mr8.1")
        JenkinsBuildInfo.objects.create(
            job_url="http://fake.local/job/release-copy-debs-yml/",
            projectname="release-copy-debs-yml",
            jobname="release-copy-debs-yml",
            tag="UUIDA",
            param_release="mr8.1",
            param_release_uuid="UUID_mr8.1",
            buildnumber=1,
            result="SUCCESS",
        )
        br = BuildRelease.objects.get(pk=br.pk)
        self.assertEqual(br.built_projects, "release-copy-debs-yml")
        tb.assert_called_once_with(
            "data-hal",
            br.uuid,
            br.release,
            br.uuid,
            br.branch_or_tag,
            br.distribution,
        )


@override_settings(
    DEBUG=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
)
class BRManageTest(TestCase):
    @patch("build.tasks.trigger_copy_deps")
    @patch("build.models.trigger_build")
    def test_br_manage(self, tb, rb):
        br = BuildRelease.objects.create_build_release("UUID_mr8.1", "mr8.1")
        tb.assert_not_called()
        rb.assert_called_once_with(
            internal=True, release=br.release, release_uuid=br.uuid
        )
