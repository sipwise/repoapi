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
from unittest.mock import call
from unittest.mock import patch

from django.test import override_settings

from build.models import BuildRelease
from repoapi.models import JenkinsBuildInfo
from repoapi.test.base import BaseTest


@override_settings(JBI_ALLOWED_HOSTS=["fake.local"])
@patch("repoapi.utils.dlfile")
@patch("build.tasks.trigger_build")
class JBIManageTest(BaseTest):
    fixtures = [
        "test_models",
    ]
    release = "release-mr8.1"
    release_uuid = "dbe569f7-eab6-4532-a6d1-d31fb559648b"

    def test_jbi_manage_ok_release_job(self, tb, dl):
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
            "project": "data-hal-get-code",
            "release_uuid": br.uuid,
            "trigger_release": br.release,
            "trigger_branch_or_tag": br.branch_or_tag,
            "trigger_distribution": br.distribution,
        }
        tb.assert_called_once_with(**params)
        br = BuildRelease.objects.get(uuid=self.release_uuid)
        self.assertEqual(br.pool_size, 1)
        self.assertEqual(br.triggered_projects, "data-hal")

    @override_settings(BUILD_POOL=2)
    def test_jbi_manage_pool(self, tb, dl):
        br = BuildRelease.objects.get(uuid=self.release_uuid)
        self.assertEqual(br.pool_size, 0)
        JenkinsBuildInfo.objects.create(
            job_url="http://fake.local/job/release-copy-debs-yml/",
            projectname="release-copy-debs-yml",
            jobname="release-copy-debs-yml",
            tag="UUIDA",
            param_release="mr8.1",
            param_release_uuid=self.release_uuid,
            buildnumber=1,
            result="SUCCESS",
        )
        br = BuildRelease.objects.get(id=br.pk)
        self.assertEqual(br.built_projects, "release-copy-debs-yml")
        params = {
            "project": "data-hal-get-code",
            "release_uuid": br.uuid,
            "trigger_release": br.release,
            "trigger_branch_or_tag": br.branch_or_tag,
            "trigger_distribution": br.distribution,
        }
        calls = [call(**params)]
        params["project"] = "libinewrate-get-code"
        calls.append(call(**params))
        tb.assert_has_calls(calls)
        br = BuildRelease.objects.get(pk=br.pk)
        self.assertEqual(br.pool_size, 2)
        self.assertEqual(br.triggered_projects, "data-hal,libinewrate")

    @override_settings(BUILD_POOL=2)
    def test_jbi_manage_pool_building(self, tb, dl):
        self.test_jbi_manage_pool()
        br = BuildRelease.objects.get(uuid=self.release_uuid)
        self.assertEqual(br.pool_size, 2)
        JenkinsBuildInfo.objects.create(
            job_url="http://fake.local/job/data-hal-binaries/",
            projectname="data-hal",
            jobname="data-hal-binaries",
            tag="UUIDA",
            param_release=self.release,
            param_release_uuid=self.release_uuid,
            buildnumber=1,
            result="SUCCESS",
        )
        br = BuildRelease.objects.get(id=br.pk)
        self.assertEqual(br.pool_size, 2)
        self.assertEqual(br.triggered_projects, "data-hal,libinewrate")
        JenkinsBuildInfo.objects.create(
            job_url="http://fake.local/job/libinewrate-binaries/",
            projectname="libinewrate",
            jobname="libinewrate-binaries",
            tag="UUIDA",
            param_release=self.release,
            param_release_uuid=self.release_uuid,
            buildnumber=1,
            result="SUCCESS",
        )
        br = BuildRelease.objects.get(pk=br.pk)
        self.assertEqual(br.pool_size, 2)
        self.assertEqual(br.triggered_projects, "data-hal,libinewrate")

    @override_settings(BUILD_POOL=2)
    def test_jbi_manage_pool_next(self, tb, dl):
        self.test_jbi_manage_pool()
        br = BuildRelease.objects.get(uuid=self.release_uuid)
        self.assertEqual(br.pool_size, 2)
        JenkinsBuildInfo.objects.create(
            job_url="http://fake.local/job/data-hal-repos/",
            projectname="data-hal",
            jobname="data-hal-repos",
            tag="UUIDA",
            param_release=self.release,
            param_release_uuid=self.release_uuid,
            buildnumber=1,
            result="SUCCESS",
        )
        br = BuildRelease.objects.get(pk=br.pk)
        self.assertEqual(br.built_projects, "release-copy-debs-yml,data-hal")
        params = {
            "project": "libswrate-get-code",
            "release_uuid": br.uuid,
            "trigger_release": br.release,
            "trigger_branch_or_tag": br.branch_or_tag,
            "trigger_distribution": br.distribution,
        }
        tb.assert_called_once_with(**params)
        self.assertEqual(br.pool_size, 2)
        self.assertEqual(br.triggered_projects, "libinewrate,libswrate")

    @override_settings(BUILD_POOL=3)
    def test_jbi_manage_pool_deps(self, tb, dl):
        br = BuildRelease.objects.get(uuid=self.release_uuid)
        self.assertEqual(br.pool_size, 0)
        JenkinsBuildInfo.objects.create(
            job_url="http://fake.local/job/release-copy-debs-yml/",
            projectname="release-copy-debs-yml",
            jobname="release-copy-debs-yml",
            tag="UUIDA",
            param_release="mr8.1",
            param_release_uuid=self.release_uuid,
            buildnumber=1,
            result="SUCCESS",
        )
        params = {
            "project": "data-hal-get-code",
            "release_uuid": br.uuid,
            "trigger_release": br.release,
            "trigger_branch_or_tag": br.branch_or_tag,
            "trigger_distribution": br.distribution,
        }
        calls = [call(**params)]
        params["project"] = "libinewrate-get-code"
        calls.append(call(**params))
        params["project"] = "libswrate-get-code"
        calls.append(call(**params))
        tb.assert_has_calls(calls)

        JenkinsBuildInfo.objects.create(
            job_url="http://fake.local/job/data-hal-repos/",
            projectname="data-hal",
            jobname="data-hal-repos",
            tag="UUIDA",
            param_release=self.release,
            param_release_uuid=self.release_uuid,
            buildnumber=1,
            result="SUCCESS",
        )
        params["project"] = "libtcap-get-code"
        tb.assert_called_with(**params)

        JenkinsBuildInfo.objects.create(
            job_url="http://fake.local/job/libswrate-repos/",
            projectname="libswrate",
            jobname="libswrate-repos",
            tag="UUIDA",
            param_release=self.release,
            param_release_uuid=self.release_uuid,
            buildnumber=1,
            result="SUCCESS",
        )
        params["project"] = "sipwise-base-get-code"
        tb.assert_called_with(**params)

        JenkinsBuildInfo.objects.create(
            job_url="http://fake.local/job/libinewrate-repos/",
            projectname="libinewrate",
            jobname="libinewrate-repos",
            tag="UUIDA",
            param_release=self.release,
            param_release_uuid=self.release_uuid,
            buildnumber=1,
            result="SUCCESS",
        )
        br = BuildRelease.objects.get(uuid=self.release_uuid)
        self.assertEqual(
            br.triggered_projects, "libtcap,sipwise-base,check-tools"
        )
        params["project"] = "check-tools-get-code"
        tb.assert_called_with(**params)
        tb.reset_mock()

        JenkinsBuildInfo.objects.create(
            job_url="http://fake.local/job/libtcap-repos/",
            projectname="libtcap",
            jobname="libtcap-repos",
            tag="UUIDA",
            param_release=self.release,
            param_release_uuid=self.release_uuid,
            buildnumber=1,
            result="SUCCESS",
        )
        br = BuildRelease.objects.get(uuid=self.release_uuid)
        self.assertEqual(br.triggered_projects, "sipwise-base,check-tools")
        tb.assert_not_called()

        JenkinsBuildInfo.objects.create(
            job_url="http://fake.local/job/check-tools-repos/",
            projectname="check-tools",
            jobname="check-tools-repos",
            tag="UUIDA",
            param_release=self.release,
            param_release_uuid=self.release_uuid,
            buildnumber=1,
            result="SUCCESS",
        )
        br = BuildRelease.objects.get(uuid=self.release_uuid)
        self.assertEqual(br.triggered_projects, "sipwise-base")
        tb.assert_not_called()

        JenkinsBuildInfo.objects.create(
            job_url="http://fake.local/job/sipwise-base-repos/",
            projectname="sipwise-base",
            jobname="sipwise-base-repos",
            tag="UUIDA",
            param_release=self.release,
            param_release_uuid=self.release_uuid,
            buildnumber=1,
            result="SUCCESS",
        )
        br = BuildRelease.objects.get(uuid=self.release_uuid)
        self.assertEqual(br.triggered_projects, "ngcp-schema")
        params["project"] = "ngcp-schema-get-code"
        tb.assert_called_with(**params)


@override_settings(JBI_ALLOWED_HOSTS=["fake.local"])
@patch("repoapi.utils.dlfile")
@patch("build.tasks.trigger_build")
@patch("build.tasks.trigger_build_matrix")
class WeeklyTest(BaseTest):
    fixtures = [
        "test_weekly",
    ]
    release = "release-trunk-weekly"
    release_uuid = "dbe569f7-eab6-4532-a6d1-d31fb559649b"

    @override_settings(BUILD_POOL=2)
    def test_jbi_manage_trigger_matrix(self, tbm, tb, dl):
        br = BuildRelease.objects.get(uuid=self.release_uuid)
        JenkinsBuildInfo.objects.create(
            job_url="http://fake.local/job/ngcp-prompts-repos/",
            projectname="ngcp-prompts",
            jobname="ngcp-prompts-repos",
            tag="UUIDA",
            param_release=self.release,
            param_release_uuid=self.release_uuid,
            buildnumber=1,
            result="SUCCESS",
        )
        br = BuildRelease.objects.get(pk=br.pk)
        self.assertTrue(br.built_projects.endswith("ngcp-prompts"))
        self.assertEqual(br.pool_size, 0)
        tb.assert_not_called()
        tbm.assert_called_once_with()
