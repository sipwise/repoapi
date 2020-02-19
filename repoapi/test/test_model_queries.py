# Copyright (C) 2015 The Sipwise Team - http://sipwise.com
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
from datetime import datetime
from datetime import timedelta

from django.test import override_settings
from django.utils.dateparse import parse_datetime

from repoapi.models import JenkinsBuildInfo
from repoapi.test.base import BaseTest


@override_settings(DEBUG=True)
class JBIQueriesTestCase(BaseTest):
    fixtures = ["test_model_queries.json"]

    def test_releases(self):
        releases = JenkinsBuildInfo.objects.releases()
        self.assertCountEqual(releases, ["mr3.1-fake"])

    def test_release_projects(self):
        projects = [
            "fake",
        ]
        check = JenkinsBuildInfo.objects.release_projects("mr3.1-fake")
        self.assertCountEqual(check, projects)

    def test_release_project_uuids(self):
        projects = [
            "fake",
        ]
        uuids_ok = dict()
        uuids = dict()

        uuids_ok["fake"] = ["UUID1", "UUID0"]
        for project in projects:
            uuids[project] = JenkinsBuildInfo.objects.release_project_uuids(
                "mr3.1-fake", project
            )
            self.assertCountEqual(uuids_ok[project], uuids[project])

    def test_jobs_by_uuid(self):
        jobs = JenkinsBuildInfo.objects.jobs_by_uuid(
            "mr3.1-fake", "fake", "UUID0"
        )
        self.assertCountEqual(
            JenkinsBuildInfo.objects.filter(
                param_release="mr3.1-fake", projectname="fake", tag="UUID0"
            ),
            jobs,
        )
        jobs = JenkinsBuildInfo.objects.jobs_by_uuid(
            "mr3.1-fake", "fake", "UUID1"
        )
        self.assertCountEqual(
            JenkinsBuildInfo.objects.filter(
                param_release="mr3.1-fake", projectname="fake", tag="UUID1"
            ),
            jobs,
        )

    def test_latest_uuid(self):
        date = parse_datetime("2015-05-04T17:04:57.802Z")
        self.assertEquals(
            JenkinsBuildInfo.objects.latest_uuid("mr3.1-fake", "fake"),
            {"tag": "UUID1", "date": date},
        )

    def test_purge_release(self):
        jbi = JenkinsBuildInfo.objects.get(pk=1)
        jbi.date = datetime.now()
        jbi.save()
        self.assertEquals(JenkinsBuildInfo.objects.count(), 5)
        JenkinsBuildInfo.objects.purge_release(
            "mr3.1-fake", timedelta(weeks=3)
        )
        self.assertEquals(JenkinsBuildInfo.objects.count(), 1)

    def test_purge_release_none(self):
        jbi = JenkinsBuildInfo.objects.get(pk=1)
        jbi.param_release = None
        jbi.save()
        self.assertEquals(
            JenkinsBuildInfo.objects.filter(
                param_release__isnull=True
            ).count(),
            1,
        )
        self.assertEquals(JenkinsBuildInfo.objects.count(), 5)
        JenkinsBuildInfo.objects.purge_release(None, timedelta(weeks=3))
        self.assertEquals(JenkinsBuildInfo.objects.count(), 4)


@override_settings(DEBUG=True)
class JBIQueriesUUIDTest(BaseTest):
    fixtures = ["test_model_queries_uuid.json"]
    release = "release-mr8.1"
    release_uuid = "UUID_mr8.1"

    def test_release_projects(self):
        projects = [
            "kamailio",
        ]
        check = JenkinsBuildInfo.objects.release_projects(
            self.release, release_uuid=self.release_uuid
        )
        self.assertCountEqual(check, projects)

    def test_release_project_uuids(self):
        projects = [
            "kamailio",
        ]
        uuids_ok = dict()
        uuids = dict()

        uuids_ok["kamailio"] = ["UUID1", "UUID0"]
        for project in projects:
            uuids[project] = JenkinsBuildInfo.objects.release_project_uuids(
                self.release, project, release_uuid=self.release_uuid
            )
            self.assertCountEqual(uuids_ok[project], uuids[project])

    def test_jobs_by_uuid(self):
        jobs = JenkinsBuildInfo.objects.jobs_by_uuid(
            self.release, "kamailio", "UUID0"
        )
        jbi_list = JenkinsBuildInfo.objects.filter(
            param_release=self.release,
            projectname="kamailio",
            tag="UUID0",
            param_release_uuid=self.release_uuid,
        )
        self.assertCountEqual(jbi_list, jobs)
        jbi_list = JenkinsBuildInfo.objects.filter(
            param_release=self.release,
            projectname="kamailio",
            tag="UUID1",
            param_release_uuid=self.release_uuid,
        )
        jobs = JenkinsBuildInfo.objects.jobs_by_uuid(
            self.release, "kamailio", "UUID1", release_uuid=self.release_uuid
        )
        self.assertCountEqual(jbi_list, jobs)

    def test_latest_uuid(self):
        date = parse_datetime("2015-05-04T17:04:57.802Z")
        self.assertEquals(
            JenkinsBuildInfo.objects.latest_uuid(
                self.release, "kamailio", release_uuid=self.release_uuid
            ),
            {"tag": "UUID1", "date": date},
        )
