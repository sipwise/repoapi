# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('repoapi', '0004_auto_20150723_0646'),
    ]

    operations = [
        migrations.AddField(
            model_name='jenkinsbuildinfo',
            name='git_commit',
            field=models.TextField(null=True),
        ),
    ]
