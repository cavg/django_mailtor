# Generated by Django 2.0 on 2017-12-19 18:50

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    replaces = [('mailtor', '0001_initial')]

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('attachment', models.FileField(blank=True, null=True, upload_to='attachment')),
            ],
            options={
                'verbose_name': 'Attachment',
                'verbose_name_plural': 'Attachments',
            },
        ),
        migrations.CreateModel(
            name='Mail',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('sender', models.CharField(max_length=100)),
                ('receptor_to', models.CharField(max_length=100)),
                ('receptor_cc', models.CharField(blank=True, max_length=100, null=True)),
                ('receptor_bcc', models.CharField(blank=True, max_length=100, null=True)),
                ('body', models.TextField()),
                ('subject', models.CharField(max_length=150)),
                ('deliver_at', models.DateTimeField(blank=True, null=True)),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Mail',
                'verbose_name_plural': 'Mails',
            },
        ),
        migrations.CreateModel(
            name='MailTemplate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=50)),
                ('body', models.TextField()),
                ('sender', models.CharField(max_length=100)),
                ('subject', models.CharField(max_length=150)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'MailTemplate',
                'verbose_name_plural': 'MailTemplates',
            },
        ),
        migrations.CreateModel(
            name='MailTemplateEntities',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=25)),
                ('arg_name', models.CharField(max_length=25)),
                ('instance_attr_name', models.CharField(blank=True, max_length=25, null=True)),
                ('kind', models.IntegerField(choices=[(1, 'Text'), (2, 'Image'), (3, 'Date'), (4, 'Time'), (5, 'Datetime'), (6, 'LINK')], default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'MailTemplateEntities',
                'verbose_name_plural': 'MailTemplateEntitiess',
            },
        ),
        migrations.AddField(
            model_name='mail',
            name='mail_template',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mailtor.MailTemplate'),
        ),
        migrations.AddField(
            model_name='attachment',
            name='mail',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mailtor.Mail'),
        ),
    ]