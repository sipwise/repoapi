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

from django.conf import settings

if settings.DEBUG:
    PROJECTS = ("fake",)
else:
    PROJECTS = (
        "acc-cdi",
        "asterisk",
        "asterisk-sounds",
        "backup-tools",
        "bootenv",
        "captagent",
        "cdr-exporter",
        "cfg-schema",
        "check-tools",
        "cleanup-tools",
        "cloudpbx-devices",
        "collectd-mod-redis",
        "comx",
        "comx-sip",
        "comx-xmpp",
        "data-hal",
        "db-schema",
        "diva-drivers",
        "documentation",
        "heartbeat",
        "hylafaxplus",
        "iaxmodem",
        "installer",
        "kamailio",
        "kamailio-config-tests",
        "keyring",
        "kibana",
        "klish",
        "libswrate",
        "libtcap",
        "license-client",
        "lua-ngcp-kamailio",
        "mediaproxy-ng",
        "mediaproxy-redis",
        "mediator",
        "megacli",
        "metapackages",
        "monitoring-tools",
        "netscript",
        "ngcp-klish-config",
        "ngcp-panel",
        "ngcp-prompts",
        "ngcp-schema",
        "ngcp-status",
        "ngcp-support",
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
        "sems-ha",
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
        "www_admin",
        "www_csc"
    )
