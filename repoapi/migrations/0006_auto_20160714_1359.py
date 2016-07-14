# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('repoapi', '0005_jenkinsbuildinfo_git_commit'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkfrontNoteInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('workfront_id', models.CharField(max_length=50)),
                ('gerrit_change', models.CharField(max_length=50)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='workfrontnoteinfo',
            unique_together=set([('workfront_id', 'gerrit_change')]),
        ),
    ]
