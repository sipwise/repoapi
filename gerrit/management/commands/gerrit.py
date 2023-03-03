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

from gerrit.utils import get_change_info
from gerrit.utils import get_datetime
from repoapi.models.gri import GerritRepoInfo


class Command(BaseCommand):
    help = "gerrit actions"

    def add_arguments(self, parser):
        parser.add_argument("action", choices=["refresh"])

    def refresh(self, *args, **options):
        qs = GerritRepoInfo.objects.filter(created__date=date(1977, 1, 1))
        for gri in qs.iterator():
            info = get_change_info(gri.gerrit_change)
            gri.created = get_datetime(info["created"])
            gri.modified = get_datetime(info["updated"])
            # don't update modified field on save
            gri.update_modified = False
            gri.save()

    def handle(self, *args, **options):
        action = getattr(self, options["action"])
        action(*args, **options)
