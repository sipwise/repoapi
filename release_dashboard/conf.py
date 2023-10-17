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
from django.conf import settings  # noqa
from appconf import AppConf


class ReleaseDashboardConf(AppConf):
    FILTER_TAGS = r"^refs/tags/(.+)$"
    FILTER_BRANCHES = r"^refs/heads/(.+)$"
    FILTER_MRXX = r"^mr[0-9]+\.[0-9]+$"
    FILTER_MRXXX = r"^mr[0-9]+\.[0-9]+\.[0-9]+$"
    PROJECTS = (
        "acc-cdi",
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
        "codec-chain",
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
        "ngcp-admin-ui",
        "ngcp-api-tools",
        "ngcp-csc",
        "ngcp-csc-ui",
        "ngcp-cudecs",
        "ngcp-cve-scanner",
        "ngcp-exporter",
        "ngcp-fauditd",
        "ngcp-freeswitch-appserv",
        "ngcp-inventory",
        "ngcp-js-api-client",
        "ngcp-klish-config",
        "ngcp-logfs",
        "ngcp-panel",
        "ngcp-prompts",
        "ngcp-rest-api",
        "ngcp-rtcengine",
        "ngcp-schema",
        "ngcp-status",
        "ngcp-sudo-plugin",
        "ngcp-support",
        "ngcp-task-agent",
        "ngcp-user-framework",
        "ngcp-web-tests-e2e",
        "ngcpcfg",
        "ngcpcfg-api",
        "ngcpcfg-ha",
        "ngrep-sip",
        "ossbss",
        "prosody",
        "pushd",
        "py-ngcp-kamailio",
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
        "www_csc",
    )
    DOCKER_PROJECTS = (
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
        "ngcp-rest-api",
        "ngcp-rtcengine",
        "ngcpcfg",
        "rate-o-mat",
        "snmp-agent",
        "system-tests",
        "system-tools",
    )

    class Meta:
        prefix = "release_dashboard"
