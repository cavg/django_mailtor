from django.db import models
from django.apps import apps
from django.conf import settings
from django.utils import timezone
from django.core.mail import EmailMessage
from pytz import timezone as tz

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
    DIRECT_KIND = 1
    IMG_KIND = 2
    DATE_KIND = 3
    TIME_KIND = 4
    DATETIME_KIND = 5
    LINK_KIND = 6
    KIND_CHOICES = (
        (DIRECT_KIND, 'Direct'),
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
    def get_replacement(self, mode_html, **kwargs):
        if self.instance_attr_name is None:
            for arg_name, value in kwargs.items():
                    if arg_name == self.arg_name:
                        return self.get_value_by_kind(value, mode_html)
        else:
            if self.arg_name is not None:
                for arg_name, instance in kwargs.items():
                    if arg_name == self.arg_name:
                        value = getattr(instance, self.instance_attr_name)
                        return self.get_value_by_kind(value, mode_html)


    def get_value_by_kind(self, value = None, mode_html = False):
        if self.kind == MailTemplateEntities.DIRECT_KIND:
            return value
        elif self.kind == MailTemplateEntities.IMG_KIND:
            if mode_html:
                return "<img src='{}' alt='{}'>".format(value, value)
            else:
                return value
        elif self.kind == MailTemplateEntities.DATE_KIND:
            return value.strftime(settings.MAILTOR_DATE_FORMAT)
        elif self.kind == MailTemplateEntities.TIME_KIND:
            return value.strftime(settings.MAILTOR_TIME_FORMAT)
        elif self.kind == MailTemplateEntities.DATETIME_KIND:
            return value.strftime(settings.MAILTOR_DATETIME_FORMAT)
        elif self.kind == MailTemplateEntities.LINK_KIND:
            if mode_html:
                return "<a href='{}' target='_blank'>{}</a>".format(value, value)
            else:
                return value
        else:
            return None


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
    mode_html = models.BooleanField(default=False, null=False, blank=False)
    deliver_at = models.DateTimeField(blank=True, null=True) # None means at creation moment
    sent_at = models.DateTimeField(blank=True, null=True)

    mail_template = models.ForeignKey(MailTemplate, on_delete=models.CASCADE, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Mail"
        verbose_name_plural = "Mails"

    def __str__(self):
        return "Sender:{}, receptor_to:{}, deliver_at:{}, template:{}".format(self.sender, self.receptor_to, self.deliver_at, self.mail_template)

    @classmethod
    def get_token(self):
        return getattr(settings, 'MAILTOR_ESCAPE_TOKEN', "###")

    """ Populate body using params
    Args:
        body(str): Mail body
        **body_args: All args required to obtain values to replace in email body
    Returns:
        body populated (str), keys not found in MailTemplateEntities(list), keys not founds in args (list)
    """
    @classmethod
    def populate_body(self, body, mode_html, **body_args):
        token = Mail.get_token()
        keys = re.findall("({}+[\w\d.+-]+{})".format(token, token), body)
        not_found_keys = []
        not_found_args = []
        keys = list(set(keys))
        for key in keys:
            try:
                mte = MailTemplateEntities.objects.get(token = key.replace(token,""))
                replacement = mte.get_replacement(mode_html, **body_args)
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
        body (str): mail content
        subject (str): mail subject
        receptor (str): destinatary
        receptor_cc (str): copy to
        receptor_bcc (str): hide copy to
        deliver_at (datetime): deliver datetime (without tz)
        mail_template (MailTemplate) = Mail will build based on this entity, optional param
        **body_args: All args required to obtain values to replace in email body
    Returns:
        Mail entity (already created)

    """
    @classmethod
    def build(self, sender = None, body = None, subject = None, receptor_to = None, receptor_cc =  None, receptor_bcc = None, deliver_at = None, mail_template = None, mode_html = False, **body_args):
        if deliver_at is not None:
            deliver_at = deliver_at.astimezone(tz(settings.TIME_ZONE))

        to_send = sender if sender is not None else mail_template.sender

        subject = subject if subject is not None else mail_template.subject

        body = body if body is not None else mail_template.body

        if None in [to_send, subject, body, receptor_to]:
            logger.error("Mail require at least to_send, subject, receptor_to and body fields.\nto_send:{},\nsubject:{},\nbody:{},\nreceptor_to:{}".format(to_send, subject, body, receptor_to))
            return None, [], []

        body, nf_keys, nt_args = Mail.populate_body(body, mode_html, **body_args)

        if (len(nf_keys) + len(nt_args)) > 0:
            logger.error("Mail has replacement not populated.\nnf_keys:{},\n nt_args:{}\n".format(nf_keys, nt_args))
            return None, nf_keys, nt_args
        else:
            mail = Mail.objects.create(
                sender = to_send,
                receptor_to = receptor_to,
                receptor_cc = receptor_cc,
                receptor_bcc = receptor_bcc,
                body = body,
                subject = subject,
                mode_html = mode_html,
                deliver_at = deliver_at
            )

            return mail, nf_keys, nt_args

    """ Deliver mail
    Args:
        None
    Returns:
        True/False, With True sent_at iis time stamped
    """
    def send(self):
        try:
            email = EmailMessage(
                self.subject,
                self.body,
                self.sender,
                [self.receptor_to],
                [self.receptor_bcc],
                reply_to=[self.receptor_cc],
            )
            attachments = Attachment.objects.filter(mail = self)
            for attachment in attachments:
                if attachment.attachment is not None:
                    email.attach_file(attachment.attachment.path)

            email.send()

            self.sent_at = datetime.datetime.now().astimezone(tz(settings.TIME_ZONE))
            self.save()
            return True
        except Exception as e:
            logger.critical("Mail with id:{} couldn't send, {}".format(self.id, str(e)))
            return False




class Attachment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    attachment = models.FileField(upload_to='attachment', null=False, blank=False)

    mail = models.ForeignKey(Mail, on_delete=models.CASCADE, null=False, blank=False)

    class Meta:
        verbose_name = "Attachment"
        verbose_name_plural = "Attachments"

    def __str__(self):
        return "Attachment:{}, mail:{}".format(self.attachment, self.mail)


