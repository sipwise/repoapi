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
import structlog

from .models import NoteInfo
from debian.changelog import Changelog

logger = structlog.get_logger(__name__)


def process_hotfix(jbi_info, projectname, path, force=False):
    model = NoteInfo.get_model()
    ids, changelog = parse_changelog(path, model)
    structlog.contextvars.bind_contextvars(
        ids=ids, project=projectname, release=changelog.full_version
    )
    logger.info(f"hotfix_released[{jbi_info}] {path}")
    for wid in ids:
        model.create(wid, projectname, changelog.full_version, force)


def parse_changelog(path, model=None):
    if model is None:
        model = NoteInfo.get_model()
    changelog = Changelog()
    with open(path, "r") as file_changelog:
        changelog.parse_changelog(file_changelog.read())
    set_ids = set()
    for block in changelog:
        for change in block.changes():
            set_ids = set_ids.union(model.getIds(change))
    return (set_ids, changelog)
