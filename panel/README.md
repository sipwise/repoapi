panel
=====

This is mainly the interface of [repoapi](../repoapi/models/jbi.py). There are some panels
for releases and projects.

Panels use [boostrap v3.3.7](panel/static/panel/js/bootstrap.min.js) toolkit and
[django-assets](https://django-assets.readthedocs.io/en/latest/staticfiles.html)

There's some javascript logic at [panel*.js](panel/static/panel/js/panel_release.js).
It will make things dynamic so build results will appear with refresh the whole page
and some other tricks.
