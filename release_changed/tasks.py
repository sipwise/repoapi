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
import json
import logging

from celery import shared_task
from django.apps import apps

from .models import ReleaseChanged

logger = logging.getLogger(__name__)


@shared_task(ignore_result=True)
def process_result(jbi_id, path_envVars):
    JenkinsBuildInfo = apps.get_model("repoapi", "JenkinsBuildInfo")
    jbi = JenkinsBuildInfo.objects.get(id=jbi_id)
    with open(path_envVars) as data_file:
        data = json.load(data_file)
    info = data["envMap"]
    if info["vmdone"] == "yes":
        ReleaseChanged.objects.filter(
            version=info["vmversion"], vmtype=info["vmtype"],
        ).delete()
        logger.info("{}_{} deleted".format(info["vmtype"], info["vmversion"]))
        return
    r, created = ReleaseChanged.objects.get_or_create(
        version=info["vmversion"],
        vmtype=info["vmtype"],
        defaults={"result": jbi.result},
    )
    if not created:
        r.result = jbi.result
        r.save()
    if r.result == "SUCCESS":
        changed = "*NOT*"
    else:
        changed = ""
    msg = "setting {}_{} as {} changed, created:{}"
    logger.info(msg.format(r.vmtype, r.version, changed, created))
