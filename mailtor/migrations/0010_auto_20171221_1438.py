# Generated by Django 2.0 on 2017-12-21 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mailtor', '0009_auto_20171219_1846'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mail',
            name='mode_html',
            field=models.NullBooleanField(default=None),
        ),
    ]
