# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('repoapi', '0003_gerritrepoinfo'),
    ]

    operations = [
        migrations.AddField(
            model_name='gerritrepoinfo',
            name='gerrit_change',
            field=models.CharField(default='fake', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='gerritrepoinfo',
            name='param_ppa',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterUniqueTogether(
            name='gerritrepoinfo',
            unique_together=set([('param_ppa', 'gerrit_change')]),
        ),
        migrations.RemoveField(
            model_name='gerritrepoinfo',
            name='count',
        ),
    ]
