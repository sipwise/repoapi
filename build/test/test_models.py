# Copyright (C) 2017-2022 The Sipwise Team - http://sipwise.com
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
import datetime
from unittest.mock import MagicMock
from unittest.mock import patch

from django.test import override_settings
from django.utils import timezone

from build.exceptions import BuildReleaseUnique
from build.exceptions import PreviousBuildNotDone
from build.models import build_release_jobs
from build.models import BuildRelease
from repoapi.models import JenkinsBuildInfo
from repoapi.test.base import BaseTest


def set_build_done(qs):
    for br in qs:
        if br.is_update:
            br.built_projects = br.projects
        else:
            br.built_projects = build_release_jobs + "," + br.projects
        br.save()


@override_settings(JBI_ALLOWED_HOSTS=["fake.local"])
@patch("repoapi.utils.dlfile")
class BuildReleaseManagerTestCase(BaseTest):
    fixtures = ["test_models", "test_models_jbi"]
    release = "release-mr8.1"
    release_uuid = "dbe569f7-eab6-4532-a6d1-d31fb559649b"

    def test_create_trunk(self, dlf):
        br = BuildRelease.objects.create_build_release("AAA", "trunk")
        self.assertEqual(br.release, "trunk")
        self.assertEqual(br.distribution, "buster")
        self.assertIsNone(br.tag)
        self.assertEqual(br.branch, "master")
        self.assertNotEqual(len(br.projects), 0)
        self.assertIn("sipwise-base", br.projects)

    def test_create_release_trunk(self, dlf):
        br = BuildRelease.objects.create_build_release(
            "AAA", "release-trunk-bullseye"
        )
        self.assertEqual(br.release, "trunk")
        self.assertEqual(br.distribution, "bullseye")
        self.assertIsNone(br.tag)
        self.assertEqual(br.branch, "master")
        self.assertNotEqual(len(br.projects), 0)
        self.assertIn("sipwise-base", br.projects)

    def test_create_mrXX(self, dlf):
        BuildRelease.objects.filter(release="release-mr8.1").delete()
        self.assertFalse(
            BuildRelease.objects.filter(release="release-mr8.1").exists()
        )
        br = BuildRelease.objects.create_build_release("AAA", "mr8.1")
        self.assertEqual(br.release, "release-mr8.1")

    def test_create_mrXX_update_building(self, dlf):
        """mr8.1 is building, don't allow a new build"""
        with self.assertRaises(PreviousBuildNotDone):
            BuildRelease.objects.create_build_release("AAA", "mr8.1")

    def test_create_mrXX_update(self, dlf):
        set_build_done(BuildRelease.objects.filter(release="release-mr8.1"))
        br = BuildRelease.objects.create_build_release("AAA", "mr8.1")
        self.assertEqual(br.release, "release-mr8.1-update")

    def test_create_mrXXX_fail(self, dlf):
        BuildRelease.objects.create_build_release("AAA", "mr7.5.3")
        with self.assertRaises(BuildReleaseUnique):
            BuildRelease.objects.create_build_release("BBB", "mr7.5.3")

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

    def test_last_update(self, dlf):
        br = BuildRelease.objects.get(uuid=self.release_uuid)
        job = JenkinsBuildInfo.objects.get(id=4)
        self.assertEqual(br.last_update, job.date)

    def test_release(self, dlf):
        prev = BuildRelease.objects.filter(release="release-mr8.1")
        set_build_done(prev)
        br = BuildRelease.objects.create_build_release("BBB", "mr8.1")
        self.assertEqual(br.release, "release-mr8.1-update")
        qs = BuildRelease.objects.release("release-mr8.1", "buster")
        self.assertEqual(qs.count(), prev.count() + 1)

    def test_create_fake(self, dlf):
        br = BuildRelease.objects.create_build_release(
            "AAA", "trunk", fake=True
        )
        self.assertEqual(
            br.start_date, timezone.make_aware(datetime.datetime(1977, 1, 1))
        )
        self.assertTrue(br.done)


