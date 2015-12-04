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

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

# pylint: disable=W0401,W0614,C0413
from .test import *

LOGGING['loggers']['release_dashboard']['level'] = \
    os.getenv('DJANGO_LOG_LEVEL', 'DEBUG')

# celery
BROKER_BACKEND = 'amqp'
CELERY_ALWAYS_EAGER = False
BROKER_URL = 'amqp://guest:guest@rabbit'
JBI_BASEDIR = os.path.join(BASE_DIR, 'jbi_files')
