# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-09-23 11:48
from __future__ import unicode_literals

from django.db import migrations, models
from django_extensions.db.fields import ModificationDateTimeField
from django_extensions.db.fields.json import JSONField


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('json_tags', JSONField(null=True)),
                ('json_branches', JSONField(null=True)),
                ('modified', ModificationDateTimeField(
                    auto_now=True, null=True)),
            ],
        ),
    ]