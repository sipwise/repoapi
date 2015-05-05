# Copyright (C) 2015 The Sipwise Team - http://sipwise.com

# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.

# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

from django.test import TestCase
from repoapi.models import JenkinsBuildInfo


class JBIQueriesTestCase(TestCase):
    fixtures = ['test_model_queries.json']

    def test_releases(self):
        releases = JenkinsBuildInfo.objects.releases()
        self.assertItemsEqual(releases, ['mr3.1-fake', ])

    def test_release_uuids_by_project(self):
        projects = ['fake', ]
        uuids_ok = dict()
        uuids = dict()

        uuids_ok['fake'] = ['UUID1', 'UUID0']
        for p in projects:
            uuids[p] = JenkinsBuildInfo.objects.release_uuids_by_project(
                'mr3.1-fake', p)
            self.assertItemsEqual(uuids_ok[p], uuids[p])

    def test_projects_by_uuid(self):
        projects = JenkinsBuildInfo.objects.projects_by_uuid(
            'mr3.1-fake', 'fake', 'UUID0')
        self.assertItemsEqual(['fake-get-code', ], projects)
        projects = JenkinsBuildInfo.objects.projects_by_uuid(
            'mr3.1-fake', 'fake', 'UUID1')
        self.assertItemsEqual(
            ['fake-get-code', 'fake-source-tests', 'fake-source'], projects)
