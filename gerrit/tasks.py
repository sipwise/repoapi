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

import structlog
from celery import shared_task
from django.apps import apps
from requests.exceptions import HTTPError

from gerrit.utils import get_change_info
from gerrit.utils import get_datetime

logger = structlog.get_logger(__name__)


@shared_task(ignore_result=True)
def cleanup(weeks: int, dry_run=False, today=None):
    if today is None:
        today = datetime.now()
    else:
        today = date.fromisoformat(today)
    max_date = today - timedelta(weeks=weeks)
    logger.debug(f"max_date:{max_date}")
    GerritRepoInfo = apps.get_model("repoapi", "GerritRepoInfo")
    manager = GerritRepoInfo.objects
    qs = manager.filter(modified__lt=max_date)
    for gri in qs.iterator():
        info = get_change_info(gri.gerrit_change)
        status = info["status"]
        if status not in ["MERGED", "ABANDONED"]:
            continue
        if dry_run:
            logger.info(f"{gri} {status}, remove from db, [dry-run]")
        else:
            logger.info(f"{gri} {status}, remove from db")
            manager.review_removed(
                gri.param_ppa, gri.gerrit_change, gri.projectname
            )


@shared_task(ignore_result=True)
def refresh(dry_run=False):
    GerritRepoInfo = apps.get_model("repoapi", "GerritRepoInfo")
    qs = GerritRepoInfo.objects.filter(created__date=date(1977, 1, 1))
    for gri in qs.iterator():
        try:
            info = get_change_info(gri.gerrit_change)
            gri.created = get_datetime(info["created"])
            gri.modified = get_datetime(info["updated"])
            # don't update modified field on save
            gri.update_modified = False
            if dry_run:
                logger.info(
                    f"{gri} would be changed to "
                    f" created:{gri.created}"
                    f" modified:{gri.modified}"
                )
            else:
                gri.save()
        except HTTPError:
            logger.error(f"{gri} not found, remove it from db")
            gri.delete()
