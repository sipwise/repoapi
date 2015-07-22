# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('repoapi', '0002_auto_20150714_0919'),
    ]

    operations = [
        migrations.CreateModel(
            name='GerritRepoInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('param_ppa', models.CharField(unique=True, max_length=50)),
                ('count', models.IntegerField(default=0)),
            ],
        ),
    ]
