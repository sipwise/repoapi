# Copyright (C) 2017 The Sipwise Team - http://sipwise.com

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

import re
from release_dashboard.utils import get_tags, get_branches

regex_hotfix = re.compile(r'^mr[0-9]+\.[0-9]+\.[0-9]+$')
regex_mr = re.compile(r'^mr.+$')
regex_master = re.compile(r'^master$')


def _projects_versions(projects, regex=None,
                       tags=True, branches=True, master=False):
    res = []
    for project in projects:
        info = {
            'name': project,
        }
        if tags:
            info['tags'] = get_tags(project, regex)
        if branches:
            info['branches'] = get_branches(project, regex)
        if master:
            info['branches'].append('master')
        res.append(info)
    return res


def _common_versions(context, tags=True, branches=True):
    common_versions = {'tags': set(), 'branches': set()}

    for project in context['projects']:
        if tags:
            common_versions['tags'] |= set(project['tags'])
        if branches:
            common_versions['branches'] |= set(project['branches'])
    context['common_versions'] = {
        'tags': sorted(common_versions['tags'], reverse=True),
        'branches': sorted(common_versions['branches'], reverse=True),
    }


def _hash_versions(data, projects):
    result = {}
    for i in projects:
        try:
            result[i] = data["version_{0}".format(i)]
        except (KeyError, AttributeError):
            pass
    return result
