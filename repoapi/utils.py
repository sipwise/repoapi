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
import urllib2
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def openurl(URL):
    req = urllib2.Request(URL)
    response = urllib2.urlopen(req)
    if response.code is 200:
        print "OK"
        return 0
    else:
        print "Error retrieving %s" % URL
        return 1


def jenkins_remove_ppa(repo):
    url = "%s/job/remove-reprepro-codename/buildWithParameters?"\
        "token=%s&repository=%s" % \
        (settings.JENKINS_URL, settings.JENKINS_TOKEN, repo)
    if settings.DEBUG:
        logger.info("I would call %s" % url)
    else:
        openurl(url)


def workfront_note_send(_id, message):
    """TODO"""
    pass