class BuildReleaseTestCase(BaseTest):
    fixtures = ["test_models"]
    release_uuid = "dbe569f7-eab6-4532-a6d1-d31fb559649b"

    def test_distribution(self):
        build = BuildRelease.objects.get(uuid=self.release_uuid)
        self.assertEqual(build.distribution, "buster")

    def test_projects_list(self):
        build = BuildRelease.objects.get(uuid=self.release_uuid)
        self.assertCountEqual(
            build.projects_list,
            ["kamailio", "lua-ngcp-kamailio", "ngcp-panel"],
        )

    def test_built_projects_list(self):
        build = BuildRelease.objects.get(uuid=self.release_uuid)
        self.assertCountEqual(
            build.built_projects_list, ["kamailio", "lua-ngcp-kamailio"]
        )

    def test_queued_projects_list(self):
        build = BuildRelease.objects.get(uuid=self.release_uuid)
        self.assertCountEqual(build.queued_projects_list, ["ngcp-panel"])

    def test_config(self):
        build = BuildRelease.objects.get(uuid=self.release_uuid)
        config = build.config
        self.assertIsNotNone(config)
        self.assertIs(config, build.config)

    def test_branch_or_tag_trunk(self):
        build = BuildRelease.objects.create_build_release("AAA", "trunk")
        self.assertEqual(build.branch_or_tag, "branch/master")
        self.assertFalse(build.is_update)

    def test_branch_or_tag_mrXX(self):
        build = BuildRelease.objects.get(uuid=self.release_uuid)
        self.assertEqual(build.branch_or_tag, "branch/mr8.1")
        self.assertEqual(build.release, "release-mr8.1")
        self.assertFalse(build.is_update)

    def test_branch_or_tag_mrXXX(self):
        build = BuildRelease.objects.create_build_release("AAA", "mr7.5.2")
        self.assertEqual(build.branch_or_tag, "tag/mr7.5.2.1")
        self.assertFalse(build.is_update)

    def test_is_update_ok(self):
        set_build_done(BuildRelease.objects.filter(release="release-mr8.1"))
        build = BuildRelease.objects.create_build_release("AAA", "mr8.1")
        self.assertEqual(build.branch_or_tag, "branch/mr8.1")
        self.assertEqual(build.release, "release-mr8.1-update")
        self.assertTrue(build.is_update)

    def test_done_update(self):
        set_build_done(BuildRelease.objects.filter(release="release-mr8.1"))
        build = BuildRelease.objects.create_build_release("AAA", "mr8.1")
        build.built_projects = build.projects
        self.assertTrue(build.done)

    @override_settings(BUILD_RELEASE_JOBS=["release-copy-debs-yml", "other"])
    def test_done(self):
        br = BuildRelease.objects.get(uuid=self.release_uuid)
        br.built_projects = br.projects
        self.assertFalse(br.done)
        br.built_projects = "release-copy-debs-yml,other,{}".format(
            br.projects
        )

    def test_build_deps(self):
        build_deps = [
            [
                "check-tools",
                "data-hal",
                "libinewrate",
                "libswrate",
                "libtcap",
                "sipwise-base",
            ],
            ["ngcp-schema"],
        ]
        build = BuildRelease.objects.create_build_release("AAA", "trunk")
        self.assertListEqual(build.build_deps, build_deps)

    def test_build_deps_mr11_0(self):
        build_deps = [
            [
                "ngcpcfg",
                "system-tests",
            ],
            [
                "data-hal",
                "libswrate",
                "libtcap",
                "sipwise-base",
                "system-tools",
            ],
            [
                "check-tools",
                "ngcp-schema",
            ],
            ["ngcp-panel"],
        ]
        build = BuildRelease.objects.create_build_release("AAA", "mr11.0")
        self.assertListEqual(build.build_deps, build_deps)


