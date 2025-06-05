build
=====

This app is in charge of the building process of releases.

It reads the yaml files from sipwise-repos-scripts package in order to
find out everything related to a release.

```python
REPOS_SCRIPTS_CONFIG_DIR = "/usr/share/sipwise-repos-scripts/config"
```

The [release yaml](fixtures/config/trunk.yml) file is the one source of truth related
to a release:

* debian_release
* release-mrX.Y[.Z]?: backports to be included in the release repository
* jenkins-jobs: jenkins jobs related info
* release_mirror: steps to do on release process

But for build the most important part of the file is ``jenkins-jobs``.
There are ``projects`` and ``build_deps`` defined.

``build_deps`` is a list of projects that are a build dependency of others. Like:

```yaml
jenkins-jobs:
  build_deps:
    data-hal:
      - ngcp-panel
    ngcp-schema:
      - ngcp-panel
    libinewrate:
      - sems-pbx
    libswrate:
      - kamailio
      - sems-pbx
    libtcap:
      - kamailio
      - lnpd
    sipwise-base:
      - ngcp-panel
      - ngcp-schema
    check-tools:
      - snmp-agent
```

In this example ``data-hal`` needs to be built *before* ``ngcp-panel``. ``sipwise-base`` has
to be built *before* ``ngcp-panel`` and ``ngcp-schema`` and so on.

``build`` app has the logic to resolve this dependency hierarchy so triggering the right project in the right moment.

``build`` triggers jenkins jobs and when the job finishes the next in the queue is triggered.
It keeps the info of what project has been triggered, built or failed.

``build`` depends on [repoapi](../repoapi/models/jbi.py) JenkinsBuildInfo
