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
# pylint: disable=W0401,W0614
from .common import *

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('RESULTS', '/tmp')
RESULTS_DIR = os.environ['RESULTS']

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ')+0h68-(g30hg1awc6!y65cwws6j^qd5=&pc2@h430=9x@bf%2'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

TESTING_APPS = [
    'django_jenkins',
]
INSTALLED_APPS.extend(TESTING_APPS)
INSTALLED_APPS.extend(PROJECT_APPS)

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# django-jenkins
JENKINS_TASKS = (
    'django_jenkins.tasks.run_pylint',
    'django_jenkins.tasks.run_flake8',
)
PYLINT_RCFILE = 'pylint.cfg'

DJANGO_LOG_LEVEL = 'DEBUG'

JENKINS_URL = "http://localhost"
GERRIT_URL = "https://gerrit.local/{}"
GERRIT_REST_HTTP_USER = 'jenkins'
GERRIT_REST_HTTP_PASSWD = 'verysecrethttppasswd'
GITWEB_URL = "https://git.local/gitweb/?p={}.git;a=commit;h={}"
WORKFRONT_CREDENTIALS = os.path.join(BASE_DIR, '.workfront.ini')
WORKFRONT_NOTE = True

# celery
BROKER_BACKEND = 'memory'
CELERY_ALWAYS_EAGER = True
# CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
JBI_BASEDIR = os.path.join(RESULTS_DIR, 'jbi_files')
JBI_ARTIFACT_JOBS = [
    'fake-release-tools-runner',
]