class BuildReleaseStepsTest(BaseTest):
    fixtures = ["test_models"]
    release = "release-mr8.1"
    release_uuid = "dbe569f7-eab6-4532-a6d1-d31fb559648b"

    def setUp(self):
        self.br = BuildRelease.objects.get(uuid=self.release_uuid)
        self.br.pool_size = 1
        self.jbi = MagicMock()
        self.jbi.result = "SUCCESS"

    def test_done_empty(self):
        self.assertIsNone(self.br.built_projects)
        self.assertFalse(self.br.done)

    def test_append_built_fist(self):
        self.br.built_projects = "release-copy-debs-yml"
        self.jbi.projectname = "data-hal"
        self.jbi.jobname = "data-hal-repos"
        self.assertTrue(self.br.append_built(self.jbi))
        self.assertEqual(
            self.br.built_projects, "release-copy-debs-yml,data-hal"
        )
        self.assertEqual(self.br.pool_size, 0)
        self.assertFalse(self.br.done)

    def test_append_built_empty(self):
        self.jbi.projectname = "data-hal"
        self.jbi.jobname = "data-hal-repos"
        self.assertTrue(self.br.append_built(self.jbi))
        self.assertEqual(self.br.built_projects, "data-hal")
        self.assertEqual(self.br.pool_size, 0)
        self.assertFalse(self.br.done)

    def test_append_built(self):
        self.br.built_projects = "data-hal"
        self.jbi.projectname = "libinewrate"
        self.jbi.jobname = "libinewrate-repos"
        self.br.pool_size = 2
        self.assertTrue(self.br.append_built(self.jbi))
        self.assertEqual(self.br.built_projects, "data-hal,libinewrate")
        self.assertEqual(self.br.pool_size, 1)
        self.assertFalse(self.br.done)

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
        self.assertFalse(self.br.done)

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
        self.assertEqual(self.br.next, "check-tools")

    def test_next_build_deps(self):
        build_deps = [
            [
                "check-tools",
                "data-hal",
                "libinewrate",
                "libswrate",
                "libtcap",
                "sipwise-base",
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
        self.assertFalse(self.br.done)

    def test_next_build_deps_stop(self):
        build_deps = [
            "check-tools",
            "data-hal",
            "libinewrate",
            "libswrate",
            "libtcap",
            "sipwise-base",
        ]
        i = 1
        self.jbi.projectname = "release-copy-debs-yml"
        self.assertTrue(self.br.append_built(self.jbi))
        for prj in build_deps:
            self.jbi.projectname = prj
            self.assertTrue(self.br.append_triggered(prj))
            _next = self.br.next
            try:
                self.assertEqual(_next, build_deps[i])
                i += 1
            except IndexError:
                self.assertIsNone(_next)
        self.assertFalse(self.br.done)

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
        self.assertTrue(self.br.done)

    def test_next_stop(self):
        self.br.built_projects = "release-copy-debs-yml,{}".format(
            self.br.projects
        )
        self.assertIsNone(self.br.next)

    def test_append_triggered_jobs(self):
        self.assertIsNone(self.br.triggered_jobs)
        res = self.br.append_triggered_job("fake-external-job")
        self.assertTrue(res)
        self.assertEqual(self.br.triggered_jobs, "fake-external-job")
        self.assertEqual(
            self.br.triggered_jobs_list,
            [
                "fake-external-job",
            ],
        )

        res = self.br.append_triggered_job("fake-external-job")
        self.assertFalse(res)
        self.assertEqual(self.br.triggered_jobs, "fake-external-job")

        res = self.br.append_triggered_job("other-external-job")
        self.assertTrue(res)
        self.assertEqual(
            self.br.triggered_jobs, "fake-external-job,other-external-job"
        )
        self.assertEqual(
            self.br.triggered_jobs_list,
            ["fake-external-job", "other-external-job"],
        )


@override_settings(JBI_ALLOWED_HOSTS=["fake.local"])
@patch("repoapi.utils.dlfile")
@patch("build.signals.build_resume")
class JBIManageTest(BaseTest):
    fixtures = ["test_models"]
    release = "release-mr8.1"
    release_uuid = "dbe569f7-eab6-4532-a6d1-d31fb559648b"

    def test_jbi_manage_ko(self, build_resume, dl):
        JenkinsBuildInfo.objects.create(
            job_url="http://fake.local/job/release-copy-debs-yml/",
            projectname="release-copy-debs-yml",
            jobname="release-copy-debs-yml",
            param_tag="UUIDA",
            param_release="mr8.2",
            param_release_uuid="UUID_mr8.2",
            buildnumber=1,
            result="SUCCESS",
        )
        build_resume.delay.assert_not_called()

    def test_jbi_manage_ko_url(self, build_resume, dl):
        JenkinsBuildInfo.objects.create(
            job_url="http://other.local/job/release-copy-debs-yml/",
            projectname="release-copy-debs-yml",
            jobname="release-copy-debs-yml",
            param_tag="UUIDA",
            param_release=self.release,
            param_release_uuid=self.release_uuid,
            buildnumber=1,
            result="SUCCESS",
        )
        build_resume.delay.assert_not_called()

    def test_jbi_manage_ok_release_job(self, build_resume, dl):
        br = BuildRelease.objects.get(uuid=self.release_uuid)
        self.assertEqual(br.pool_size, 0)
        job = JenkinsBuildInfo.objects.create(
            job_url="http://fake.local/job/release-copy-debs-yml/",
            projectname="release-copy-debs-yml",
            jobname="release-copy-debs-yml",
            tag="UUIDA",
            param_release=self.release,
            param_release_uuid=self.release_uuid,
            buildnumber=1,
            result="SUCCESS",
        )
        br = BuildRelease.objects.get(pk=br.pk)
        self.assertEqual(br.built_projects, "release-copy-debs-yml")
        build_resume.delay.assert_called_once_with(br.pk)
        self.assertEqual(br.last_update, job.date)

    def test_jbi_manage_skip(self, build_resume, dl):
        br = BuildRelease.objects.get(uuid=self.release_uuid)
        br.pool_size = 1
        br.triggered_projects = "kamailio"
        br.save()
        JenkinsBuildInfo.objects.create(
            job_url="http://fake.local/job/kamailio-binaries/",
            projectname="kamailio",
            jobname="kamailio-binaries",
            tag="UUIDA",
            param_release=self.release,
            param_release_uuid=self.release_uuid,
            buildnumber=1,
            result="SUCCESS",
        )
        br = BuildRelease.objects.get(pk=br.pk)
        self.assertIsNone(br.built_projects)
        build_resume.delay.assert_not_called()
        self.assertEqual(br.pool_size, 1)
        self.assertEqual(br.triggered_projects, "kamailio")


class BRManageTest(BaseTest):
    fixtures = ["test_models"]

    @patch("build.tasks.trigger_copy_deps")
    @patch("build.signals.build_resume")
    def test_br_manage(self, build_resume, trigger_copy_deps):
        br = BuildRelease.objects.create_build_release("UUID", "mr7.5")
        build_resume.delay.assert_not_called()
        trigger_copy_deps.assert_called_once_with(
            internal=True, release=br.release, release_uuid=br.uuid
        )

    @patch("build.tasks.trigger_copy_deps")
    @patch("build.signals.build_resume")
    def test_br_manage_ko(self, build_resume, trigger_copy_deps):
        set_build_done(BuildRelease.objects.filter(release="release-mr8.1"))
        br = BuildRelease.objects.create_build_release("UUID1", "mr8.1")
        build_resume.delay.assert_called_once_with(br.id)
        trigger_copy_deps.assert_not_called()


class BuildReleaseRetriggerTest(BaseTest):
    fixtures = ["test_models"]
    release = "release-mr8.1"
    release_uuid = "dbe569f7-eab6-4532-a6d1-d31fb559648b"

    def setUp(self):
        self.br = BuildRelease.objects.get(uuid=self.release_uuid)
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


@override_settings(JBI_ALLOWED_HOSTS=["fake.local"])
class RefreshProjects(BaseTest):
    fixtures = [
        "test_weekly",
    ]
    release = "release-trunk-weekly"
    release_uuid = "dbe569f7-eab6-4532-a6d1-d31fb559649b"

    def setUp(self):
        self.br = BuildRelease.objects.get(uuid=self.release_uuid)

    def test_refresh_append(self):
        self.assertNotIn("ngcp-cve-scanner", self.br.projects_list)
        self.assertIn("ngcp-cve-scanner", self.br.config.projects)
        _append, _removed = self.br.refresh_projects()
        self.assertEqual(_append, ["ngcp-cve-scanner"])
        self.assertEqual(_removed, [])
        self.assertIn("ngcp-cve-scanner", self.br.projects_list)

    @patch("repoapi.utils.dlfile")
    @patch("build.signals.build_resume")
    def test_refresh_remove(self, build_resume, dl):
        self.br.projects += ",fake-project"
        self.assertIn("fake-project", self.br.projects_list)
        self.br.save()
        JenkinsBuildInfo.objects.create(
            job_url="http://fake.local/job/fake-project-repos/",
            projectname="fake-project",
            jobname="fake-project-repos",
            param_tag="UUIDA",
            param_release=self.release,
            param_release_uuid=self.release_uuid,
            buildnumber=1,
            result="SUCCESS",
        )
        JenkinsBuildInfo.objects.create(
            job_url="http://fake.local/job/data-hal-source/",
            projectname="data-hal",
            jobname="data-hal-source",
            param_tag="UUIDA",
            param_release=self.release,
            param_release_uuid=self.release_uuid,
            buildnumber=1,
            result="FAILURE",
        )
        self.br = BuildRelease.objects.get(uuid=self.release_uuid)
        self.assertIn("fake-project", self.br.built_projects_list)
        self.assertIn("data-hal", self.br.failed_projects_list)
        _append, _removed = self.br.refresh_projects()
        self.assertNotIn("fake-project", self.br.projects_list)
        self.assertEqual(_append, ["ngcp-cve-scanner"])
        self.assertEqual(
            _removed,
            [
                "fake-project",
            ],
        )
        self.assertNotIn("fake-project", self.br.projects_list)
        self.assertNotIn("fake-project", self.br.built_projects_list)
        self.assertNotIn("fake-project", self.br.triggered_projects_list)
        self.assertNotIn("fake-project", self.br.failed_projects_list)
        res = JenkinsBuildInfo.objects.filter(
            param_release_uuid=self.release_uuid
        ).count()
        self.assertEqual(1, res)
