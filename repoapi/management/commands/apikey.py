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
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from rest_framework_api_key.crypto import KeyGenerator


class Command(BaseCommand):
    help = "apikey helper"
    keygen = KeyGenerator()

    def generate(self, *args, **options):
        key, prefix, hashed_key = self.keygen.generate()
        self.stdout.write(
            self.style.SUCCESS(
                f"key:{key} prefix:{prefix} hashed_key:{hashed_key}"
            )
        )

    def hash(self, *argc, **options):
        if "value" not in options:
            raise CommandError("no value parameter found")
        res = self.keygen.hash(options["value"])
        self.stdout.write(self.style.SUCCESS(f"{res}"))

    def verify(self, *args, **options):
        if "value" not in options:
            raise CommandError("no value parameter found")
        value = options["value"]
        if "key" not in options:
            raise CommandError("no key parameter found")
        key = options["key"]
        res = self.keygen.verify(key, value)
        if not res:
            raise CommandError(
                f"verification failed key:{key} hashed_key:{value}"
            )

    def add_arguments(self, parser):
        parser.add_argument(
            "action", choices=["generate", "hash", "verify"], default="hash"
        )
        parser.add_argument("--key")
        parser.add_argument("--value", help="value")

    def handle(self, *args, **options):
        return getattr(self, options["action"])(**options)
