from django.test import TestCase
from django.contrib.auth.models import User
from django.conf import settings
from django.core import mail
from django.core.files import File
from django.db.models import Q

from .models import MailTemplateEntity, Mail, MailTemplate, Attachment
from .html_parser import MyHTMLParser

import datetime
import shutil

def _create_fixtures():
    MailTemplateEntity.build(
        MailTemplateEntity,
        token = "NAME",
        arg_name = "user",
        instance_attr_name = "first_name",
        kind = MailTemplateEntity.DIRECT_KIND
    )

    MailTemplateEntity.build(
        MailTemplateEntity,
        token = "AGE",
        arg_name = "32",
        instance_attr_name = None,
        kind = MailTemplateEntity.DIRECT_KIND
    )

    User.objects.create(
        first_name = "User1322",
        last_name = "Recolector",
        email = "agent@empresa.cl",
        username = "agent@empresa.cl"
    )


class MailTemplateEntityTestCase(TestCase):

    def setUp(self):
        _create_fixtures()

    def test_replacement_text(self):
        mte1_email = MailTemplateEntity.build(
            MailTemplateEntity,
            token = "User.Email",
            arg_name = "user",
            instance_attr_name = "email",
            kind = MailTemplateEntity.DIRECT_KIND
        )
        self.assertEqual(mte1_email.token, mte1_email.token.upper())

        # Test MailTEmplateEntity creation
        mte1 = MailTemplateEntity._get_by_token(MailTemplateEntity, "NAME")
        self.assertEqual(mte1.arg_name, "user")

        # Testing MailTemplateEntity with extra_filters
        mte1 = MailTemplateEntity._get_by_token(
            MailTemplateEntity,
            "NAME",
            [Q(arg_name="user")]
            )
        self.assertEqual(mte1.token, "NAME")

    def test_get_remplacement(self):
        user = User.objects.get(first_name="User1322")

        # Testing replacement direct from Entity
        mte_direct = MailTemplateEntity.build(
            MailTemplateEntity,
            token = "BRAND",
            arg_name = "LeanTech",
            instance_attr_name = None,
            kind = MailTemplateEntity.DIRECT_KIND
        )
        self.assertEqual(mte_direct._get_replacement(), mte_direct.arg_name)

        # Testing replacement by args
        mte = MailTemplateEntity.build(
            MailTemplateEntity,
            token = "IS_STAFF",
            arg_name = "user",
            instance_attr_name = "is_staff",
            kind = MailTemplateEntity.DIRECT_KIND
        )
        self.assertEqual(mte._get_replacement(user=user), user.is_staff)

        # Testing replacement fail because not populate data found
        self.assertEqual(mte._get_replacement(), None)


    def test_values_by_kind(self):
        # Case IMAGE
        mte = MailTemplateEntity.build(
            MailTemplateEntity,
            token = "COMPANY_LOGO",
            arg_name = "image",
            instance_attr_name = None,
            kind = MailTemplateEntity.IMG_KIND
        )
        img_path = "http://cdn.website.com/image.png"
        result = mte._get_value_by_kind(img_path)
        self.assertEqual(result, "<img src='{}' alt='{}'>".format(img_path, img_path))

        # Case Date
        mte = MailTemplateEntity.build(
            MailTemplateEntity,
            token = "DEBT_DATE",
            arg_name = "debt_date",
            instance_attr_name = None,
            kind = MailTemplateEntity.DATE_KIND
        )
        date = datetime.date(year=2017,month=5,day=21)
        result = mte._get_value_by_kind(date)
        self.assertEqual(result, date.strftime(settings.MAILTOR_DATE_FORMAT))

        # Case Time
        mte = MailTemplateEntity.build(
            MailTemplateEntity,
            token = "DEBT_DATE",
            arg_name = "debt_date",
            instance_attr_name = None,
            kind = MailTemplateEntity.TIME_KIND
        )
        time = datetime.time(hour=23, minute=0, second=0)
        result = mte._get_value_by_kind(time)
        self.assertEqual(result, time.strftime(settings.MAILTOR_TIME_FORMAT))

        # Case Datetime
        mte = MailTemplateEntity.build(
            MailTemplateEntity,
            token = "DEBT_DATE",
            arg_name = "debt_date_time",
            instance_attr_name = None,
            kind = MailTemplateEntity.DATETIME_KIND
        )
        dt = datetime.datetime(year=2017, month=5, day=21, hour=23, minute=0, second=0)
        result = mte._get_value_by_kind(dt)
        self.assertEqual(result, dt.strftime(settings.MAILTOR_DATETIME_FORMAT))

        # Case link
        mte = MailTemplateEntity.build(
            MailTemplateEntity,
            token = "DEBT_DATE",
            arg_name = "debt_date",
            instance_attr_name = None,
            kind = MailTemplateEntity.LINK_KIND
        )
        link = "http://www.company.com/customer/payment"
        result = mte._get_value_by_kind(link)
        self.assertEqual(result, "<a href='{}' target='_blank'>{}</a>".format(link, link))

