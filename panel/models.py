# Copyright (C) 2020 The Sipwise Team - http://sipwise.com
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
# This is needed due to:
#
# AppConf classes depend on being imported during startup of the Django
# process. Even though there are multiple modules loaded automatically, only
# the models modules (usually the models.py file of your app) are guaranteed
# to be loaded at startup. Therefore it’s recommended to put your AppConf
# subclass(es) there, too.
#
# https://django-appconf.readthedocs.io/en/latest/
from .conf import settings  # noqa
