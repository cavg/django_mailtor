# Generated by Django 2.0 on 2018-02-06 21:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mailtor', '0017_mail_opened_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mail',
            name='error_detail',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
