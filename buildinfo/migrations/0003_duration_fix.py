# Generated by Django 3.2.15 on 2022-12-16 13:56
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("buildinfo", "0002_ldap_grp_perms"),
    ]

    operations = [
        migrations.AlterField(
            model_name="buildinfo",
            name="duration",
            field=models.PositiveIntegerField(),
        ),
    ]
