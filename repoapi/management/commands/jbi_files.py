# Copyright (C) 2024 The Sipwise Team - http://sipwise.com
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
from os import scandir
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from repoapi.models import JenkinsBuildInfo
from repoapi.utils import cleanup_build


class Command(BaseCommand):
    help = "jbi_files related actions"

    def get_missing_builds(self, jobname, path: Path):
        qs = JenkinsBuildInfo.objects.job_builds(jobname)
        known_builds = [str(x) for x in qs]
        missing_builds = set()
        with scandir(path) as it:
            for item in it:
                if item.is_dir() and item.name not in known_builds:
                    missing_builds.add(item.name)
        count = len(missing_builds)
        if count > 0:
            self.stdout.write(
                self.style.NOTICE(
                    f"detected {count} missing builds files for {jobname}"
                )
            )
        return missing_builds

    def add_arguments(self, parser):
        parser.add_argument("action", choices=["cleanup"])
        parser.add_argument("--dry-run", action="store_true")

    def cleanup(self, *args, **options):
        jobnames = []
        with scandir(settings.JBI_BASEDIR) as it:
            for item in it:
                if item.is_dir():
                    jobnames.append(item.name)
        for jobname in jobnames:
            path = settings.JBI_BASEDIR / jobname
            dst_path = settings.JBI_ARCHIVE / jobname
            missing_builds = self.get_missing_builds(jobname, path)
            if options["dry_run"]:
                continue
            for build in missing_builds:
                cleanup_build(path / build, dst_path)
            if len(missing_builds) > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"archived {missing_builds} dirs at {path}"
                    )
                )

    def handle(self, *args, **options):
        action = getattr(self, options["action"])
        action(*args, **options)
