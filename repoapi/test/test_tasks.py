# Copyright (C) 2017-2020 The Sipwise Team - http://sipwise.com
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
from copy import deepcopy
from datetime import datetime
from os.path import join
from unittest.mock import patch

from django.test import override_settings
from django.utils.timezone import make_aware

from repoapi import tasks
from repoapi.conf import settings
from repoapi.models import GerritRepoInfo
from repoapi.models import JenkinsBuildInfo
from repoapi.test.base import BaseTest

FIXTURES_PATH = join(settings.BASE_DIR, "repoapi", "fixtures", "jbi_files")


class TasksTestCase(BaseTest):
    fixtures = ["test_model_queries.json"]

    def test_purge(self):
        prev_count = JenkinsBuildInfo.objects.count()
        jbi = JenkinsBuildInfo.objects.get(pk=1)
        jbi.date = make_aware(datetime.now())
        jbi.save()
        self.assertEqual(JenkinsBuildInfo.objects.count(), prev_count)
        tasks.jbi_purge.delay("mr3.1-fake", 3)
        self.assertEqual(JenkinsBuildInfo.objects.count(), 1)

    def test_purge_none(self):
        prev_count = JenkinsBuildInfo.objects.count()
        jbi = JenkinsBuildInfo.objects.get(pk=1)
        jbi.param_release = None
        jbi.save()
        self.assertEqual(
            JenkinsBuildInfo.objects.filter(
                param_release__isnull=True
            ).count(),
            1,
        )
        self.assertEqual(JenkinsBuildInfo.objects.count(), prev_count)
        tasks.jbi_purge.delay(None, 3)
        self.assertEqual(JenkinsBuildInfo.objects.count(), prev_count - 1)


@override_settings(JBI_BASEDIR=FIXTURES_PATH)
@patch("repoapi.tasks.jenkins_remove_project_ppa")
@patch("repoapi.utils.jenkins_remove_ppa")
class TaskGerritRepoTest(BaseTest):
    default_params = {
        "gerrit_patchset": "44323",
        "gerrit_change": "44323",
        "gerrit_eventtype": "patchset-created",
        "tag": "de13c0b6-2e70-4c9d-b3a5-3a476149d2d1",
        "projectname": "lua-ngcp-kamailio",
        "git_commit_msg": "TT#95650 mocks/pv: ",
        "job_url": "https://fake/job/lua-ngcp-kamailio-repos/",
        "buildnumber": 605,
        "jobname": "lua-ngcp-kamailio-repos",
        "result": "SUCCESS",
        "param_tag": "none",
        "param_branch": "master",
        "param_release": "none",
        "param_release_uuid": "",
        "param_distribution": "buster",
        "param_ppa": "gerrit_vseva_95650",
    }

    def setUp(self, *args, **kwargs):
        super(TaskGerritRepoTest, self).setUp(*args, **kwargs)
        self.params = deepcopy(self.default_params)

    def tearDown(self, *args, **kwargs):
        pass  # don't remove FIXTURES_PATH

    def test_ppa_created(self, rppa, rp):
        jbi = JenkinsBuildInfo.objects.create(**self.params)
        self.assertIsNotNone(jbi.source)
        rp.assert_not_called()
        rppa.assert_not_called()

    def test_ppa_created_failed(self, rppa, rp):
        self.params["result"] = "FAILED"
        jbi = JenkinsBuildInfo.objects.create(**self.params)
        self.assertIsNotNone(jbi.source)
        rp.assert_not_called()
        rppa.assert_not_called()

    def test_repo_not_ppa(self, rppa, rp):
        self.params["param_ppa"] = "$ppa"
        JenkinsBuildInfo.objects.create(**self.params)
        rp.assert_not_called()
        rppa.assert_not_called()

    def test_not_repo_job(self, rppa, rp):
        self.params["jobname"] = "lua-ngcp-kamailio-binaries"
        JenkinsBuildInfo.objects.create(**self.params)
        rp.assert_not_called()
        rppa.assert_not_called()

    def test_ppa_merged_just_one_review(self, rppa, rp):
        self.params["gerrit_eventtype"] = "change-merged"
        jbi = JenkinsBuildInfo.objects.create(**self.params)
        self.assertIsNotNone(jbi.source)
        rp.assert_not_called()
        rppa.assert_called_with("gerrit_vseva_95650")

    def test_ppa_merged_multiple_just_one_project(self, rppa, rp):
        ppa = GerritRepoInfo.objects.filter(param_ppa=self.params["param_ppa"])
        self.assertEqual(ppa.count(), 0)

        JenkinsBuildInfo.objects.create(**self.params)
        self.assertEqual(ppa.count(), 1)

        self.params["gerrit_change"] = "54"
        self.params["gerrit_patchset"] = "54"
        JenkinsBuildInfo.objects.create(**self.params)
        self.assertEqual(ppa.count(), 2)

        self.params = deepcopy(self.default_params)
        self.params["gerrit_eventtype"] = "change-merged"
        jbi = JenkinsBuildInfo.objects.create(**self.params)
        self.assertIsNotNone(jbi.source)
        self.assertEqual(ppa.count(), 1)
        rp.assert_not_called()
        rppa.assert_not_called()

    def test_ppa_cleaned(self, rppa, rp):
        self.test_ppa_merged_multiple_just_one_project()
        # be sure that the PPA is removed when all reviews merged
        self.params["gerrit_change"] = "54"
        self.params["gerrit_patchset"] = "54"
        self.params["gerrit_eventtype"] = "change-merged"
        JenkinsBuildInfo.objects.create(**self.params)
        rp.assert_not_called()
        rppa.assert_called_with("gerrit_vseva_95650")

    def _prepare(self):
        ppa = GerritRepoInfo.objects.filter(param_ppa=self.params["param_ppa"])
        self.assertEqual(ppa.count(), 0)

        self.params["gerrit_change"] = "54"
        self.params["gerrit_patchset"] = "54"
        self.params["projectname"] = "vmnotify"
        self.params["jobname"] = "vmnotify-repos"
        JenkinsBuildInfo.objects.create(**self.params)
        self.assertEqual(ppa.count(), 1)

        self.params = deepcopy(self.default_params)
        JenkinsBuildInfo.objects.create(**self.params)
        self.assertEqual(ppa.count(), 2)
        return ppa

    def test_ppa_merged_more_reviews_open_same_project(self, rppa, rp):
        ppa = self._prepare()
        ppa_project = ppa.filter(projectname=self.params["projectname"])
        self.assertEqual(ppa_project.count(), 1)

        self.params["gerrit_change"] = "545"
        self.params["gerrit_patchset"] = "545"
        JenkinsBuildInfo.objects.create(**self.params)
        self.assertEqual(ppa.count(), 3)
        self.assertEqual(ppa_project.count(), 2)

        self.params["gerrit_eventtype"] = "change-merged"
        jbi = JenkinsBuildInfo.objects.create(**self.params)
        self.assertIsNotNone(jbi.source)
        self.assertEqual(ppa.count(), 2)
        self.assertEqual(ppa_project.count(), 1)
        rp.assert_not_called()
        rppa.assert_not_called()

    def test_ppa_merged_multiple_more_reviews_open(self, rppa, rp):
        ppa = self._prepare()

        self.params["gerrit_eventtype"] = "change-merged"
        jbi = JenkinsBuildInfo.objects.create(**self.params)
        self.assertIsNotNone(jbi.source)
        self.assertEqual(ppa.count(), 1)
        rp.assert_called_once_with("gerrit_vseva_95650", "lua-ngcp-kamailio")
        rppa.assert_not_called()
