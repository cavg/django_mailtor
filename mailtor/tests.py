from django.test import TestCase
from django.contrib.auth.models import User
from django.conf import settings
from django.core import mail

from .models import MailTemplateEntities, Mail, MailTemplate, Attachment

import datetime
import shutil

def _create_fixtures():
    MailTemplateEntities.objects.create(
        token = "NAME",
        arg_name = "user",
        instance_attr_name = "first_name",
        kind = MailTemplateEntities.DIRECT_KIND
    )

    User.objects.create(
        first_name = "User1322",
        last_name = "Recolector",
        email = "agent@empresa.cl",
        username = "agent@empresa.cl"
    )

    MailTemplateEntities.objects.create(
        token = "AGE",
        arg_name = "age",
        instance_attr_name = None,
        kind = MailTemplateEntities.DIRECT_KIND
    )

class MailTemplateEntitiesTestCase(TestCase):

    def setUp(self):
        _create_fixtures()


    def test_replacement_text(self):
        # Test MailTEmplateEntities creation
        mte1 = MailTemplateEntities.objects.get(token="NAME")
        self.assertEqual(mte1.arg_name, "user")

        # Testing replacement by entity's attr
        first_name = "User1322"
        user = User.objects.get(first_name=first_name)
        self.assertEqual(mte1.get_replacement(mode_html=False, user=user),first_name)

        # Testing replacement by regular param
        mte2 = MailTemplateEntities.objects.get(token="AGE")
        param = {'age':32}
        self.assertEqual(mte2.get_replacement(mode_html=False, **param),param['age'])

        # Testing attr not found
        self.assertEqual(mte2.get_replacement(mode_html=False, foo='faa'), None)

    def test_values_by_kind(self):
        # Case IMAGE
        mte = MailTemplateEntities.objects.create(
            token = "COMPANY_LOGO",
            arg_name = "image",
            instance_attr_name = None,
            kind = MailTemplateEntities.IMG_KIND
        )
        img_path = "http://cdn.website.com/image.png"
        result = mte.get_value_by_kind(img_path, mode_html = False)
        self.assertEqual(result, img_path)
        result = mte.get_value_by_kind(img_path, mode_html = True)
        self.assertEqual(result, "<img src='{}' alt='{}'>".format(img_path, img_path))

        # Case Date
        mte = MailTemplateEntities.objects.create(
            token = "DEBT_DATE",
            arg_name = "debt_date",
            instance_attr_name = None,
            kind = MailTemplateEntities.DATE_KIND
        )
        date = datetime.date(year=2017,month=5,day=21)
        result = mte.get_value_by_kind(date)
        self.assertEqual(result, date.strftime(settings.MAILTOR_DATE_FORMAT))

        # Case Time
        mte = MailTemplateEntities.objects.create(
            token = "DEBT_DATE",
            arg_name = "debt_date",
            instance_attr_name = None,
            kind = MailTemplateEntities.TIME_KIND
        )
        time = datetime.time(hour=23, minute=0, second=0)
        result = mte.get_value_by_kind(time)
        self.assertEqual(result, time.strftime(settings.MAILTOR_TIME_FORMAT))

        # Case Datetime
        mte = MailTemplateEntities.objects.create(
            token = "DEBT_DATE",
            arg_name = "debt_date_time",
            instance_attr_name = None,
            kind = MailTemplateEntities.DATETIME_KIND
        )
        dt = datetime.datetime(year=2017, month=5, day=21, hour=23, minute=0, second=0)
        result = mte.get_value_by_kind(dt)
        self.assertEqual(result, dt.strftime(settings.MAILTOR_DATETIME_FORMAT))

        # Case link
        mte = MailTemplateEntities.objects.create(
            token = "DEBT_DATE",
            arg_name = "debt_date",
            instance_attr_name = None,
            kind = MailTemplateEntities.LINK_KIND
        )
        link = "http://www.company.com/customer/payment"
        result = mte.get_value_by_kind(link, mode_html=True)
        self.assertEqual(result, "<a href='{}' target='_blank'>{}</a>".format(link, link))

