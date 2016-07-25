# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-07-26 12:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='WorkfrontNoteInfo',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID')),
                ('workfront_id', models.CharField(max_length=50)),
                ('projectname', models.CharField(max_length=50)),
                ('version', models.CharField(max_length=50)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='workfrontnoteinfo',
            unique_together=set(
                [('workfront_id', 'projectname', 'version')]),
        ),
    ]
