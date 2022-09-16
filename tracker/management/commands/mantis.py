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
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from tracker.utils import mantis_get_issue
from tracker.utils import mantis_get_issue_id
from tracker.utils import mantis_get_target_releases
from tracker.utils import mantis_set_release_target


class Command(BaseCommand):
    help = "mantis API helper"

    def add_arguments(self, parser):
        parser.add_argument(
            "command",
            choices=["get-issue", "set-target-release", "get-target-release"],
        )
        parser.add_argument("--mantis-id", type=int)
        parser.add_argument("--value", type=str)
        parser.add_argument("--force", action="store_true", default=False)

    def get_mantis_id(self, **options):
        if options["mantis_id"] is None:
            raise CommandError("--mantis-id missing")
        return options["mantis_id"]

    def handle(self, *args, **options):
        if options["command"] == "get-issue":
            mantis_id = self.get_mantis_id(**options)
            issue = mantis_get_issue(mantis_id)
            self.stdout.write(f"{issue}")
        elif options["command"] == "get-target-release":
            mantis_id = self.get_mantis_id(**options)
            issue = mantis_get_issue(mantis_id)
            releases = mantis_get_target_releases(issue)
            self.stdout.write(f"{releases}")
        elif options["command"] == "set-target-release":
            mantis_id = self.get_mantis_id(**options)
            if options["value"] is None:
                raise CommandError("--value missing")
            res = mantis_set_release_target(
                mantis_id, options["value"], options["force"]
            )
            if res:
                issue = mantis_get_issue_id(res.json(), mantis_id)
                releases = mantis_get_target_releases(issue)
                self.stdout.write(f"{releases}")
            else:
                self.stdout.write("value already in target_release")
