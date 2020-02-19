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
import os
from socket import gethostbyname
from socket import gethostname

from .test import *  # noqa

# pylint: disable=W0401,W0614,C0413
# avoid having to hardcode an IP address

LOGGING["loggers"]["repoapi"]["level"] = os.getenv(  # noqa
    "DJANGO_LOG_LEVEL", "DEBUG"
)

# celery
BROKER_BACKEND = "amqp"
CELERY_ALWAYS_EAGER = False
BROKER_URL = "amqp://guest:guest@rabbit"
JBI_BASEDIR = os.path.join(BASE_DIR, "jbi_files")  # noqa

# Enable access when not accessing from localhost:
ALLOWED_HOSTS = [
    gethostname(),
    gethostbyname(gethostname()),
]
# or to manually override:
# ALLOWED_HOSTS = ['172.17.0.3']
