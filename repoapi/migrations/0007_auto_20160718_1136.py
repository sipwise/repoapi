# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-07-18 11:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('repoapi', '0006_auto_20160714_1359'),
    ]

    operations = [
        migrations.AddField(
            model_name='workfrontnoteinfo',
            name='eventtype',
            field=models.CharField(default='patchset-created', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='workfrontnoteinfo',
            unique_together=set(
                [('workfront_id', 'gerrit_change', 'eventtype')]),
        ),
    ]
