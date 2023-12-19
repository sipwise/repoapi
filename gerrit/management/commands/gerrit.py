# Copyright (C) 2023 The Sipwise Team - http://sipwise.com
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
from datetime import date

from django.core.management.base import BaseCommand

from gerrit import tasks


class Command(BaseCommand):
    help = "gerrit actions"

    def add_arguments(self, parser):
        parser.add_argument("action", choices=["refresh", "cleanup"])
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument(
            "--weeks",
            type=int,
            default=6,
            help="filter reviews older than this value in weeks",
        )
        parser.add_argument(
            "--today",
            type=date.fromisoformat,
            default=date.today(),
            help="set today value in isoformat 'YYYY-MM-DD'",
        )

    def refresh(self, *args, **options):
        tasks.refresh(options["dry_run"])

    def cleanup(self, *args, **options):
        tasks.cleanup(
            options["weeks"], options["dry_run"], options["today"].isoformat()
        )

    def handle(self, *args, **options):
        action = getattr(self, options["action"])
        action(*args, **options)
