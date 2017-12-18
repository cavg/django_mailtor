# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-16 19:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mailtor', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mail',
            name='mail_template',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mailtor.MailTemplate'),
        ),
        migrations.AlterField(
            model_name='mailtemplateentities',
            name='kind',
            field=models.IntegerField(choices=[(1, 'Direct'), (2, 'Image'), (3, 'Date'), (4, 'Time'), (5, 'Datetime'), (6, 'LINK')], default=1),
        ),
    ]
