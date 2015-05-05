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
            name='tag',
            field=models.CharField(max_length=64, null=True),
        ),
    ]
