# Copyright (C) 2015 The Sipwise Team - http://sipwise.com

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

import os
import shutil

from django.test import TestCase, override_settings
from django.conf import settings
from mock import patch, call, mock_open


debian_changelog = """
ngcp-fake (3.8.7.4+0~mr3.8.7.4) unstable; urgency=medium

  [ Kirill Solomko ]
  * [ee3c706] MT#21499 add mysql replication options

  [ Victor Seva ]
  * [aabb345] TT#345 fake comment
  * [aabb123] MT#8989 TT#123 fake comment

  [ Sipwise Jenkins Builder ]

 -- whatever <jenkins@sipwise.com>  Fri, 22 Jul 2016 17:29:27 +0200
"""


@override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True)
@override_settings(JBI_BASEDIR=os.path.join(BASE_DIR, 'hotfix', 'fixtures'))
class TestHotfixReleased(TestCase):

    @patch('__builtin__.open', mock_open(read_data=debian_changelog))
    def test_hotfixreleased(self):
        param = self.get_defaults()
        jbi = JenkinsBuildInfo.objects.create(**param)
        base_path = os.path.join(settings.JBI_BASEDIR,
                                 jbi.jobname, str(jbi.buildnumber))
        url = JBI_ENVVARS_URL.format(
            settings.JENKINS_URL,
            jbi.jobname,
            jbi.buildnumber
        )
        path = os.path.join(base_path, 'envVars.json')
        dlfile.assert_any_call(url, path)