class MailTestCase(TestCase):

    token = None

    def setUp(self):
        self.token = Mail.get_token()
        _create_fixtures()

    def test_populate_body(self):
        # Testing replacement entity and not found args
        body = "Hello {}NAME{}, This is an example of populate body email, your age is {}AGE{}?".format(self.token, self.token, self.token, self.token)
        user = User.objects.get(first_name="User1322")
        populate_body, _, nt_args = Mail.populate_body(body=body, mode_html = False, user=user)
        body_expected = "Hello {}, This is an example of populate body email, your age is {}AGE{}?".format(user.first_name, self.token, self.token)
        self.assertEqual(body_expected, populate_body)
        self.assertEqual(nt_args, ['AGE'])

        # Combine entity with dict
        age = 32
        body = "Hello {}NAME{}, This is an example of populate body email, your age is {}AGE{}? are you sure {}AGE{} is?".format(self.token, self.token, self.token, self.token, self.token, self.token)
        body_expected = "Hello {}, This is an example of populate body email, your age is {}? are you sure {} is?".format(user.first_name, age, age)
        populate_body, _, _ = Mail.populate_body(body=body, mode_html = False, user=user, age = age)
        self.assertEqual(body_expected, populate_body)

        # Testing not found key
        body = "Hello {}LAST_NAME{}".format(self.token, self.token)
        body_expected = "Hello {}LAST_NAME{}".format(self.token, self.token)
        populate_body, nf_keys, _ = Mail.populate_body(body=body, mode_html = False)
        self.assertEqual(nf_keys, ['LAST_NAME'])

    def test_build(self):
        body = "Hello {}NAME{}, This is an example of populate body email".format(self.token, self.token)
        mt = MailTemplate.objects.create(
            name = "template-email1",
            body = body,
            sender = "Camilo Verdugo <asdf@gmail.com>",
            subject = "Subject emails"
        )
        user = User.objects.get(first_name="User1322")
        mail, nf_keys, nf_args = Mail.build(
            receptor_to = "User <userr@gmail.com>",
            mail_template = mt,
            mode_html = False,
            user=user # body args
        )
        self.assertEqual(type(mail), Mail)
        self.assertEqual(nf_keys, [])
        self.assertEqual(nf_args, [])

        # Testing successfull delivery
        mail.send()
        self.assertEqual(type(mail.sent_at), datetime.datetime)

        # Test no specify receptor_to
        mail, nf_keys, nf_args = Mail.build(
            mail_template = mt,
            mode_html = False,
            user=user # body args
        )
        self.assertEqual(mail, None)

    def test_build_mail_mode_html(self):
        mte = MailTemplateEntities.objects.create(
            token = "ACTIVATION_LINK",
            arg_name = "activation_link",
            instance_attr_name = None,
            kind = MailTemplateEntities.LINK_KIND
        )
        body = "Hello active your account at {}ACTIVATION_LINK{}".format(self.token, self.token)
        mt = MailTemplate.objects.create(
            name = "template-email1",
            body = body,
            sender = "Camilo Verdugo <asdf@gmail.com>",
            subject = "Subject emails"
        )
        link = "http://www.company.com/activation?foo"
        mail, nf_keys, nf_args = Mail.build(
            receptor_to = "User <userr@gmail.com>",
            mail_template = mt,
            mode_html = True,
            activation_link = link
        )
        self.assertEqual(type(mail), Mail)
        self.assertEqual(nf_keys, [])
        self.assertEqual(nf_args, [])
        expected_result = "Hello active your account at <a href='{}' target='_blank'>{}</a>".format(link, link)
        self.assertEqual(mail.body, expected_result)

    def test_send(self):
        subject = "Greetings from Awesome Company!"
        email = Mail.objects.create(
            sender = "Company No Reply <no-reply@company.com>",
            receptor_to = "Customer <customer@customer.com>",
            body = "Hello Dear Customer!",
            subject = subject,
            mode_html = False,
            deliver_at = None
        )

        from django.core.files import File
        f = open("test.txt", "r")
        at = Attachment.objects.create(
            attachment = File(f),
            mail = email
        )
        f.close()

        path = "{}/attachment".format(settings.BASE_DIR)

        email.send()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, subject)
        self.assertEqual(len(mail.outbox[0].attachments), 1)

        shutil.rmtree(path)
