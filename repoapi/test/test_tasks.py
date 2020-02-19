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
from datetime import datetime

from repoapi import tasks
from repoapi.models import JenkinsBuildInfo
from repoapi.test.base import BaseTest


class TasksTestCase(BaseTest):
    fixtures = ["test_model_queries.json"]

    def test_purge(self):
        jbi = JenkinsBuildInfo.objects.get(pk=1)
        jbi.date = datetime.now()
        jbi.save()
        self.assertEquals(JenkinsBuildInfo.objects.count(), 5)
        tasks.jbi_purge.delay("mr3.1-fake", 3)
        self.assertEquals(JenkinsBuildInfo.objects.count(), 1)

    def test_purge_none(self):
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
        tasks.jbi_purge.delay(None, 3)
        self.assertEquals(JenkinsBuildInfo.objects.count(), 4)
