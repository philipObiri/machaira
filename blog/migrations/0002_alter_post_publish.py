# Generated by Django 4.2 on 2023-05-01 19:52

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="post",
            name="publish",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]