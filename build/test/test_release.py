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
from copy import deepcopy
from unittest.mock import MagicMock

from django.test import override_settings
from django.test import TestCase

from build.models import BuildRelease


@override_settings(DEBUG=True)
class BuildReleaseStepsTest(TestCase):
    fixtures = [
        "test_change_build_deps",
    ]

    def setUp(self):
        self.br = BuildRelease.objects.get(pk=1)
        self.built_projects = deepcopy(self.br.built_projects)
        self.jbi = MagicMock()
        self.jbi.result = "SUCCESS"

    def test_stopped(self):
        self.test_append_built()
        self.assertIsNone(self.br.next)

    def test_append_built(self):
        self.jbi.projectname = "templates"
        self.jbi.jobname = "templates-repos"
        self.assertTrue(self.br.append_built(self.jbi))
        self.built_projects += ",templates"
        self.assertEqual(self.br.built_projects, self.built_projects)
        self.assertEqual(self.br.pool_size, 0)

    def test_next_build_deps_changed(self):
        self.assertEqual(self.br.next, "templates")

    def test_next_retrigger(self):
        self.test_append_built()
        self.jbi.projectname = "bootenv"
        self.jbi.jobname = "{}-repos".format(self.jbi.projectname)
        self.assertTrue(self.br.append_built(self.jbi))
        self.assertIsNotNone(self.br.next)
