release_dashboard
=================

dashboard for:

* build releases: [build app](../build)
* docker images:
  we can trigger the proper jenkins job to rebuild Dockerfiles at any ``DOCKER_PROJECTS``
* hotfixes: triggers the proper jenkins job for ``PROJECTS``
* gerrit: info related to tags needed for hotfixes

There's some [javascript logic](release_dashboard/static/release_dashboard/js)
