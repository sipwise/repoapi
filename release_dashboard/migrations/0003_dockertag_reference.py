# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-06-26 17:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('release_dashboard', '0002_dockerimage'),
    ]

    operations = [
        migrations.RunSQL(
            [("DELETE FROM release_dashboard_dockertag;", None)]),
        migrations.AddField(
            model_name='dockertag',
            name='reference',
            field=models.CharField(max_length=150, unique=True),
        ),
    ]
