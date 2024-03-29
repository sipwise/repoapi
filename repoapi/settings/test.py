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
import os
from pathlib import Path

from .common import *  # noqa

# pylint: disable=W0401,W0614

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent
os.environ.setdefault("RESULTS", "/tmp")
RESULTS_DIR = Path(os.environ["RESULTS"])

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ")+0h68-(g30hg1awc6!y65cwws6j^qd5=&pc2@h430=9x@bf%2"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# needed for django-coverage-plugin
TEMPLATES[0]["OPTIONS"]["debug"] = True  # noqa

DJANGO_LOG_LEVEL = "DEBUG"

JENKINS_URL = "http://localhost"
GITWEB_URL = "https://git.local/gitweb/?p={}.git;a=commit;h={}"
TRACKER_WORKFRONT_CREDENTIALS = BASE_DIR / ".workfront.ini"
DOCKER_REGISTRY_URL = "https://localhost:5000/v2/{}"

# fake info
DOCKER_REGISTRY = """
{"repositories":["comx-fs-test-jessie","data-hal-jessie","documentation-jessie","janus-admin-jessie","janus-client-jessie","jenkins-configs","jenkins-configs-jessie","kamailio-config-tests-jessie","libswrate-jessie","libtcap-jessie","lua-ngcp-kamailio","lua-ngcp-kamailio-jenkins","lua-ngcp-kamailio-jessie","ngcp-csc-jessie","ngcp-panel-selenium","ngcp-panel-tests-rest-api-jessie","ngcp-panel-tests-selenium-jessie","ngcp-rate-o-mat-unit-tests-jessie","ngcp-rtcengine-test-jessie","ngcp-rtcengine-tests-selenium-jessie","ngcp-rtcengine-tests-selenium-stretch","ngcp-sipwise-snmp-mibs-jessie","ngcp-snmp-jessie","ngcpcfg-jessie","ossbss-perl-testing-wheezy","puppet-octocatalog-diff","puppet-sipwise-jessie","rate-o-mat-functional-tests-jessie","rate-o-mat-jessie","release-dashboard","repoapi-jessie","repos-scripts-jessie","rtpengine-jessie","sipphone-android","sipwise/ce-trunk","sipwise/mr3.8.10","sipwise/mr3.8.2","sipwise/mr3.8.3","sipwise/mr3.8.4","sipwise/mr3.8.5","sipwise/mr3.8.6","sipwise/mr3.8.7","sipwise/mr3.8.8","sipwise/mr3.8.9","sipwise/mr4.0.1","sipwise/mr4.0.2","sipwise/mr4.1.1","sipwise/mr4.1.2","sipwise/mr4.2.1","sipwise/mr4.2.2","sipwise/mr4.3.1","sipwise/mr4.3.2","sipwise/mr4.4.1","sipwise/mr4.4.2","sipwise/mr4.5.1","sipwise/mr4.5.2","sipwise/mr4.5.3","sipwise/mr4.5.4","sipwise/mr5.0.1","sipwise/mr5.0.2","sipwise/mr5.1.1","sipwise/mr5.1.2","sipwise/mr5.2.1","sipwise/mr5.3.1","sipwise-jessie","sipwise-stretch","sipwise-webpage-soap-docker-jessie","sipwise-webpage-soap-jessie","sipwise-wheezy","system-tools-jessie"]}
"""
BUILD_POOL = 1

RELEASE_DASHBOARD_DOCKER_IMAGES = {
    "data-hal-jessie": [
        "Ia9b03983d174a1546631f5b42e605235809711ef",
        "If508e72c01d9bc78836a40204e508585d1dc3555",
        "latest",
        "mr5.2",
        "mr5.3.1",
        "mr5.3",
    ],
    "documentation-jessie": [
        "If53a93f4b6d1c82fd7af5672e8b02087e646b507",
        "latest",
        "mr5.2",
        "mr5.3.1",
        "mr5.3",
    ],
    "ngcp-panel-selenium": ["latest"],
    "ngcp-panel-tests-rest-api-jessie": [
        "I5c5c351e36da15db71fe3addbed4603007e8c304",
        "I89e9acd846132508e135f7443482c0371c80d2b2",
        "latest",
    ],
    "ngcp-panel-tests-selenium-jessie": [
        "I3a899b8945688c2ef3a4be6ba6c4c1d4cbf6d548",
        "latest",
    ],
}

# build app
BUILD_REPOS_SCRIPTS_CONFIG_DIR = BASE_DIR.joinpath(
    "build", "fixtures", "config"
)

# celery
CELERY_BROKER_URL = "memory://localhost/"
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
JBI_BASEDIR = RESULTS_DIR / "jbi_files"
JBI_ARTIFACT_JOBS = [
    "fake-release-tools-runner",
]
REPOAPI_ARTIFACT_JOB_REGEX = []
JBI_ALLOWED_HOSTS = ["jenkins-dev.mgm.sipwise.com"]

# no tracker
TRACKER_PROVIDER = "None"
