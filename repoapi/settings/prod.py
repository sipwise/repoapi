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
#
# Build paths inside the project like this: join(BASE_DIR, ...)
import os
from configparser import RawConfigParser
from os.path import dirname
from os.path import join

from celery.schedules import crontab

from .common import *  # noqa

# pylint: disable=W0401,W0614

BASE_DIR = dirname(dirname(dirname(os.path.abspath(__file__))))

VAR_DIR = "/var/lib/repoapi"
if not os.path.exists(VAR_DIR):
    VAR_DIR = BASE_DIR

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# read it from external file
SECRET_KEY = open(join(VAR_DIR, ".secret_key")).read().strip()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [".mgm.sipwise.com"]

INSTALLED_APPS.extend(PROJECT_APPS)  # noqa

LOGGING["loggers"]["repoapi"]["level"] = os.getenv(  # noqa
    "DJANGO_LOG_LEVEL", "INFO"
)  # noqa

server_config = RawConfigParser()
server_config.read(join(VAR_DIR, "server.ini"))
JENKINS_URL = server_config.get("server", "JENKINS_URL")
GERRIT_URL = server_config.get("server", "GERRIT_URL")
DOCKER_REGISTRY_URL = server_config.get("server", "DOCKER_REGISTRY_URL")
AUTH_LDAP_SERVER_URI = server_config.get("server", "AUTH_LDAP_SERVER_URI")
AUTH_LDAP_USER_BASE = server_config.get("server", "AUTH_LDAP_USER_BASE")
AUTH_LDAP_USER_DN_TEMPLATE = "uid=%(user)s," + AUTH_LDAP_USER_BASE
BUILD_POOL = server_config.get("server", "BUILD_POOL")

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

gerrit_config = RawConfigParser()
gerrit_config.read(join(VAR_DIR, "gerrit.ini"))
GERRIT_REST_HTTP_USER = gerrit_config.get("gerrit", "HTTP_USER")
GERRIT_REST_HTTP_PASSWD = gerrit_config.get("gerrit", "HTTP_PASSWD")

GITWEB_URL = "https://git.mgm.sipwise.com/gitweb/?p={}.git;a=commit;h={}"
WORKFRONT_CREDENTIALS = join(BASE_DIR, "/etc/jenkins_jobs/workfront.ini")
WORKFRONT_NOTE = True

# build app
BUILD_KEY_AUTH = True
REPOS_SCRIPTS_CONFIG_DIR = "/usr/share/sipwise-repos-scripts/config"

# celery
BROKER_URL = server_config.get("server", "BROKER_URL")
CELERYBEAT_SCHEDULE = {
    # Executes every Sunday morning at 7:30 A.M
    "purge-trunk": {
        "task": "repoapi.tasks.jbi_purge",
        "schedule": crontab(hour=7, minute=30, day_of_week="sunday"),
        "args": ("none", 4),
    },
    "purge-none": {
        "task": "repoapi.tasks.jbi_purge",
        "schedule": crontab(hour=7, minute=30, day_of_week="sunday"),
        "args": (None, 1),
    },
}
CELERY_TIMEZONE = "UTC"

JBI_BASEDIR = join(VAR_DIR, "jbi_files")
JBI_ARTIFACT_JOBS = [
    "release-tools-runner",
]
JBI_ALLOWED_HOSTS = ["jenkins.mgm.sipwise.com"]
