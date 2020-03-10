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
from repoapi.test.base import BaseTest


@override_settings(DEBUG=True, JBI_ALLOWED_HOSTS=["fake.local"])
@patch("repoapi.utils.dlfile")
class BuildReleaseManagerTestCase(BaseTest):
    fixtures = ["test_models", "test_models_jbi"]
    release = "release-mr8.1"
    release_uuid = "dbe569f7-eab6-4532-a6d1-d31fb559649b"

    def test_create_trunk(self, dlf):
        br = BuildRelease.objects.create_build_release("AAA", "trunk")
        self.assertEqual(br.release, "release-trunk-buster")
        self.assertEqual(br.distribution, "buster")
        self.assertIsNone(br.tag)
        self.assertEqual(br.branch, "master")
        self.assertNotEqual(len(br.projects), 0)
        self.assertIn("sipwise-base", br.projects)

    def test_release_jobs(self, dlf):
        jobs = BuildRelease.objects.release_jobs(self.release_uuid)
        self.assertListEqual(list(jobs.all()), ["release-copy-debs-yml"])

    def test_release_jobs_uuids(self, dlf):
        uuids = BuildRelease.objects.release_jobs_uuids(
            self.release_uuid, "release-copy-debs-yml"
        )
        self.assertListEqual(
            list(uuids.values("tag")),
            [
                {"tag": "3cc6063e-6627-48b6-9dff-92e693547f62"},
                {"tag": "3cc6063e-6627-48b6-9dff-92e693547f59"},
            ],
        )

    def test_releases_with_builds(self, dlf):
        self.assertListEqual(
            list(BuildRelease.objects.releases_with_builds()), ["mr8.1"]
        )


@override_settings(DEBUG=True)
class BuildReleaseTestCase(TestCase):
    fixtures = [
        "test_models",
    ]

    def test_distribution(self):
        build = BuildRelease.objects.get(
            uuid="dbe569f7-eab6-4532-a6d1-d31fb559649b"
        )
        self.assertEqual(build.distribution, "buster")

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
        self.br.pool_size = 1
        self.jbi = MagicMock()
        self.jbi.result = "SUCCESS"

    def test_append_built_fist(self):
        self.br.built_projects = "release-copy-debs-yml"
        self.jbi.projectname = "data-hal"
        self.jbi.jobname = "data-hal-repos"
        self.assertTrue(self.br.append_built(self.jbi))
        self.assertEqual(
            self.br.built_projects, "release-copy-debs-yml,data-hal"
        )
        self.assertEqual(self.br.pool_size, 0)

    def test_append_built_empty(self):
        self.jbi.projectname = "data-hal"
        self.jbi.jobname = "data-hal-repos"
        self.assertTrue(self.br.append_built(self.jbi))
        self.assertEqual(self.br.built_projects, "data-hal")
        self.assertEqual(self.br.pool_size, 0)

    def test_append_built(self):
        self.br.built_projects = "data-hal"
        self.jbi.projectname = "libinewrate"
        self.jbi.jobname = "libinewrate-repos"
        self.br.pool_size = 2
        self.assertTrue(self.br.append_built(self.jbi))
        self.assertEqual(self.br.built_projects, "data-hal,libinewrate")
        self.assertEqual(self.br.pool_size, 1)

    def test_append_built_dup(self):
        self.br.built_projects = "data-hal"
        self.jbi.projectname = "data-hal"
        self.jbi.jobname = "data-hal-repos"
        self.assertFalse(self.br.append_built(self.jbi))
        self.assertEqual(self.br.built_projects, "data-hal")
        self.assertEqual(self.br.pool_size, 1)

    def test_append_built_release_job(self):
        self.jbi.projectname = "release-copy-debs-yml"
        self.jbi.jobname = "release-copy-debs-yml"
        self.br.pool_size = 0
        self.assertTrue(self.br.append_built(self.jbi))
        self.assertEqual(self.br.built_projects, self.jbi.jobname)
        self.assertEqual(self.br.pool_size, 0)

    def test_append_built_fail_empty(self):
        self.jbi.projectname = "data-hal"
        self.jbi.jobname = "data-hal-repos"
        self.jbi.result = "FAILURE"
        self.assertTrue(self.br.append_built(self.jbi))
        self.assertIsNone(self.br.built_projects)
        self.assertEqual(self.br.failed_projects, "data-hal")
        self.assertEqual(self.br.pool_size, 0)

    def test_append_built_fail(self):
        self.br.built_projects = "data-hal"
        self.jbi.projectname = "libinewrate"
        self.jbi.jobname = "libinewrate-repos"
        self.jbi.result = "FAILURE"
        self.assertTrue(self.br.append_built(self.jbi))
        self.assertEqual(self.br.built_projects, "data-hal")
        self.assertEqual(self.br.failed_projects, "libinewrate")
        self.assertEqual(self.br.pool_size, 0)

    def test_append_built_fail_dup(self):
        self.br.built_projects = "data-hal"
        self.br.failed_projects = "libinewrate"
        self.jbi.projectname = "libinewrate"
        self.jbi.jobname = "libinewrate-repos"
        self.jbi.result = "FAILURE"
        self.assertFalse(self.br.append_built(self.jbi))
        self.assertEqual(self.br.built_projects, "data-hal")
        self.assertEqual(self.br.failed_projects, "libinewrate")
        self.assertEqual(self.br.pool_size, 1)

    def test_append_built_fail_piuparts(self):
        self.br.built_projects = "data-hal,libinewrate"
        self.jbi.projectname = "libinewrate"
        self.jbi.jobname = "libinewrate-piuparts"
        self.jbi.result = "FAILURE"
        self.assertFalse(self.br.append_built(self.jbi))
        self.assertEqual(self.br.built_projects, "data-hal,libinewrate")
        self.assertIsNone(self.br.failed_projects)
        self.assertEqual(self.br.pool_size, 1)

    def test_append_built_release_job_fail(self):
        self.jbi.projectname = "release-copy-debs-yml"
        self.jbi.jobname = "release-copy-debs-yml"
        self.jbi.result = "FAILURE"
        self.assertTrue(self.br.append_built(self.jbi))
        self.assertIsNone(self.br.built_projects)
        self.assertEqual(self.br.failed_projects, "release-copy-debs-yml")
        self.assertEqual(self.br.pool_size, 0)

    def test_next_empty_fail(self):
        self.br.failed_projects = "release-copy-debs-yml"
        self.assertIsNone(self.br.next)

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
            self.jbi.jobname = "{}-repos".format(prj)
            self.assertTrue(self.br.append_built(self.jbi))
            _next = self.br.next
            try:
                self.assertEqual(_next, build_deps[0][i])
                i += 1
            except IndexError:
                self.assertEqual(_next, "ngcp-schema")
        self.jbi.projectname = "ngcp-schema"
        self.jbi.jobname = "ngcp-schema-repos"
        self.assertTrue(self.br.append_built(self.jbi))
        self.assertEqual(self.br.next, "asterisk-voicemail")

    def test_next_last(self):
        pl = self.br.projects_list[:-1]
        pl.insert(0, "release-copy-debs-yml")
        self.br.built_projects = ",".join(pl)
        self.assertTrue(
            self.br.built_projects.startswith("release-copy-debs-yml,")
        )
        last_projectname = self.br.projects_list[-2]
        self.assertTrue(
            self.br.built_projects.endswith(",{}".format(last_projectname))
        )
        self.jbi.projectname = self.br.projects_list[-1]
        self.jbi.jobname = "{}-repos".format(self.jbi.projectname)
        self.assertTrue(self.br.append_built(self.jbi))
        self.assertIsNone(self.br.next)

    def test_next_stop(self):
        self.br.built_projects = "release-copy-debs-yml,{}".format(
            self.br.projects
        )
        self.assertIsNone(self.br.next)


