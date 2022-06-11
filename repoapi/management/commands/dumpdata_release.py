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
import argparse

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from repoapi.admin import JenkinsBuildInfoResource


class JenkinsBuildInfoResourceFilter(JenkinsBuildInfoResource):
    def __init__(self, **kwargs):
        self.filter = kwargs

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(**self.filter)


class Command(BaseCommand):
    help = "export BuildRelease info"

    def add_arguments(self, parser):
        parser.add_argument(
            "--format", choices=["json", "yaml"], default="yaml"
        )
        parser.add_argument("uuid", help="release_uuid")
        parser.add_argument("file", type=argparse.FileType("w"))

    def handle(self, *args, **options):
        params = {
            "param_release_uuid": options["uuid"],
        }
        jbi = JenkinsBuildInfoResourceFilter(**params)
        dataset = jbi.export()
        exported = len(dataset)
        if exported <= 0:
            raise CommandError(
                "no jbi objects for release_uuid:'{}' found".format(
                    options["uuid"]
                )
            )
        with options["file"] as f:
            f.write(dataset.export(options["format"]))
        self.stdout.write(
            self.style.SUCCESS(
                "Successfully exported %s jbi objects" % exported
            )
        )
