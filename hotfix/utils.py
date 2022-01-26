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
import re

import structlog

from .models import WorkfrontNoteInfo
from debian.changelog import Changelog
from repoapi import utils

hotfix_re_release = re.compile(r".+~(mr[0-9]+\.[0-9]+\.[0-9]+.[0-9]+)$")

logger = structlog.get_logger(__name__)


def process_hotfix(jbi_info, projectname, path):
    logger.info("hotfix_released[%s] %s", jbi_info, path)
    wids, changelog = parse_changelog(path)
    for wid in wids:
        create_note(wid, projectname, changelog.full_version)


def parse_changelog(path):
    changelog = Changelog()
    with open(path, "r") as file_changelog:
        changelog.parse_changelog(file_changelog.read())
    set_ids = set()
    for block in changelog:
        for change in block.changes():
            set_ids = set_ids.union(WorkfrontNoteInfo.getIds(change))
    return (set_ids, changelog)


def get_target_release(version):
    match = hotfix_re_release.search(version)
    if match:
        return match.group(1)


def create_note(wid, projectname, version):
    wni = WorkfrontNoteInfo.objects

    note, created = wni.get_or_create(
        workfront_id=wid, projectname=projectname, version=version
    )
    if created:
        msg = "hotfix %s.git %s triggered" % (note.projectname, note.version)
        utils.workfront_note_send(wid, msg)
        target_release = get_target_release(note.version)
        if target_release:
            utils.workfront_set_release_target(wid, target_release)
