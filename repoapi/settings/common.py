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
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from os.path import abspath
from os.path import dirname
from os.path import join

from configurations import Configuration
from configurations import values


class Common(Configuration):
    BASE_DIR = dirname(dirname(dirname(abspath(__file__))))
    PROJECT_APPS = [
        "repoapi.apps.RepoAPIConfig",
        "hotfix.apps.HotfixConfig",
        "panel.apps.PanelConfig",
        "release_dashboard.apps.ReleaseDashboardConfig",
        "build.apps.ReleaseConfig",
    ]
    INSTALLED_APPS = [
        "object_tools",
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "rest_framework",
        "rest_framework_api_key",
        "rest_framework_swagger",
        "django_assets",
        "django_celery_results",
        "django_extensions",
        "django_filters",
        "jsonify",
        "export",
    ] + PROJECT_APPS

    MIDDLEWARE_CLASSES = (
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.auth.middleware.SessionAuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
        "django.middleware.security.SecurityMiddleware",
    )

    ROOT_URLCONF = "repoapi.urls"
    LOGIN_URL = "rest_framework:login"
    LOGOUT_URL = "rest_framework:logout"
    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": ["repoapi/templates"],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
            },
        },
    ]

    WSGI_APPLICATION = "repoapi.wsgi.application"

    # Internationalization
    # https://docs.djangoproject.com/en/1.8/topics/i18n/
    LANGUAGE_CODE = "en-us"
    TIME_ZONE = "UTC"
    USE_I18N = True
    USE_L10N = True
    USE_TZ = True

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/1.8/howto/static-files/
    STATIC_URL = "/static/"

    STATICFILES_FINDERS = (
        "django.contrib.staticfiles.finders.FileSystemFinder",
        "django.contrib.staticfiles.finders.AppDirectoriesFinder",
        "django_assets.finders.AssetsFinder",
    )

    STATIC_ROOT = join(BASE_DIR, "static_media/")

    REST_FRAMEWORK = {
        "PAGE_SIZE": 10,
        "DEFAULT_FILTER_BACKENDS": (
            "rest_framework.filters.DjangoFilterBackend",
        ),
    }

    SWAGGER_SETTINGS = {
        "api_version": "0.1",
        "info": {
            "contact": "dev@sipwise.com",
            "description": "repoapi, one ring to rule them all",
            "license": "GPL 3.0",
            "title": "RepoApi",
        },
    }
    LOG_LEVEL = values.Value("INFO")

    JENKINS_TOKEN = "sipwise_jenkins_ci"

    CELERY_TASK_SERIALIZER = "json"
    CELERY_RESULT_SERIALIZER = "json"
    CELERY_ACCEPT_CONTENT = ["json"]
    CELERY_RESULT_BACKEND = "django-db"

    @property
    def LOGGING(self):
        val = {
            "version": 1,
            "disable_existing_loggers": False,
            "handlers": {"console": {"class": "logging.StreamHandler"}},
            "loggers": {
                "repoapi": {"handlers": ["console"], "level": self.LOG_LEVEL},
            },
        }
        return val
