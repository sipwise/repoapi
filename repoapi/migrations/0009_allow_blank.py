# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-03-04 09:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("repoapi", "0008_auto_20170609_1954"),
    ]

    operations = [
        migrations.AlterField(
            model_name="jenkinsbuildinfo",
            name="gerrit_change",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="jenkinsbuildinfo",
            name="gerrit_eventtype",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="jenkinsbuildinfo",
            name="gerrit_patchset",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="jenkinsbuildinfo",
            name="git_commit_msg",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="jenkinsbuildinfo",
            name="param_branch",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="jenkinsbuildinfo",
            name="param_distribution",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="jenkinsbuildinfo",
            name="param_ppa",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="jenkinsbuildinfo",
            name="param_release_uuid",
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name="jenkinsbuildinfo",
            name="param_tag",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="jenkinsbuildinfo",
            name="repo_name",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
