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

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Application definition
# django-jenkins
PROJECT_APPS = [
    'repoapi',
    'hotfix',
    'panel',
    'release_dashboard',
    'build',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_api_key',
    'rest_framework_swagger',
    'django_assets',
    'django_celery_results',
    'django_extensions',
    'jsonify',
]

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'repoapi.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            'repoapi/templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'repoapi.wsgi.application'

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django_assets.finders.AssetsFinder',
)

STATIC_ROOT = os.path.join(BASE_DIR, 'static_media/')

REST_FRAMEWORK = {
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.DjangoFilterBackend',
    )
}

SWAGGER_SETTINGS = {
    'api_version': '0.1',
    'info': {
        'contact': 'dev@sipwise.com',
        'description': 'repoapi, one ring to rule them all',
        'license': 'GPL 3.0',
        'title': 'RepoApi',
    },
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'repoapi': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
        'release_dashboard': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
    },
}

JENKINS_TOKEN = "sipwise_jenkins_ci"

CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_RESULT_BACKEND = 'django-db'

HOTFIX_ARTIFACT = 'debian_changelog.txt'

RELEASE_DASHBOARD_SETTINGS = {
    'debian_supported': ('auto', 'buster', 'stretch', 'jessie', 'wheezy', 'squeeze'),
    'build_deps': (
        "check-tools", "data-hal", "libswrate", "sipwise-base", "mediaproxy-ng",
        "ngcp-schema", "rtpengine", "libtcap", "libinewrate"
    ),
    'projects': (
        "asterisk",
        "asterisk-sounds",
        "asterisk-voicemail",
        "backup-tools",
        "bulk-processor",
        "bulk-processor-projects",
        "bootenv",
        "captagent",
        "cdr-exporter",
        "cfg-schema",
        "check-tools",
        "cleanup-tools",
        "cloudpbx-devices",
        "cloudpbx-sources",
        "collectd-mod-redis",
        "comx",
        "comx-application",
        "comx-fileshare-service",
        "comx-sip",
        "comx-xmpp",
        "csta-testsuite",
        "data-hal",
        "db-schema",
        "dhtest",
        "diva-drivers",
        "deployment-iso",
        "documentation",
        "faxserver",
        "glusterfs-config",
        "heartbeat",
        "hylafaxplus",
        "iaxmodem",
        "installer",
        "janus-admin",
        "janus-client",
        "kamailio",
        "kamailio-config-tests",
        "keyring",
        "kibana",
        "klish",
        "libhsclient-c-wrapper",
        "libinewrate",
        "libswrate",
        "libtcap",
        "license-client",
        "lnpd",
        "lua-ngcp-kamailio",
        "mediaproxy-ng",
        "mediaproxy-redis",
        "mediator",
        "megacli",
        "metapackages",
        "monitoring-tools",
        "netscript",
        "ngcp-api-tools",
        "ngcp-csc",
        "ngcp-csc-ui",
        'ngcp-exporter',
        "ngcp-fauditd",
        "ngcp-inventory",
        "ngcp-klish-config",
        "ngcp-logfs",
        "ngcp-panel",
        "ngcp-prompts",
        "ngcp-rtcengine",
        "ngcp-schema",
        "ngcp-status",
        "ngcp-sudo-plugin",
        "ngcp-support",
        "ngcp-user-framework",
        "ngcpcfg",
        "ngcpcfg-api",
        "ngcpcfg-ha",
        "ngrep-sip",
        "ossbss",
        "prosody",
        "pushd",
        "rate-o-mat",
        "reminder",
        "rtpengine",
        "rtpengine-redis",
        "sems",
        "sems-app",
        "sems-ha",
        "sems-modules",
        "sems-pbx",
        "sems-prompts",
        "sipsak",
        "sipwise-base",
        "snmp-agent",
        "system-tests",
        "system-tools",
        "templates",
        "upgrade",
        "vmnotify",
        "voisniff-ng",
        "websocket",
        "www_admin",
        "www_csc"
    ),
    'abandoned': (
        "acc-cdi",
        "asterisk",
        "asterisk-sounds",
        "cloudpbx-devices",
        "collectd-mod-redis",
        "comx",
        "comx-sip",
        "comx-xmpp",
        "diva-drivers",
        "hylafaxplus",
        "iaxmodem",
        "mediaproxy-ng",
        "mediaproxy-redis",
        "rtpengine-redis",
        "ossbss",
        "sems-prompts",
        "sipsak",
        "www_admin",
        "www_csc",
    ),
    'docker_projects': (
        "comx-fileshare-service",
        "data-hal",
        "documentation",
        "janus-admin",
        "janus-client",
        "kamailio-config-tests",
        "libswrate",
        "libtcap",
        "lua-ngcp-kamailio",
        "ngcp-csc",
        "ngcp-panel",
        "ngcp-rtcengine",
        "ngcpcfg",
        "rate-o-mat",
        "snmp-agent",
        "system-tools",
    ),
}
