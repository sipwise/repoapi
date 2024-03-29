# Generated by Django 3.2.15 on 2022-09-14 18:31
from django.db import migrations
from django.db import models

import tracker.conf


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="TrackerMapper",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "mapper_type",
                    models.CharField(
                        choices=[
                            (tracker.conf.MapperType["ISSUE"], "Issue"),
                            (tracker.conf.MapperType["TASK"], "Task"),
                        ],
                        max_length=15,
                    ),
                ),
                ("mantis_id", models.CharField(max_length=50, unique=True)),
                ("workfront_id", models.CharField(max_length=50, unique=True)),
                (
                    "workfront_uuid",
                    models.CharField(max_length=50, unique=True),
                ),
            ],
        ),
    ]
