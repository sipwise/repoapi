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
from copy import deepcopy
from unittest.mock import MagicMock

from django.test import override_settings

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

    def append_built(self, projectname, size=0):
        self.jbi.projectname = projectname
        self.jbi.jobname = f"{projectname}-repos"
        self.assertTrue(self.br.append_built(self.jbi))
        self.built_projects += f",{projectname}"
        self.assertEqual(self.br.built_projects, self.built_projects)
        self.assertEqual(self.br.pool_size, size)

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

    def append_triggered(self, projectname, size=0):
        self.br.append_triggered(projectname)
        self.assertEqual(self.br.pool_size, size)


@override_settings(BUILD_POOL=4)
class BuildReleaseStepsTest(StepsTest):
    """template was not build_dep and bootenv failed"""

    fixtures = [
        "test_release_steps",
    ]

    build_deps = [
        ["ngcpcfg", "system-tests"],
        ["data-hal", "libswrate", "libtcap", "sipwise-base", "system-tools"],
        ["check-tools", "ngcp-schema"],
        ["ngcp-panel"],
    ]

    def test_status(self):
        self.assertEqual(self.br.built_projects, "release-copy-debs-yml")
        self.assertIsNone(self.br.failed_projects)
        self.assertEqual(self.br.pool_size, 0)

    def test_levels_build_deps(self):
        self.assertEqual(self.br.config.levels_build_deps, self.build_deps)

    def test_next_one_by_one(self):
        self.assertEqual(self.br.next, "ngcpcfg")
        self.append_built("ngcpcfg")
        self.assertEqual(self.br.next, "system-tests")
        self.append_built("system-tests")
        self.assertEqual(self.br.next, "data-hal")
        self.append_built("data-hal")
        self.assertEqual(self.br.next, "libswrate")
        self.append_built("libswrate")

    def test_stop_for_build_deps(self):
        self.assertEqual(self.br.next, "ngcpcfg")
        self.append_built("ngcpcfg")
        self.assertEqual(self.br.next, "system-tests")
        self.append_triggered("system-tests", 1)
        self.assertIsNone(self.br.next)

    def test_stop_for_build_deps_last(self):
        for level in range(3):
            for prj in self.build_deps[level]:
                self.append_built(prj)
        self.assertEqual(self.br.next, "ngcp-panel")
        self.append_triggered("ngcp-panel", 1)
        self.assertIsNone(self.br.next)


class ChangeBuildDepsTest(StepsTest):
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
