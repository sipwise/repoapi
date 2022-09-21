# Copyright (C) 2022 The Sipwise Team - http://sipwise.com
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
from django.shortcuts import get_object_or_404
from django.views.generic.base import RedirectView

from .conf import MapperType
from .conf import TrackerConf
from .models import TrackerMapper

tracker_settings = TrackerConf()


class WFIssueRedirectView(RedirectView):
    permanent = True
    query_string = True
    url = tracker_settings.MANTIS_MAPPER_URL

    def get_redirect_url(self, *args, **kwargs):
        issue = get_object_or_404(
            TrackerMapper.objects.get_workfront_issue_qs(
                kwargs["workfront_id"]
            ),
            mapper_type=MapperType.ISSUE,
        )
        return self.url.format(mantis_id=issue.mantis_id)


class WFTaskRedirectView(RedirectView):
    permanent = True
    query_string = True
    url = tracker_settings.MANTIS_MAPPER_URL

    def get_redirect_url(self, *args, **kwargs):
        issue = get_object_or_404(
            TrackerMapper.objects.get_workfront_task_qs(
                kwargs["workfront_id"]
            ),
            mapper_type=MapperType.TASK,
        )
        return self.url.format(mantis_id=issue.mantis_id)


class WFRedirectView(RedirectView):
    permanent = True
    query_string = True
    url = tracker_settings.MANTIS_MAPPER_URL

    def get_redirect_url(self, *args, **kwargs):
        wf = get_object_or_404(
            TrackerMapper.objects.get_wf_qs(
                [
                    kwargs["workfront_id"],
                ]
            )
        )
        return self.url.format(mantis_id=wf.mantis_id)
