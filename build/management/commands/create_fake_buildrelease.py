# Copyright (C) 2020 The Sipwise Team - http://sipwise.com
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
import uuid

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from build.models import BuildRelease
from build.models import regex_mrXX
from build.utils import ReleaseConfig


class Command(BaseCommand):
    help = "generates fake BuildRelease info. Useful just for mrX.Y builds"

    def add_arguments(self, parser):
        parser.add_argument("version")
        parser.add_argument(
            "--uuid", help="release_uuid", default=uuid.uuid4()
        )

    def handle(self, *args, **options):
        ver = options["version"]
        if not regex_mrXX.match(ver):
            raise CommandError("'{}'' not mrX.Y version".format(ver))
        release = "release-{}".format(ver)
        config = ReleaseConfig(release)
        if (
            BuildRelease.objects.release(
                release, config.debian_release
            ).count()
            > 0
        ):
            raise CommandError("'{}' has already instances".format(release))
        BuildRelease.objects.create_build_release(
            options["uuid"], ver, fake=True
        )
