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
from datetime import datetime
from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from requests.exceptions import HTTPError

from gerrit.utils import get_change_info
from gerrit.utils import get_datetime
from repoapi.models.gri import GerritRepoInfo


class Command(BaseCommand):
    help = "gerrit actions"

    def add_arguments(self, parser):
        parser.add_argument("action", choices=["refresh", "cleanup"])
        parser.add_argument("--dry-run", type=bool, default=False)
        parser.add_argument(
            "--weeks",
            type=int,
            default=6,
            help="filter reviews older than this value in weeks",
        )
        parser.add_argument(
            "--today",
            type=date.fromisoformat,
            default=datetime.today(),
            help="set today value in isoformat 'YYYY-MM-DD'",
        )

    def refresh(self, *args, **options):
        qs = GerritRepoInfo.objects.filter(created__date=date(1977, 1, 1))
        for gri in qs.iterator():
            try:
                info = get_change_info(gri.gerrit_change)
                gri.created = get_datetime(info["created"])
                gri.modified = get_datetime(info["updated"])
                # don't update modified field on save
                gri.update_modified = False
                if options["dry_run"]:
                    self.stdout.write(
                        f"{gri} would be changed to "
                        f" created:{gri.created}"
                        f" modified:{gri.modified}"
                    )
                else:
                    gri.save()
            except HTTPError:
                self.stderr.write(f"{gri} not found, remove it from db")
                gri.delete()

    def cleanup(self, *args, **options):
        max_date = options["today"] - timedelta(weeks=options["weeks"])
        self.stderr.write(f"max_date:{max_date}")
        if settings.DEBUG:
            self.stderr.write("debug ON")
        manager = GerritRepoInfo.objects
        qs = manager.filter(modified__lt=max_date)
        for gri in qs.iterator():
            info = get_change_info(gri.gerrit_change)
            if info["status"] == "MERGED":
                if options["dry_run"]:
                    self.stdout.write(
                        f"{gri} merged, remove from db, [dry-run]"
                    )
                else:
                    self.stdout.write(f"{gri} merged, remove from db")
                    manager.review_removed(
                        gri.param_ppa, gri.gerrit_change, gri.projectname
                    )

    def handle(self, *args, **options):
        action = getattr(self, options["action"])
        action(*args, **options)
