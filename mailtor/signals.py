from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import MailTemplateEntity

@receiver(pre_save, sender=MailTemplateEntity)
def send_instant_mail(sender, instance, *args, **kwargs):
    instance.token = instance.token.upper()