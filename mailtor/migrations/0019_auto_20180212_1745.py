# Generated by Django 2.0 on 2018-02-12 17:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mailtor', '0018_auto_20180206_2128'),
    ]

    operations = [
        migrations.AddField(
            model_name='mail',
            name='opened_at_last',
            field=models.DateTimeField(blank=True, default=None, null=True, verbose_name='Última apertura (Fecha)'),
        ),
        migrations.AlterField(
            model_name='mail',
            name='body',
            field=models.TextField(verbose_name='Mensaje'),
        ),
        migrations.AlterField(
            model_name='mail',
            name='deliver_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Fecha de envio programada'),
        ),
        migrations.AlterField(
            model_name='mail',
            name='opened_at',
            field=models.DateTimeField(blank=True, default=None, null=True, verbose_name='Aperturado (Fecha)'),
        ),
        migrations.AlterField(
            model_name='mail',
            name='receptor_bcc',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Copia oculta (BCC)'),
        ),
        migrations.AlterField(
            model_name='mail',
            name='receptor_cc',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Destinatario en copia (CC)'),
        ),
        migrations.AlterField(
            model_name='mail',
            name='receptor_to',
            field=models.CharField(max_length=100, verbose_name='Destinatario (To)'),
        ),
        migrations.AlterField(
            model_name='mail',
            name='sender',
            field=models.CharField(max_length=100, verbose_name='Remitente'),
        ),
        migrations.AlterField(
            model_name='mail',
            name='sent_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Fecha de envio'),
        ),
        migrations.AlterField(
            model_name='mail',
            name='subject',
            field=models.CharField(max_length=150, verbose_name='Asunto'),
        ),
    ]
