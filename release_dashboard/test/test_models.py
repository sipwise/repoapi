# Copyright (C) 2016 The Sipwise Team - http://sipwise.com

# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.

# You should have received a copy of the GNU General Public License along
# with this prograproj.  If not, see <http://www.gnu.org/licenses/>.
import copy
from django.test import TestCase
from release_dashboard.models import Project

GERRIT_REST_TAGS = """
)]}'
[
  {
    "ref": "refs/tags/mr2.0.0"
  },
  {
    "ref": "refs/tags/mr1.0.0"
  }
]
"""
FILTERED_TAGS = [
    {
        "ref": "refs/tags/mr2.0.0"
    },
    {
        "ref": "refs/tags/mr1.0.0"
    }
]
GERRIT_REST_BRANCHES = """
)]}'
[
  {
    "ref": "refs/heads/master"
  },
  {
    "ref": "refs/heads/vseva/1789"
  }
]
"""
FILTERED_BRANCHES = [
    {
        "ref": "refs/heads/master"
    },
    {
        "ref": "refs/heads/vseva/1789"
    }
]


class ProjectTestCase(TestCase):

    def test_create(self):
        proj = Project.objects.create(name="fake")
        self.assertCountEqual(proj.name, "fake")

    def test_tags(self):
        proj = Project.objects.create(name="fake", json_tags=FILTERED_TAGS)
        self.assertCountEqual(proj.name, "fake")
        self.assertIsInstance(proj.tags, list)
        self.assertItemsEqual(proj.tags, ["mr2.0.0", "mr1.0.0", ])

    def test_tags_null(self):
        proj = Project.objects.create(name="fake")
        self.assertCountEqual(proj.name, "fake")
        self.assertIsInstance(proj.tags, list)
        self.assertItemsEqual(proj.tags, [])

    def test_branches(self):
        proj = Project.objects.create(name="fake",
                                      json_branches=FILTERED_BRANCHES)
        self.assertCountEqual(proj.name, "fake")
        self.assertIsInstance(proj.branches, list)
        self.assertItemsEqual(proj.branches, ["vseva/1789", "master"])

    def test_branches_null(self):
        proj = Project.objects.create(name="fake")
        self.assertCountEqual(proj.name, "fake")
        self.assertIsInstance(proj.branches, list)
        self.assertItemsEqual(proj.branches, [])

    def test_filtered_json(self):
        res = Project._get_filtered_json(GERRIT_REST_TAGS)
        self.assertCountEqual(res, FILTERED_TAGS)

    def test_filter_values(self):
        values = copy.deepcopy(FILTERED_TAGS)
        res = Project._filter_values(FILTERED_TAGS, '^refs/tags/(.+)$')
        self.assertCountEqual(res, ['mr2.0.0', 'mr1.0.0'])
        values.append({"ref": "no/no"})
        res = Project._filter_values(values, '^refs/tags/(.+)$')
        self.assertCountEqual(res, ['mr2.0.0', 'mr1.0.0'])

    def test_filter_values_regex(self):
        values = copy.deepcopy(FILTERED_TAGS)
        res = Project._filter_values(FILTERED_TAGS, '^refs/tags/(.+)$',
                                     r'^mr[0-9]+\.[0-9]+\.[0-9]+$')
        self.assertCountEqual(res, ['mr2.0.0', 'mr1.0.0'])
        values.append({"ref": "refs/tags/3.7.8"})
        res = Project._filter_values(values, '^refs/tags/(.+)$',
                                     r'^mr[0-9]+\.[0-9]+\.[0-9]+$')
        self.assertCountEqual(res, ['mr2.0.0', 'mr1.0.0'])
        res = Project._filter_values(values, '^refs/tags/(.+)$',
                                     r'^[0-9]+\.[0-9]+\.[0-9]+$')
        self.assertCountEqual(res, ['3.7.8'])

    def test_tags_set(self):
        proj = Project.objects.create(name="fake")
        self.assertCountEqual(proj.name, "fake")
        self.assertIsInstance(proj.tags, list)
        self.assertItemsEqual(proj.tags, [])
        proj.tags = GERRIT_REST_TAGS
        self.assertItemsEqual(proj.tags, ["mr2.0.0", "mr1.0.0"])

    def test_branches_set(self):
        proj = Project.objects.create(name="fake")
        self.assertCountEqual(proj.name, "fake")
        self.assertIsInstance(proj.branches, list)
        self.assertItemsEqual(proj.branches, [])
        proj.branches = GERRIT_REST_BRANCHES
        self.assertItemsEqual(proj.branches, ["master", "vseva/1789"])

    def test_branches_mrXX(self):
        tmp = [
            {"ref": "refs/heads/master"},
            {"ref": "refs/heads/mr0.1"},
            {"ref": "refs/heads/mr0.1.1"},
            {"ref": "refs/heads/vseva/nono"},
        ]
        proj = Project.objects.create(name="fake",
                                      json_branches=tmp)
        self.assertCountEqual(proj.name, "fake")
        self.assertItemsEqual(proj.branches_mrXX(),
                              ["mr0.1", ])

    def test_branches_mrXXX(self):
        tmp = [
            {"ref": "refs/heads/master"},
            {"ref": "refs/heads/mr0.1"},
            {"ref": "refs/heads/mr0.1.1"},
            {"ref": "refs/heads/vseva/nono"},
        ]
        proj = Project.objects.create(name="fake",
                                      json_branches=tmp)
        self.assertCountEqual(proj.name, "fake")
        self.assertItemsEqual(proj.branches_mrXXX(),
                              ["mr0.1.1", ])
