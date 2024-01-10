# Copyright (C) 2015-2022 The Sipwise Team - http://sipwise.com
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

import structlog

from .test import *  # noqa

# pylint: disable=W0401,W0614,C0413
# avoid having to hardcode an IP address

LOGGING["loggers"]["repoapi"]["level"] = os.getenv(  # noqa
    "DJANGO_LOG_LEVEL", "DEBUG"
)

# celery
BROKER_BACKEND = "amqp"
CELERY_TASK_ALWAYS_EAGER = False
CELERY_BROKER_URL = "amqp://guest:guest@rabbit"
JBI_BASEDIR = BASE_DIR / "jbi_files"  # noqa
JBI_ARCHIVE = BASE_DIR / "jbi_archive"  # noqa

# Enable access when not accessing from localhost:
ALLOWED_HOSTS = [
    gethostname(),
    gethostbyname(gethostname()),
]
# or to manually override:
# ALLOWED_HOSTS = ['172.17.0.3']

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
        structlog.processors.CallsiteParameterAdder(
            {
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            }
        ),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
