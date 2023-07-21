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
#
# Build paths inside the project like this: join(BASE_DIR, ...)
import os
from configparser import RawConfigParser
from functools import reduce
from pathlib import Path
from urllib.parse import urlparse

import ldap
import structlog
from celery.schedules import crontab
from django_auth_ldap.config import LDAPGroupQuery
from django_auth_ldap.config import LDAPSearch
from django_auth_ldap.config import PosixGroupType

from .common import *  # noqa

# pylint: disable=W0401,W0614

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent

VAR_DIR = Path("/var/lib/repoapi")
if not VAR_DIR.exists():
    VAR_DIR = BASE_DIR

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# read it from external file
SECRET_KEY = (VAR_DIR / ".secret_key").read_text().strip()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [".mgm.sipwise.com"]

LOGGING["loggers"]["repoapi"]["level"] = os.getenv(  # noqa
    "DJANGO_LOG_LEVEL", "INFO"
)  # noqa
# for now lets see debug for auth ldap
LOGGING["loggers"]["django_auth_ldap"] = {  # noqa
    "level": "DEBUG",
    "handlers": ["console"],
}

server_config = RawConfigParser()
server_config.read(VAR_DIR / "server.ini")

JENKINS_URL = server_config.get("jenkins", "URL")
JENKINS_HTTP_USER = server_config.get("jenkins", "HTTP_USER")
JENKINS_HTTP_PASSWD = server_config.get("jenkins", "HTTP_PASSWD")

GERRIT_URL = server_config.get("gerrit", "URL")
GERRIT_REST_HTTP_USER = server_config.get("gerrit", "HTTP_USER")
GERRIT_REST_HTTP_PASSWD = server_config.get("gerrit", "HTTP_PASSWD")

TRACKER_MANTIS_URL = server_config.get("mantis", "URL")
TRACKER_MANTIS_TOKEN = server_config.get("mantis", "TOKEN")
mantis_parsed = urlparse(TRACKER_MANTIS_URL)
TRACKER_MANTIS_MAPPER_URL = (
    f"{mantis_parsed.scheme}://{mantis_parsed.netloc}/view.php?id="
    + "{mantis_id}"
)
DOCKER_REGISTRY_URL = server_config.get("server", "DOCKER_REGISTRY_URL")
AUTH_LDAP_SERVER_URI = server_config.get("server", "AUTH_LDAP_SERVER_URI")
AUTH_LDAP_USER_BASE = server_config.get("server", "AUTH_LDAP_USER_BASE")
AUTH_LDAP_GROUP_BASE = server_config.get("server", "AUTH_LDAP_GROUP_BASE")
AUTH_LDAP_REQUIRE_GROUP_LIST = server_config.get(
    "server", "AUTH_LDAP_REQUIRE_GROUP_LIST"
).split(",")
require_grp_list_size = len(AUTH_LDAP_REQUIRE_GROUP_LIST)
AUTH_LDAP_USER_DN_TEMPLATE = "uid=%(user)s," + AUTH_LDAP_USER_BASE
AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail",
}
AUTH_LDAP_ALWAYS_UPDATE_USER = True
AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
    AUTH_LDAP_GROUP_BASE, ldap.SCOPE_SUBTREE, "(objectClass=posixGroup)"
)
AUTH_LDAP_GROUP_TYPE = PosixGroupType()
AUTH_LDAP_USER_FLAGS_BY_GROUP = {
    "is_staff": f"cn=devops,{AUTH_LDAP_GROUP_BASE}",
}
AUTH_LDAP_FIND_GROUP_PERMS = True
AUTH_LDAP_CACHE_TIMEOUT = 3600

if require_grp_list_size > 1:
    AUTH_LDAP_REQUIRE_GROUP = reduce(
        lambda x, y: LDAPGroupQuery(f"cn={x},{AUTH_LDAP_GROUP_BASE}")
        | LDAPGroupQuery(f"cn={y},{AUTH_LDAP_GROUP_BASE}"),
        AUTH_LDAP_REQUIRE_GROUP_LIST,
    )
elif require_grp_list_size == 1:
    for x in AUTH_LDAP_REQUIRE_GROUP_LIST:
        AUTH_LDAP_REQUIRE_GROUP = LDAPGroupQuery(
            f"cn={x},{AUTH_LDAP_GROUP_BASE}"
        )

BUILD_POOL = server_config.getint("server", "BUILD_POOL")

# Keep ModelBackend around for per-user permissions and maybe a local
# superuser.
AUTHENTICATION_BACKENDS = (
    "django_auth_ldap.backend.LDAPBackend",
    "django.contrib.auth.backends.ModelBackend",
)

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": server_config.get("server", "DB_NAME"),
        "USER": server_config.get("server", "DB_USER"),
        "PASSWORD": server_config.get("server", "DB_PWD"),
        "HOST": "localhost",
        "PORT": "",
    }
}
STATICFILES_STORAGE = (
    "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
)
GITWEB_URL = "https://git.mgm.sipwise.com/gitweb/?p={}.git;a=commit;h={}"
TRACKER_WORKFRONT_CREDENTIALS = BASE_DIR / "/etc/jenkins_jobs/workfront.ini"

# build app
BUILD_REPOS_SCRIPTS_CONFIG_DIR = Path(
    "/usr/share/sipwise-repos-scripts/config"
)

# celery
CELERY_BROKER_URL = server_config.get("server", "BROKER_URL")
CELERY_BEAT_SCHEDULE = {
    # Executes every Sunday morning at 7:30 A.M
    "purge-trunk": {
        "task": "repoapi.tasks.jbi_purge",
        "schedule": crontab(hour=7, minute=30, day_of_week="sun"),
        "args": ("none", 4),
    },
    "purge-none": {
        "task": "repoapi.tasks.jbi_purge",
        "schedule": crontab(hour=7, minute=30, day_of_week="sun"),
        "args": (None, 1),
    },
    "gerrit-cleanup": {
        "schedule": crontab(hour=7, minute=30, day_of_month=15),
        "tasks": "gerrit.tasks.cleanup",
        "args": (4),
    },
}
CELERY_TIMEZONE = "UTC"

JBI_BASEDIR = VAR_DIR / "jbi_files"
JBI_ARTIFACT_JOBS = [
    "release-tools-runner",
]
JBI_ALLOWED_HOSTS = [urlparse(JENKINS_URL).netloc]

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.CallsiteParameterAdder(
            {
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            }
        ),
        structlog.processors.ExceptionPrettyPrinter(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
