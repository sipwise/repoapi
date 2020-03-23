# Copyright (C) 2015 The Sipwise Team - http://sipwise.com
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
from os.path import join
from socket import gethostbyname
from socket import gethostname

from configurations import values

from .test import Test


class Dev(Test):
    LOG_LEVEL = values.Value("DEBUG")
    # celery
    BROKER_BACKEND = "amqp"
    CELERY_TASK_ALWAYS_EAGER = False
    CELERY_BROKER_URL = "amqp://guest:guest@rabbit"
    JBI_BASEDIR = join(Test.BASE_DIR, "jbi_files")  # noqa

    # Enable access when not accessing from localhost:
    ALLOWED_HOSTS = [
        gethostname(),
        gethostbyname(gethostname()),
    ]
    # or to manually override:
    # ALLOWED_HOSTS = ['172.17.0.3']
