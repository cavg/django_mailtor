from django.test import TestCase
from django.contrib.auth.models import User
from django.conf import settings
from django.core import mail

from .models import MailTemplateEntity, Mail, MailTemplate, Attachment

import datetime
import shutil

def _create_fixtures():
    MailTemplateEntity.build(
        token = "NAME",
        arg_name = "user",
        instance_attr_name = "first_name",
        kind = MailTemplateEntity.DIRECT_KIND
    )

    User.objects.create(
        first_name = "User1322",
        last_name = "Recolector",
        email = "agent@empresa.cl",
        username = "agent@empresa.cl"
    )

    MailTemplateEntity.build(
        token = "AGE",
        arg_name = "32",
        instance_attr_name = None,
        kind = MailTemplateEntity.DIRECT_KIND
    )

class MailTemplateEntityTestCase(TestCase):

    def setUp(self):
        _create_fixtures()

    def test_replacement_text(self):
        mte1_email = MailTemplateEntity.build(
            token = "User.Email",
            arg_name = "user",
            instance_attr_name = "email",
            kind = MailTemplateEntity.DIRECT_KIND
        )
        self.assertEqual(mte1_email.token, mte1_email.token.upper())

        # Test MailTEmplateEntity creation
        mte1 = MailTemplateEntity.get_by_token("NAME")
        self.assertEqual(mte1.arg_name, "user")

        # Testing replacement by entity's attr
        first_name = "User1322"
        user = User.objects.get(first_name=first_name)
        self.assertEqual(mte1.get_replacement(mode_html=False, user=user), user.first_name)

        # Testing replacement by regular param
        mte2 = MailTemplateEntity.get_by_token("AGE")
        self.assertEqual(mte2.get_replacement(mode_html=False), mte2.arg_name)

    def test_values_by_kind(self):
        # Case IMAGE
        mte = MailTemplateEntity.build(
            token = "COMPANY_LOGO",
            arg_name = "image",
            instance_attr_name = None,
            kind = MailTemplateEntity.IMG_KIND
        )
        img_path = "http://cdn.website.com/image.png"
        result = mte.get_value_by_kind(img_path, mode_html = False)
        self.assertEqual(result, img_path)
        result = mte.get_value_by_kind(img_path, mode_html = True)
        self.assertEqual(result, "<img src='{}' alt='{}'>".format(img_path, img_path))

        # Case Date
        mte = MailTemplateEntity.build(
            token = "DEBT_DATE",
            arg_name = "debt_date",
            instance_attr_name = None,
            kind = MailTemplateEntity.DATE_KIND
        )
        date = datetime.date(year=2017,month=5,day=21)
        result = mte.get_value_by_kind(date)
        self.assertEqual(result, date.strftime(settings.MAILTOR_DATE_FORMAT))

        # Case Time
        mte = MailTemplateEntity.build(
            token = "DEBT_DATE",
            arg_name = "debt_date",
            instance_attr_name = None,
            kind = MailTemplateEntity.TIME_KIND
        )
        time = datetime.time(hour=23, minute=0, second=0)
        result = mte.get_value_by_kind(time)
        self.assertEqual(result, time.strftime(settings.MAILTOR_TIME_FORMAT))

        # Case Datetime
        mte = MailTemplateEntity.build(
            token = "DEBT_DATE",
            arg_name = "debt_date_time",
            instance_attr_name = None,
            kind = MailTemplateEntity.DATETIME_KIND
        )
        dt = datetime.datetime(year=2017, month=5, day=21, hour=23, minute=0, second=0)
        result = mte.get_value_by_kind(dt)
        self.assertEqual(result, dt.strftime(settings.MAILTOR_DATETIME_FORMAT))

        # Case link
        mte = MailTemplateEntity.build(
            token = "DEBT_DATE",
            arg_name = "debt_date",
            instance_attr_name = None,
            kind = MailTemplateEntity.LINK_KIND
        )
        link = "http://www.company.com/customer/payment"
        result = mte.get_value_by_kind(link, mode_html=True)
        self.assertEqual(result, "<a href='{}' target='_blank'>{}</a>".format(link, link))

