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

from build.models import BuildRelease
from repoapi.test.base import BaseTest


class StepsTest(BaseTest):
    def setUp(self):
        super().setUp()
        self.br = BuildRelease.objects.get(pk=1)
        self.built_projects = deepcopy(self.br.built_projects)
        self.failed_projects = deepcopy(self.br.failed_projects)
        self.jbi = MagicMock()
        self.jbi.result = "SUCCESS"

    def append_built(self, projectname):
        self.jbi.projectname = projectname
        self.jbi.jobname = f"{projectname}-repos"
        self.assertTrue(self.br.append_built(self.jbi))
        self.built_projects += f",{projectname}"
        self.assertEqual(self.br.built_projects, self.built_projects)
        self.assertEqual(self.br.pool_size, 0)

    def append_built_failed(self, projectname):
        self.jbi.projectname = projectname
        self.jbi.jobname = f"{projectname}-repos"
        self.jbi.result = "FAILURE"
        self.assertTrue(self.br.append_built(self.jbi))
        if self.failed_projects:
            self.failed_projects += f",{projectname}"
        else:
            self.failed_projects = f"{projectname}"
        self.assertEqual(self.br.failed_projects, self.failed_projects)


class BuildReleaseStepsTest(StepsTest):
    """template was not build_dep and bootenv failed"""

    fixtures = [
        "test_change_build_deps",
    ]

    def test_status(self):
        self.assertTrue(self.br.config.is_build_dep("templates"))
        self.assertEqual(self.br.failed_projects, "bootenv")

    def test_next_build_deps_changed(self):
        self.assertEqual(self.br.next, "templates")

    def test_next_build_deps_fixed(self):
        self.append_built("templates")
        self.assertEqual(self.br.next, "cdr-exporter")


class BuildReleaseFailureStepsTest(StepsTest):
    """failed build dep... no more builds"""

    fixtures = [
        "test_failed_builds",
    ]

    def test_status(self):
        self.assertTrue(self.br.config.is_build_dep("templates"))
        self.assertTrue(self.br.config.is_build_dep("ngcp-schema"))
        self.assertEqual(self.br.failed_projects, "templates")

    def test_stopped(self):
        self.assertIsNone(self.br.next)

    def test_next_fixed(self):
        self.append_built("templates")
        self.assertEqual(self.br.failed_projects, None)
        self.failed_projects = None
        self.assertEqual(self.br.next, "ngcp-schema")

    def test_failed_non_build_dep(self):
        self.test_next_fixed()
        self.append_built("ngcp-schema")
        self.assertEqual(self.br.next, "asterisk-voicemail")
        self.assertFalse(self.br.config.is_build_dep("asterisk-voicemail"))
        self.append_built_failed("asterisk-voicemail")
        # next will continue
        self.assertEqual(self.br.next, "backup-tools")
