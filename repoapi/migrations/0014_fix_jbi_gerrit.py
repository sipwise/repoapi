import re

from django.db import migrations

RE_GERRIT = re.compile("-gerrit$")


def revert_func(apps, schema_editor):
    pass


def remove_gerrit(model):
    qs = model.objects.filter(projectname__endswith="-gerrit")
    for jbi in qs:
        jbi.projectname = RE_GERRIT.sub("", jbi.projectname)
        jbi.save()


def forwards_func(apps, schema_editor):
    JenkinsBuildInfo = apps.get_model("repoapi", "JenkinsBuildInfo")
    remove_gerrit(JenkinsBuildInfo)
    BuildInfo = apps.get_model("buildinfo", "BuildInfo")
    remove_gerrit(BuildInfo)


class Migration(migrations.Migration):

    dependencies = [
        ("repoapi", "0013_mantisnoteinfo"),
    ]

    operations = [
        migrations.RunPython(forwards_func, revert_func),
    ]
