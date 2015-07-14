# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('repoapi', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jenkinsbuildinfo',
            name='param_release',
            field=models.CharField(max_length=50, null=True, db_index=True),
        ),
        migrations.AlterIndexTogether(
            name='jenkinsbuildinfo',
            index_together=set([('param_release', 'projectname', 'tag'), ('param_release', 'projectname')]),
        ),
    ]