class MailTestCase(TestCase):

    escape = None

    def setUp(self):
        self.escape = MailTemplateEntity.get_escape()
        _create_fixtures()

    def test_populate_body(self):
        # Testing replacement entity
        user = User.objects.get(first_name="User1322")
        mte_name = MailTemplateEntity.get_by_token("NAME")
        mte_age = MailTemplateEntity.get_by_token("AGE")
        body= "Hello {}{}{}, This is an example of populate body email, your age is {}{}{}?".format(self.escape, mte_name.token, self.escape, self.escape, mte_age.token, self.escape)
        age = 32
        body_populated, _, _ = Mail.populate_body(body=body, mode_html = False, filters = None, user=user, age=age)
        body_expected = "Hello {}, This is an example of populate body email, your age is {}?".format(user.first_name, age)
        self.assertEqual(body_populated, body_expected)

        # Testing not found and valid replacement args
        not_found = "NOT_FOUND"
        body = "Hello {}{}{}, This is an example of populate body email, your age is {}{}{}?".format(self.escape, mte_name.token, self.escape, self.escape, not_found, self.escape)
        populate_body, nf_keys, _ = Mail.populate_body(body=body, mode_html = False, filters=None, user=user)
        body_expected = "Hello {}, This is an example of populate body email, your age is {}{}{}?".format(user.first_name, self.escape, not_found, self.escape)
        self.assertEqual(body_expected, populate_body)
        self.assertEqual(nf_keys, [not_found])

        # Testing not found args
        body = "Hello {}{}{}, This is an example of populate body email, your age is {}{}{}?".format(self.escape, mte_name.token, self.escape, self.escape, mte_age.token, self.escape)
        body_populated, _, nf_args = Mail.populate_body(body=body, mode_html = False, filters=None)
        body_expected = "Hello {}{}{}, This is an example of populate body email, your age is {}?".format(self.escape, mte_name.token, self.escape, mte_age.arg_name)
        self.assertEqual(body_expected, body_populated)
        self.assertEqual(nf_args, [mte_name.token])

    def test_build(self):
        body = "Hello {}NAME{}, This is an example of populate body email".format(self.escape, self.escape)
        mt = MailTemplate.build(
            name = "template-email1",
            body = body,
            sender = "Camilo Verdugo <asdf@gmail.com>",
            subject = "Subject emails"
        )
        user = User.objects.get(first_name="User1322")
        mail, nf_keys, nf_args = Mail.build_populate(
            receptor_to = "User <userr@gmail.com>",
            mail_template = mt,
            mode_html = False,
            filters = None,
            user=user # body args
        )
        self.assertEqual(type(mail), Mail)
        self.assertEqual(nf_keys, [])
        self.assertEqual(nf_args, [])

        # Testing successfull delivery
        mail.send()
        self.assertEqual(type(mail.sent_at), datetime.datetime)

        # Test no specify receptor_to
        mail, nf_keys, nf_args = Mail.build_populate(
            mail_template = mt,
            mode_html = False,
            filters = None,
            user=user # body args
        )
        self.assertEqual(mail, None)

    def test_build_mail_mode_html(self):
        link = "http://www.company.com/activation?foo"
        mte = MailTemplateEntity.build(
            token = "ACTIVATION_LINK",
            arg_name = link,
            instance_attr_name = None,
            kind = MailTemplateEntity.LINK_KIND
        )
        body = "Hello active your account at {}ACTIVATION_LINK{}".format(self.escape, self.escape)
        mt = MailTemplate.build(
            name = "template-email1",
            body = body,
            sender = "Camilo Verdugo <asdf@gmail.com>",
            subject = "Subject emails"
        )
        mail, nf_keys, nf_args = Mail.build_populate(
            receptor_to = "User <userr@gmail.com>",
            mail_template = mt,
            mode_html = True,
            filters = None,
            activation_link = link
        )
        self.assertEqual(type(mail), Mail)
        self.assertEqual(nf_keys, [])
        self.assertEqual(nf_args, [])
        expected_result = "Hello active your account at <a href='{}' target='_blank'>{}</a>".format(link, link)
        self.assertEqual(mail.body, expected_result)

    def test_send(self):
        subject = "Greetings from Awesome Company!"
        email = Mail.build(
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

        # Cleanning temp directory
        shutil.rmtree(path)
