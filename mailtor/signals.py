from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .models import Mail

import datetime
import logging

logger = logging.getLogger(__name__)

# @receiver(post_save, sender=Mail)
# def send_instant_mail(sender, instance, created, **kwargs):
#     if created == True and instance.deliver_at is None:
#         instance.perform_send()