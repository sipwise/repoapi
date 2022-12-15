# Copyright (C) 2017-2022 The Sipwise Team - http://sipwise.com
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

import structlog
from django.apps import apps

from .models import BuildInfo

logger = structlog.get_logger(__name__)


def process_buildinfo(jbi_id: int, path: str):
    JenkinsBuildInfo = apps.get_model("repoapi", "JenkinsBuildInfo")
    jbi = JenkinsBuildInfo.objects.get(pk=jbi_id)
    with open(path, "r") as file:
        info = json.load(file)
    BuildInfo.objects.create(
        builton=info["builtOn"],
        timestamp=info["timestamp"],
        duration=info["duration"],
        projectname=jbi.projectname,
        jobname=jbi.jobname,
        buildnumber=jbi.buildnumber,
        param_tag=jbi.param_tag,
        param_branch=jbi.param_branch,
        param_release=jbi.param_release,
        param_release_uuid=jbi.param_release_uuid,
        param_distribution=jbi.param_distribution,
        param_ppa=jbi.param_ppa,
    )
