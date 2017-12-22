from django.db import models
from django.apps import apps
from django.conf import settings
from django.forms import ModelForm
from django.utils import timezone
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.db.models import Q

from pytz import timezone as tz
from mailtor.html_parser import MyHTMLParser

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

    @classmethod
    def build(self, _class = None, **kwargs):
        obj = _class(**kwargs)
        obj.save()
        return obj

    class Meta:
        verbose_name = "MailTemplate"
        verbose_name_plural = "MailTemplates"

    def __str__(self):
        return "Name:{}, subject:{}".format(self.name, self.subject)


class MailTemplateEntity(models.Model):
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
        (LINK_KIND, 'Link')
    )

    token = models.CharField(max_length=25, blank=False, null=False)

    arg_name = models.CharField(max_length=25, blank=False, null=False)
    instance_attr_name = models.CharField(max_length=25, blank=True, null=True)

    kind = models.IntegerField(choices=KIND_CHOICES, default=1, null=False, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def build(self, _class = None, **kwargs):
        obj = _class(**kwargs)
        obj.save()
        return obj

    """ Get token by token name
    Args:
        _class (Class)
        token (str)
        filters (array<Q>) extra filters for _class
    Returns:
        _class(object)

    """
    @classmethod
    def _get_by_token(self, _class, token, extra_filters = []):
        queries = []
        queries.append(Q(token=token))
        if extra_filters is not None:
            for f in extra_filters:
                queries.append(f)
        tokens = _class.objects.filter(*queries)
        if tokens.count() == 1:
            return tokens[0]
        else:
            return None

    class Meta:
        verbose_name = "MailTemplateEntity"
        verbose_name_plural = "MailTemplateEntitys"

    @classmethod
    def _get_escape(self):
        return getattr(settings, 'MAILTOR_ESCAPE_TOKEN', "###")

    """ Obtain replacement values according a instance_attr_name
        If instance_attr_name is not None then correspond a property's instance
    Args:
        **kwargs (dict): entities to replace
    Returns:
        str: value replaced if exist otherwise None

    """
    def _get_replacement(self, **kwargs):
        if self.instance_attr_name is None:
            return self._get_value_by_kind(self.arg_name)
        else:
            if self.arg_name is not None:
                for arg_name, instance in kwargs.items():
                    if arg_name == self.arg_name:
                        value = getattr(instance, self.instance_attr_name)
                        return self._get_value_by_kind(value)


    def _get_value_by_kind(self, value = None):
        if self.kind == MailTemplateEntity.DIRECT_KIND:
            return value
        elif self.kind == MailTemplateEntity.IMG_KIND:
            return "<img src='{}' alt='{}'>".format(value, value)
        elif self.kind == MailTemplateEntity.DATE_KIND:
            return value.strftime(settings.MAILTOR_DATE_FORMAT)
        elif self.kind == MailTemplateEntity.TIME_KIND:
            return value.strftime(settings.MAILTOR_TIME_FORMAT)
        elif self.kind == MailTemplateEntity.DATETIME_KIND:
            return value.strftime(settings.MAILTOR_DATETIME_FORMAT)
        elif self.kind == MailTemplateEntity.LINK_KIND:
            return "<a href='{}' target='_blank'>{}</a>".format(value, value)

    def __str__(self):
        return "Token:{}, arg_name:{}, Kind:{}, instance_attr_name:{}".format(self.token, self.arg_name, self.kind, self.instance_attr_name)

class MailTemplateEntityForm(ModelForm):
    class Meta:
        model = MailTemplateEntity
        fields = '__all__'


class Mail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    sender = models.CharField(max_length=100, null=False, blank=False)
    receptor_to = models.CharField(max_length=100, null=False, blank=False)
    receptor_cc = models.CharField(max_length=100, null=True, blank=True)
    receptor_bcc = models.CharField(max_length=100, null=True, blank=True)
    body = models.TextField(blank=False, null=False)
    subject = models.CharField(max_length=150, null=False, blank=False)
    mode_html = models.NullBooleanField(default=None, null=True, blank=True)
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

    """ Populate body using params
    Args:
        body(str): Mail body
        **body_args: All args required to obtain values to replace in email body
    Returns:
        body populated (str), keys not found in MailTemplateEntity(list), keys not founds in args (list)
    """
    @classmethod
    def _populate_body(self, _class = None, body = '', extra_filters = [], **body_args):
        token = _class._get_escape()
        keys = re.findall("({}+[\w\d.+-]+{})".format(token, token), body)
        not_found_keys = []
        not_found_args = []
        keys = list(set(keys))
        for key in keys:
                mte = _class._get_by_token(_class, key.replace(token,""), extra_filters)
                if mte:
                    replacement = mte._get_replacement(**body_args)
                    if replacement is not None:
                        body = body.replace(key, str(replacement))
                    else:
                        not_found_args.append(key.replace(token,""))
                elif mte is None:
                    not_found_keys.append(key.replace(token,""))
        return body, not_found_keys, not_found_args

    """ Replace template body tags for values an create an instance of Mail
    Args:
        filter (array<Q>): using to filter MailTemplateEntities
        mail_fields (dict): All args required to obtain values to replace in email body
        body_args (dict): All args required to obtain values to replace in email body
    Hint:
        For deliver_at: deliver_at.astimezone(tz(settings.TIME_ZONE))
    Returns:
        mail (Mail)
        not_found_keys (array): not found keys in body
        not_found_args (array): not found replacement params
    """
    @classmethod
    def build(self, mail_class = None, entity_class = None, extra_filters = [] ,mail_fields = {}, body_args = {}):
        body = None
        nf_keys = []
        nt_args = []

        if len(['body', 'sender', 'receptor_to', 'subject'] -  mail_fields.keys()) == 0:
            body, nf_keys, nt_args = mail_class._populate_body(
                entity_class,
                mail_fields.get('body'),
                extra_filters,
                **body_args
            )
            mail_fields['body'] = body
            if (len(nf_keys) + len(nt_args)) > 0 or body is None:
                logger.error("Mail has replacement not populated.\nnf_keys:{},\n nt_args:{}\n".format(nf_keys, nt_args))
                return None, nf_keys, nt_args
            else:
                m = mail_class(
                    **mail_fields
                )
                m.save()

                return m, nf_keys, nt_args
        else:
            return None, nf_keys, nt_args


    """ Deliver mail
    Args:
        None
    Returns:
        True/False, With True sent_at iis time stamped
    """
    def send(self):
        parser = MyHTMLParser()
        parser.feed(self.body)
        mode_html = parser.is_html()

        try:
            if mode_html:
                email = EmailMultiAlternatives(
                    self.subject,
                    parser.get_plain_text(),
                    self.sender,
                    [self.receptor_to],
                    [self.receptor_bcc],
                    reply_to=[self.receptor_cc],
                )
                email.content_subtype = "html"
                email.attach_alternative(self.body, "text/html")
            else:
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
            self.mode_html = mode_html
            self.save()
            return True
        except Exception as e:
            logger.critical("Mail with id:{} couldn't send, {}".format(self.id, str(e)))
            return False


class Attachment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    attachment = models.FileField(upload_to='attachment', null=False, blank=False)

    mail = models.ForeignKey(Mail, on_delete=models.CASCADE, null=False, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Attachment"
        verbose_name_plural = "Attachments"

    def __str__(self):
        return "Attachment:{}, mail:{}".format(self.attachment.name, self.mail)


