# Generated by Django 3.2.13 on 2022-06-14 16:12
from django.contrib.auth.management import create_permissions
from django.db import migrations


def add_permissions(apps, schema_editor):
    """ContentType table is populated after all the migrations applied"""
    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, verbosity=0)
        app_config.models_module = None


def forwards_func(apps, schema_editor):
    add_permissions(apps, schema_editor)
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")
    db_alias = schema_editor.connection.alias

    devops_grp = Group.objects.using(db_alias).get(name="devops")

    BuildInfo = apps.get_model("buildinfo", "BuildInfo")
    ct = ContentType.objects.get_for_model(BuildInfo)

    perm_codenames = []
    for perm in ("add", "change", "delete", "view"):
        perm_codenames.append(f"{perm}_buildinfo")

    for codename in perm_codenames:
        perm = Permission.objects.using(db_alias).get(
            content_type=ct, codename=codename
        )
        devops_grp.permissions.add(perm)


class Migration(migrations.Migration):

    dependencies = [
        ("buildinfo", "0001_initial"),
        ("repoapi", "0011_ldap_groups"),
    ]

    operations = [
        migrations.RunPython(forwards_func),
    ]
