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
import argparse

from django.core.management.base import BaseCommand
from tablib import Dataset

from repoapi.admin import JenkinsBuildInfoResource


class Command(BaseCommand):
    help = "import BuildRelease info"

    def add_arguments(self, parser):
        parser.add_argument(
            "--format", choices=["json", "yaml"], default="yaml"
        )
        parser.add_argument("file", type=argparse.FileType("r"))

    def handle(self, *args, **options):
        jbi = JenkinsBuildInfoResource()
        data = Dataset()
        with options["file"] as f:
            data.load(f)
        loaded = len(data)
        self.stdout.write(
            self.style.SUCCESS("Successfully loaded %s jbi objects" % loaded)
        )
        result = jbi.import_data(
            data, raise_errors=True, use_transactions=True
        )
        self.stdout.write(
            self.style.SUCCESS(
                "Successfully imported %s jbi objects" % result.total_rows
            )
        )
