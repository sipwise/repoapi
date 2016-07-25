# Copyright (C) 2016 The Sipwise Team - http://sipwise.com

# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.

# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import absolute_import
import logging
from debian import Changelog
from .models import WorkfrontNoteInfo

logger = logging.getLogger(__name__)


def parse_changelog(projectname, release, path):
    wni = WorkfrontNoteInfo.objects
    changelog = Changelog(path)
    workfront_ids = set()
    for change in changelog[0].changes():
        set_ids += WorkfrontNoteInfo.getIds(change)

    for wid in workfront_ids:
        obj, created = wni.get_or_create(
            workfront_id=wid,
            projectname=projectname,
            version=changelog[0].version,
            param_tag=release)
