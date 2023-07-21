# Copyright (C) 2016-2022 The Sipwise Team - http://sipwise.com
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
import os

from celery import Celery
from django_structlog.celery.steps import DjangoStructLogInitStep

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "repoapi.settings.prod")

app = Celery("repoapi")
app.steps["worker"].add(DjangoStructLogInitStep)
# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("repoapi.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task()
def jbi_parse_hotfix(jbi_id: str, path: str):
    app.send_task("hotfix.tasks.hotfix_released", args=[jbi_id, path])


@app.task()
def jbi_parse_buildinfo(jbi_id: str, path: str):
    app.send_task("buildinfo.tasks.parse_buildinfo", args=[jbi_id, path])


@app.task()
def process_result(jbi_id: str, path_envVars: str):
    app.send_task(
        "release_changed.tasks.process_result",
        args=[jbi_id, path_envVars],
    )
