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

from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class TestRest(APITestCase):

    def setUp(self):
        self.url = dict()
        self.url['jbi'] = reverse('jenkinsbuildinfo-list')

    def test_jbi_creation(self):
        data = {"url": "http://127.0.0.1:8000/jenkinsbuildinfo/1/",
                "projectname": "fake",
                "jobname": "fake-get-code",
                "buildnumber": 1,
                "result": "OK",
                "job_url": "http://fake.org/gogo", }
        data_all = {
            "url": "http://testserver/jenkinsbuildinfo/1/",
            "tag": None,
            "projectname": "fake",
            "jobname": "fake-get-code",
            "buildnumber": 1,
            "result": "OK",
            "job_url": "http://fake.org/gogo",
            "gerrit_patchset": None,
            "gerrit_change": None,
            "gerrit_eventtype": None,
            "param_tag": None,
            "param_branch": None,
            "param_release": None,
            "param_distribution": None,
            "param_ppa": None,
            "repo_name": None,
            "git_commit_msg": None
        }
        response = self.client.post(self.url['jbi'], data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data_all['date'] = response.data['date']
        self.assertEqual(response.data, data_all)