class MailTestCase(TestCase):

    escape = None

    def setUp(self):
        self.escape = MailTemplateEntity._get_escape()
        _create_fixtures()

    def test_populate_body(self):
        # Testing replacement entity
        user = User.objects.get(first_name="User1322")
        mte_name = MailTemplateEntity._get_by_token(MailTemplateEntity, "NAME")
        mte_age = MailTemplateEntity._get_by_token(MailTemplateEntity, "AGE")
        body= "Hello {}{}{}, This is an example of populate body email, your age is {}{}{}?".format(self.escape, mte_name.token, self.escape, self.escape, mte_age.token, self.escape)
        age = 32
        body_populated, nf_keys, nf_args = Mail._populate_body(
            _class=MailTemplateEntity,
            body=body,
            filters=[],
            user=user,
            age=age
        )
        body_expected = "Hello {}, This is an example of populate body email, your age is {}?".format(user.first_name, age)
        self.assertEqual(body_populated, body_expected)
        self.assertEqual(nf_keys, [])
        self.assertEqual(nf_args, [])

        # Testing not found and valid replacement args
        not_found = "NOT_FOUND"
        body = "Hello {}{}{}, This is an example of populate body email, your age is {}{}{}?".format(self.escape, mte_name.token, self.escape, self.escape, not_found, self.escape)
        populate_body, nf_keys, nf_args = Mail._populate_body(
            _class=MailTemplateEntity,
            body=body,
            filters=[],
            user=user
        )
        body_expected = "Hello {}, This is an example of populate body email, your age is {}{}{}?".format(user.first_name, self.escape, not_found, self.escape)
        self.assertEqual(body_expected, populate_body)
        self.assertEqual(nf_keys, [not_found])
        self.assertEqual(nf_args, [])

        # Testing not found args
        nf_keys =[]
        nf_args =[]
        body = "Hello {}{}{}, This is an example of populate body email".format(self.escape, mte_name.token, self.escape)
        body_populated, nf_keys, nf_args = Mail._populate_body(
             _class=MailTemplateEntity,
             body=body,
             filters=[],
             populate_values ={}
        )
        body_expected = "Hello {}{}{}, This is an example of populate body email".format(self.escape, mte_name.token, self.escape)
        self.assertEqual(body_expected, body_populated)
        self.assertEqual(nf_keys, [])
        self.assertEqual(nf_args, [mte_name.token])


    def test_build_base_case(self):
        # Testing replacement successfuly from user entity
        body = "Hello {}NAME{}, This is an example of populate body email".format(self.escape, self.escape)
        mt = MailTemplate.build(
            MailTemplate,
            name = "template-email1",
            body = body,
            sender = "Camilo Verdugo <asdf@gmail.com>",
            subject = "Subject emails"
        )
        user = User.objects.get(first_name="User1322")
        mail_fields = {
            'sender':mt.sender,
            'receptor_to':"User <userr@gmail.com>",
            'body': mt.body,
            'subject': mt.subject
        }
        body_args = {
            'user':user
        }
        mail, nf_keys, nf_args = Mail.build(
            Mail,
            MailTemplateEntity,
            None,
            mail_fields,
            body_args
        )
        self.assertEqual(type(mail), Mail)
        self.assertEqual(mail.body, "Hello {}, This is an example of populate body email".format(user.first_name))
        self.assertEqual(nf_keys, [])
        self.assertEqual(nf_args, [])

        # Testing successfull delivery plain mode
        mail.send()
        self.assertEqual(type(mail.sent_at), datetime.datetime)

        # Test no specify receptor_to
        mail_fields = {
            'sender':mt.sender,
            'body': mt.body,
            'subject': mt.subject
        }
        body_args = {
            'user':user
        }
        mail, nf_keys, nf_args = Mail.build(
            Mail,
            MailTemplateEntity,
            None,
            mail_fields,
            body_args
        )
        self.assertEqual(mail, None)

    def test_build_mail(self):
        # Testing direct replacement without
        link = "http://www.company.com/activation?foo"
        mte = MailTemplateEntity.build(
            MailTemplateEntity,
            token = "ACTIVATION_LINK",
            arg_name = link,
            instance_attr_name = None,
            kind = MailTemplateEntity.LINK_KIND
        )
        body = "Hello active your account at {}ACTIVATION_LINK{}".format(self.escape, self.escape)
        mt = MailTemplate.build(
            MailTemplate,
            name = "template-email1",
            body = body,
            sender = "Camilo Verdugo <asdf@gmail.com>",
            subject = "Subject emails"
        )

        mail_fields = {
            'sender':mt.sender,
            'receptor_to':"User <userr@gmail.com>",
            'body': mt.body,
            'subject': mt.subject
        }
        body_args = {}
        mail, nf_keys, nf_args = Mail.build(
            Mail,
            MailTemplateEntity,
            None,
            mail_fields,
            body_args
        )
        self.assertEqual(type(mail), Mail)
        self.assertEqual(nf_keys, [])
        self.assertEqual(nf_args, [])
        expected_result = "Hello active your account at <a href='{}' target='_blank'>{}</a>".format(link, link)
        self.assertEqual(mail.body, expected_result)

    def test_build_mail_error_keys(self):
        # No data to populate
        body = "Hello active your account at {}ACTIVATION_LINK{}".format(self.escape, self.escape)
        mt = MailTemplate.build(
            MailTemplate,
            name = "template-email1",
            body = body,
            sender = "Camilo Verdugo <asdf@gmail.com>",
            subject = "Subject emails"
        )
        mail_fields = {
            'sender':mt.sender,
            'receptor_to':"User <userr@gmail.com>",
            'body': mt.body,
            'subject': mt.subject
        }
        body_args = {}
        mail, nf_keys, nf_args = Mail.build(
            Mail,
            MailTemplateEntity,
            None,
            mail_fields,
            body_args
        )
        self.assertEqual(type(mail), Mail)
        self.assertEqual(nf_keys, ['ACTIVATION_LINK'])
        self.assertEqual(mail.error_code, mail.ERROR_KEYS)
        self.assertEqual(mail.error_detail, 'ACTIVATION_LINK')

    def test_build_mail_error_args(self):
        body = "Hello active your account at {}NAME{}".format(self.escape, self.escape)
        mt = MailTemplate.build(
            MailTemplate,
            name = "template-email1",
            body = body,
            sender = "Camilo Verdugo <asdf@gmail.com>",
            subject = "Subject emails"
        )

        mail_fields = {
            'sender':mt.sender,
            'receptor_to':"User <userr@gmail.com>",
            'body': mt.body,
            'subject': mt.subject
        }
        body_args = {}
        mail, nf_keys, nf_args = Mail.build(
            Mail,
            MailTemplateEntity,
            None,
            mail_fields,
            body_args
        )

        self.assertEqual(type(mail), Mail)
        self.assertEqual(nf_args, ['NAME'])
        self.assertEqual(mail.error_code, mail.ERROR_POPULATE)
        self.assertEqual(mail.error_detail, 'NAME')

    def test_build_mail_error_args_and_token(self):
        body = "Hello active your account at {}NAME{}, if you want to turn off this notification, click here {}SUBSCRIPTION_LINK{}".format(self.escape, self.escape, self.escape, self.escape)
        mt = MailTemplate.build(
            MailTemplate,
            name = "template-email1",
            body = body,
            sender = "Camilo Verdugo <asdf@gmail.com>",
            subject = "Subject emails"
        )

        mail_fields = {
            'sender':mt.sender,
            'receptor_to':"User <userr@gmail.com>",
            'body': mt.body,
            'subject': mt.subject
        }
        body_args = {}
        mail, nf_keys, nf_args = Mail.build(
            Mail,
            MailTemplateEntity,
            None,
            mail_fields,
            body_args
        )

        self.assertEqual(type(mail), Mail)
        self.assertEqual(nf_args, ['NAME'])
        self.assertEqual(mail.error_code, mail.ERROR_POPULATE_KEYS)
        self.assertEqual(nf_keys, ['SUBSCRIPTION_LINK'])
        self.assertEqual(mail.error_detail, 'NAME,SUBSCRIPTION_LINK')


    def test_send_with_attachment(self):
        subject = "Greetings from Awesome Company!"
        mail_fields = {
            'sender': "Company No Reply <no-reply@company.com>",
            'receptor_to': "Customer <customer@customer.com>",
            'body': "Hello Dear Customer!",
            'subject': subject
        }
        email, __,__ = Mail.build(
            Mail,
            MailTemplateEntity,
            None,
            mail_fields
        )

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

    def test_send_mail_html(self):
        subject = "Greetings from Awesome Company!"
        mail_fields = {
            'sender': "Company No Reply <no-reply@company.com>",
            'receptor_to': "Customer <customer@customer.com>",
            'body': "Hello Dear Customer!, <h1>Welcome!!!</h1>",
            'subject': subject
        }
        email, __,__ = Mail.build(
            Mail,
            MailTemplateEntity,
            None,
            mail_fields
        )

        result = email.send()

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].body, "Hello Dear Customer!, Welcome!!!")
        self.assertEqual(mail.outbox[0].alternatives, [('Hello Dear Customer!, <h1>Welcome!!!</h1>{}'.format(email.get_pixel()), 'text/html')])
        self.assertEqual(mail.outbox[0].content_subtype, 'html')
        self.assertEqual(mail.outbox[0].subject, subject)
        self.assertEqual(result, True)


class MyHTMLParserTestCase(TestCase):

    def setUp(self):
        pass

    def test_plain_parser(self):
        html = "Welcome User, I hope you enjoy this class"
        parser = MyHTMLParser()
        parser.feed(html)
        self.assertEqual(parser.star_tag,[])
        self.assertEqual(parser.end_tag,[])
        self.assertEqual(parser.comments,[])
        self.assertEqual(parser.data,[html])
        self.assertEqual(parser.get_plain_text(),html)
        self.assertEqual(parser.is_html(),False)

    def test_html_parser(self):
        html = "Welcome User, <h1>Title</h1> <a href='www.google.com'>google.com</a><!--comment-->"
        parser = MyHTMLParser()
        parser.feed(html)
        self.assertEqual(parser.star_tag,[('href','www.google.com')])
        self.assertEqual(parser.end_tag,['h1','a'])
        self.assertEqual(parser.comments,['comment'])
        self.assertEqual(parser.data,["Welcome User, ","Title"," ","google.com"])
        self.assertEqual(parser.get_plain_text(),"Welcome User, Title google.com")
        self.assertEqual(parser.is_html(),True)

