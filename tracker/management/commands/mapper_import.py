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
import sqlite3
from itertools import islice
from pathlib import Path

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from tablib import Dataset

from tracker.admin import TrackerMapperResource
from tracker.conf import MapperType


class Command(BaseCommand):
    help = "import WF to Mantis mapper info"
    headers = ("workfront_uuid", "workfront_id", "mantis_id", "mapper_type")

    def add_arguments(self, parser):
        parser.add_argument("file", type=lambda p: Path(p).absolute())

    def get_dataset(self, _type, max_rows=100):
        for row in islice(self.cur, max_rows):
            self.data.append([row[0], row[1], row[2], _type])

    def handle(self, *args, **options):
        resource = TrackerMapperResource()
        # resource.get_queryset().all().delete()
        self.data = Dataset(headers=self.headers)
        con = sqlite3.connect(options["file"])
        self.cur = con.execute(
            "SELECT wf_id, wf_ticket, mt_ticket FROM mapper_issues"
        )
        self.get_dataset(MapperType.ISSUE, None)
        self.cur = con.execute(
            "SELECT wf_id, wf_ticket, mt_ticket FROM mapper_tasks"
        )
        self.get_dataset(MapperType.TASK, None)
        result = resource.import_data(
            self.data, raise_errors=True, use_transactions=True
        )
        if result.has_errors():
            raise CommandError("error importing data")
        self.stdout.write(
            self.style.SUCCESS(f"Successfully imported {result.totals}")
        )
        con.close()
