# Copyright (C) 2022 The Sipwise Team - http://sipwise.com
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
from tempfile import NamedTemporaryFile

from django.core.management import call_command
from django.core.management.base import CommandError

from repoapi.conf import settings
from repoapi.models import JenkinsBuildInfo
from repoapi.test import check_output
from repoapi.test.base import BaseTest

FIXTURES_PATH = settings.BASE_DIR.joinpath("repoapi", "fixtures")


class exportJBITest(BaseTest):
    fixtures = ["test_commands"]
    uuid = "16726366-93fa-4050-91fd-d496bf9acabf"

    def setUp(self):
        self.cmd = [
            "dumpdata_release",
        ]

    def test_no_params(self):
        with self.assertRaises(CommandError):
            call_command(*self.cmd)

    def test_wrong_uuid(self):
        with self.assertRaises(CommandError):
            with NamedTemporaryFile() as fp:
                self.cmd.append("wrong_uuid")
                self.cmd.append(fp.name)
                call_command(*self.cmd)

    def test_ok(self):
        qs = JenkinsBuildInfo.objects.filter(param_release_uuid=self.uuid)
        self.assertTrue(qs.count() > 0)

        checkfile = FIXTURES_PATH.joinpath("export.yml")
        with NamedTemporaryFile() as fp:
            self.cmd.append(self.uuid)
            self.cmd.append(fp.name)
            call_command(*self.cmd)
            check_output(fp.name, f"{checkfile}")


class apikeyTest(BaseTest):
    key = "bF5FPwbD.twrKaUDTqYck7gKu7G1EeKUCOSehU5MX"
    hashed_key = (
        "pbkdf2_sha256$260000$0r1aVevuWiB53I"
        "Mr9dTWOO$oJwAul49UovnNVybhIAisO8gTNiSv/GxDBWo9hfH+Tk="
    )

    def setUp(self):
        self.cmd = [
            "apikey",
        ]

    def test_no_params(self):
        with self.assertRaises(CommandError):
            call_command(*self.cmd)

    def test_verify_ko(self):
        self.cmd.append("verify")
        self.cmd.append("--value")
        self.cmd.append(self.hashed_key)
        self.cmd.append("--key")
        self.cmd.append("noNo")
        with self.assertRaises(CommandError):
            call_command(*self.cmd)

    def test_verify_ok(self):
        self.cmd.append("verify")
        self.cmd.append("--value")
        self.cmd.append(self.hashed_key)
        self.cmd.append("--key")
        self.cmd.append(self.key)
        call_command(*self.cmd)

    def test_hash_ok(self):
        self.cmd.append("hash")
        self.cmd.append("--value")
        self.cmd.append(self.key)
        call_command(*self.cmd)