@override_settings(
    DEBUG=True,
    JBI_ALLOWED_HOSTS=["fake.local"],
    CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
)
@patch("repoapi.utils.dlfile")
class JBIManageTest(TestCase):
    @patch("build.models.build_next")
    def test_jbi_manage_ko(self, bn, dl):
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
        bn.assert_not_called()

    @patch("build.models.build_next")
    def test_jbi_manage_ok_release_job(self, bn, dl):
        br = BuildRelease.objects.create_build_release("UUID_mr8.1", "mr8.1")
        self.assertEqual(br.pool_size, 0)
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
        bn.assert_called_once_with(br.pk)
        self.assertEqual(br.pool_size, 1)
        self.assertEqual(br.triggered_projects, "data-hal")

    @patch("build.models.build_next")
    def test_jbi_manage_skip(self, bn, dl):
        br = BuildRelease.objects.create_build_release("UUID_mr8.1", "mr8.1")
        br.pool_size = 1
        br.triggered_projects = "kamailio"
        br.save()
        jbi = JenkinsBuildInfo.objects.create(
            job_url="http://fake.local/job/kamailio-get-code/",
            projectname="kamailio",
            jobname="kamailio-get-code",
            tag="UUIDA",
            param_release="mr8.1",
            param_release_uuid="UUID_mr8.1",
            buildnumber=1,
            result="SUCCESS",
        )
        br = BuildRelease.objects.get(pk=br.pk)
        self.assertIsNone(br.built_projects)
        params = {"instance": jbi, "created": True}
        jbi_manage(JenkinsBuildInfo, **params)
        bn.assert_not_called()
        self.assertEqual(br.pool_size, 1)
        self.assertEqual(br.triggered_projects, "kamailio")


@override_settings(
    DEBUG=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
)
class BRManageTest(TestCase):
    @patch("build.tasks.trigger_copy_deps")
    def test_br_manage(self, tcd):
        br = BuildRelease.objects.create_build_release("UUID_mr8.1", "mr8.1")
        tcd.assert_called_once_with(
            internal=True, release=br.release, release_uuid=br.uuid
        )


@override_settings(DEBUG=True)
class BuildReleaseRetriggerTest(TestCase):
    def setUp(self):
        self.br = BuildRelease.objects.create_build_release("AAA", "trunk")
        self.jbi = MagicMock()
        self.jbi.result = "SUCCESS"

    def test_append_built_empty(self):
        self.br.failed_projects = "data-hal"
        self.jbi.projectname = "data-hal"
        self.jbi.jobname = "data-hal-repos"
        self.assertTrue(self.br.append_built(self.jbi))
        self.assertEqual(self.br.built_projects, "data-hal")
        self.assertIsNone(self.br.failed_projects)

    def test_append_built(self):
        self.br.built_projects = "data-hal"
        self.br.failed_projects = "libinewrate"
        self.jbi.projectname = "libinewrate"
        self.jbi.jobname = "libinewrate-repos"
        self.assertTrue(self.br.append_built(self.jbi))
        self.assertEqual(self.br.built_projects, "data-hal,libinewrate")
        self.assertIsNone(self.br.failed_projects)
