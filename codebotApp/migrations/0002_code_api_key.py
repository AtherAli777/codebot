# Generated by Django 4.2 on 2023-05-05 08:40

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("codebotApp", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="code",
            name="api_key",
            field=models.CharField(default=django.utils.timezone.now, max_length=50),
            preserve_default=False,
        ),
    ]
