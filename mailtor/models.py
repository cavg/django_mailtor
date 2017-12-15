from django.db import models
from django.apps import apps
from django.conf import settings

import uuid
import re
import datetime
import logging

logger = logging.getLogger(__name__)

class MailTemplate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=50, blank=False, null=False)
    body = models.TextField(blank=False, null=False)
    sender = models.CharField(max_length=100, null=False, blank=False)
    subject = models.CharField(max_length=150, null=False, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "MailTemplate"
        verbose_name_plural = "MailTemplates"

    def __str__(self):
        return "Name:{}, subject:{}".format(self.name, self.subject)


class MailTemplateEntities(models.Model):
    TEXT_KIND = 1
    IMG_KIND = 2
    DATE_KIND = 3
    TIME_KIND = 4
    DATETIME_KIND = 5
    LINK_KIND = 6
    KIND_CHOICES = (
        (TEXT_KIND, 'Text'),
        (IMG_KIND, 'Image'),
        (DATE_KIND, 'Date'),
        (TIME_KIND, 'Time'),
        (DATETIME_KIND, 'Datetime'),
        (LINK_KIND, 'LINK')
    )

    token = models.CharField(max_length=25, blank=False, null=False)

    arg_name = models.CharField(max_length=25, blank=False, null=False)
    instance_attr_name = models.CharField(max_length=25, blank=True, null=True)

    kind = models.IntegerField(choices=KIND_CHOICES, default=1, null=False, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "MailTemplateEntities"
        verbose_name_plural = "MailTemplateEntitiess"


    """ Obtain replacement values according a instance_attr_name
        If instance_attr_name is not None then correspond a property's instance
    Args:
        **kwargs (dict): entities to replace
    Returns:
        str: value replaced if exist otherwise None

    """
    def get_replacement(self, **kwargs):
        if self.instance_attr_name is None:
            for arg_name, value in kwargs.items():
                    if arg_name == self.arg_name:
                        return value
        else:
            if self.arg_name is not None:
                for arg_name, instance in kwargs.items():
                    if arg_name == self.arg_name:
                        return getattr(instance, self.instance_attr_name)


    def __str__(self):
        return "Token:{}, arg_name:{}, Kind:{}, instance_attr_name:{}".format(self.token, self.arg_name, self.kind, self.instance_attr_name)


class Mail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    sender = models.CharField(max_length=100, null=False, blank=False)
    receptor_to = models.CharField(max_length=100, null=False, blank=False)
    receptor_cc = models.CharField(max_length=100, null=True, blank=True)
    receptor_bcc = models.CharField(max_length=100, null=True, blank=True)
    body = models.TextField(blank=False, null=False)
    subject = models.CharField(max_length=150, null=False, blank=False)
    deliver_at = models.DateTimeField(blank=True, null=True)
    sent_at = models.DateTimeField(blank=True, null=True)

    mail_template = models.ForeignKey(MailTemplate, on_delete=models.CASCADE, null=False, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Mail"
        verbose_name_plural = "Mails"

    @classmethod
    def get_token(self):
        return getattr(settings, 'ESCAPE_TOKEN', "###")

    """ Populate body using params
    Args:
        body(str): Mail body
        **body_args: All args required to obtain values to replace in email body
    Returns:
        body populated (str), keys not found in MailTemplateEntities(list), keys not founds in args (list)
    """
    @classmethod
    def populate_body(self, body, **body_args):
        token = Mail.get_token()
        keys = re.findall("({}+[\w\d.+-]+{})".format(token, token), body)
        not_found_keys = []
        not_found_args = []
        keys = list(set(keys))
        for key in keys:
            try:
                mte = MailTemplateEntities.objects.get(token = key.replace(token,""))
                replacement = mte.get_replacement(**body_args)
                if replacement is not None:
                    body = body.replace(key, str(replacement))
                else:
                    not_found_args.append(key.replace(token,""))
            except MailTemplateEntities.DoesNotExist:
                not_found_keys.append(key.replace(token,""))
        return body, not_found_keys, not_found_args

    """ Replace template body tags for values
    Args:
        sender (str): who send
        receptor (str): destinatary
        receptor_cc (str): copy to
        receptor_bcc (str): hide copy to
        deliver_at (datetime): deliver datetime (without tz)
        mail_template (MailTemplate) = Mail will build based on this entity
        **body_args: All args required to obtain values to replace in email body
    Returns:
        Mail entity (already created)

    """
    @classmethod
    def build_mail(sender = None, receptor_to = None, receptor_cc =  None, receptor_bcc = None, deliver_at = None, mail_template = None, **body_args):
        if deliver_at is None:
            deliver_at = datetime.datetime.now().astimezone(timezone(settings.TIME_ZONE))
        else:
            deliver_at = deliver_at.astimezone(timezone(settings.TIME_ZONE))

        to_send = sender if sender is not None else mail_template.sender
        if to_send is None:
            return None

        body, nf_keys, nt_args = Mail.populate_body(mail_template.body, **body_args)

        if (len(nf_keys) + len(nt_args)) > 0:
            return None, nf_keys, nt_args
        else:

            mail = Mail.objects.create(
                sender = to_send,
                receptor_to = receptor_to,
                receptor_cc = receptor_cc,
                receptor_bcc = receptor_bcc,
                body = body,
                subject = MailTemplate.subject,
                deliver_at = deliver_at
            )

            return mail, None, None

    def __str__(self):
        return "Sender:{}, receptor_to:{}, deliver_at:{}, template:{}".format(self.sender, self.receptor_to, self.deliver_at, self.mail_template)


class Attachment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    attachment = models.FileField(upload_to='attachment', null=True, blank=True)

    mail = models.ForeignKey(Mail, on_delete=models.CASCADE, null=False, blank=False)

    class Meta:
        verbose_name = "Attachment"
        verbose_name_plural = "Attachments"

    def __str__(self):
        return "Attachment:{}, mail:{}".format(self.attachment, self.mail)


