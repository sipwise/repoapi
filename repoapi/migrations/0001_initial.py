# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='JenkinsBuildInfo',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False,
                    auto_created=True, primary_key=True)),
                ('tag', models.CharField(max_length=64, null=True)),
                ('projectname', models.CharField(max_length=100)),
                ('jobname', models.CharField(max_length=100)),
                ('buildnumber', models.IntegerField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('result', models.CharField(max_length=50)),
                ('job_url', models.URLField()),
                ('gerrit_patchset', models.CharField(
                    max_length=50, null=True)),
                ('gerrit_change', models.CharField(max_length=50, null=True)),
                ('gerrit_eventtype', models.CharField(
                    max_length=50, null=True)),
                ('param_tag', models.CharField(max_length=50, null=True)),
                ('param_branch', models.CharField(max_length=50, null=True)),
                ('param_release', models.CharField(max_length=50, null=True)),
                ('param_distribution', models.CharField(
                    max_length=50, null=True)),
                ('param_ppa', models.CharField(max_length=50, null=True)),
                ('repo_name', models.CharField(max_length=50, null=True)),
            ],
        ),
    ]
