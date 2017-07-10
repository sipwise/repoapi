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
import re
import logging
from debian.changelog import Changelog
from repoapi import utils
from .models import WorkfrontNoteInfo

hotfix_re_release = re.compile('.+~(mr[0-9]+\.[0-9]+\.[0-9]+.[0-9]+)$')

logger = logging.getLogger(__name__)


def parse_changelog(path):
    changelog = Changelog()
    with open(path, 'r') as file_changelog:
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
        workfront_id=wid,
        projectname=projectname,
        version=version)
    if created:
        msg = "hotfix %s.git %s triggered" % (note.projectname, note.version)
        utils.workfront_note_send(wid, msg)
        target_release = get_target_release(note.version)
        if target_release:
            utils.workfront_set_release_target(wid, target_release)
