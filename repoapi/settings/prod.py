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
from ConfigParser import RawConfigParser
# pylint: disable=W0401,W0614
from .common import *

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

VAR_DIR = '/var/lib/repoapi'
if not os.path.exists(VAR_DIR):
    VAR_DIR = BASE_DIR

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# read it from external file
SECRET_KEY = open(os.path.join(VAR_DIR, '.secret_key')).read().strip()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['.mgm.sipwise.com']

INSTALLED_APPS.extend(PROJECT_APPS)

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(VAR_DIR, 'db.sqlite3'),
    }
}

LOGGING['loggers']['repoapi']['level'] = os.getenv('DJANGO_LOG_LEVEL', 'INFO')

server_config = RawConfigParser()
server_config.read(os.path.join(VAR_DIR, 'server.ini'))
JENKINS_URL = server_config.get('server', 'JENKINS_URL')
GERRIT_URL = server_config.get('server', 'GERRIT_URL')

gerrit_config = RawConfigParser()
gerrit_config.read(os.path.join(VAR_DIR, 'gerrit.ini'))
GERRIT_REST_HTTP_USER = gerrit_config.get('gerrit', 'HTTP_USER')
GERRIT_REST_HTTP_PASSWD = gerrit_config.get('gerrit', 'HTTP_PASSWD')

GITWEB_URL = "https://git.mgm.sipwise.com/gitweb/?p={}.git;a=commit;h={}"
WORKFRONT_CREDENTIALS = os.path.join(BASE_DIR,
                                     '/etc/jenkins_jobs/workfront.ini')
WORKFRONT_NOTE = True
# celery
BROKER_URL = server_config.get('server', 'BROKER_URL')
JBI_BASEDIR = os.path.join(VAR_DIR, 'jbi_files')
JBI_ARTIFACT_JOBS = [
    'release-tools-runner',
]
