from django.test import TestCase
from django.contrib.auth.models import User

from .models import MailTemplateEntities, Mail

def _create_fixtures():
    MailTemplateEntities.objects.create(
        token = "NAME",
        arg_name = "user",
        instance_attr_name = "first_name",
        kind = MailTemplateEntities.TEXT_KIND
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
        kind = MailTemplateEntities.TEXT_KIND
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
        self.assertEqual(mte1.get_replacement(user=user),first_name)

        # Testing replacement by regular param
        mte2 = MailTemplateEntities.objects.get(token="AGE")
        param = {'age':32}
        self.assertEqual(mte2.get_replacement(**param),param['age'])

        # Testing attr not found
        self.assertEqual(mte2.get_replacement(foo='faa'), None)

class MailTestCase(TestCase):

    def setUp(self):
        _create_fixtures()

    def test_populate_body(self):
        # Testing replacement entity and not found args
        body = "Hello ###NAME###, This is an example of populate body email, your age is ###AGE###?"
        user = User.objects.get(first_name="User1322")
        populate_body, _, nt_args = Mail.populate_body(body=body, user=user)
        body_expected = "Hello {}, This is an example of populate body email, your age is ###AGE###?".format(user.first_name)
        self.assertEqual(body_expected, populate_body)
        self.assertEqual(nt_args, ['AGE'])

        # Combine entity with dict
        age = 32
        body = "Hello ###NAME###, This is an example of populate body email, your age is ###AGE###? are you sure ###AGE### is?"
        body_expected = "Hello {}, This is an example of populate body email, your age is {}? are you sure {} is?".format(user.first_name, age, age)
        populate_body, _, _ = Mail.populate_body(body=body, user=user, age = age)
        self.assertEqual(body_expected, populate_body)

        # Testing not found key
        body = "Hello ###LAST_NAME###"
        body_expected = "Hello ###LAST_NAME###"
        populate_body, nf_keys, _ = Mail.populate_body(body=body)
        self.assertEqual(nf_keys, ['LAST_NAME'])


