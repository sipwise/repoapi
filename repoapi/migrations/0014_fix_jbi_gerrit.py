import re

from django.db import migrations

RE_GERRIT = re.compile("-gerrit$")


def forwards_func(apps, schema_editor):
    JenkinsBuildInfo = apps.get_model("repoapi", "JenkinsBuildInfo")
    qs = JenkinsBuildInfo.objects.filter(projectname__endswith="-gerrit")
    for jbi in qs:
        jbi.update(projectname=RE_GERRIT.sub("", jbi.projectname))


class Migration(migrations.Migration):

    dependencies = [
        ("repoapi", "0013_mantisnoteinfo"),
    ]

    operations = [
        migrations.RunPython(forwards_func),
    ]
