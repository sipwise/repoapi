# Copyright (C) 2015-2020 The Sipwise Team - http://sipwise.com
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
from django.db.models import signals

from .gri import gerrit_repo_manage
from .gri import GerritRepoInfo  # noqa
from .jbi import jbi_manage
from .jbi import JenkinsBuildInfo
from .wni import workfront_note_manage
from .wni import WorkfrontNoteInfo  # noqa
from repoapi.conf import settings

post_save = signals.post_save.connect
post_save(jbi_manage, sender=JenkinsBuildInfo)
post_save(gerrit_repo_manage, sender=JenkinsBuildInfo)
if settings.WORKFRONT_NOTE:
    post_save(workfront_note_manage, sender=JenkinsBuildInfo)
