# Copyright (C) 2020-2022 The Sipwise Team - http://sipwise.com
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
from django.apps import AppConfig
from django.db.models.signals import post_save


class RepoAPIConfig(AppConfig):
    name = "repoapi"

    def ready(self):
        from .conf import settings, Tracker

        # Implicitly connect a signal handlers decorated with @receiver.
        from . import signals

        if settings.REPOAPI_TRACKER == Tracker.WORKFRONT:
            post_save.connect(
                signals.workfront_note_manage,
                sender="repoapi.JenkinsBuildInfo",
                dispatch_uid="workfront_note_manage",
            )
