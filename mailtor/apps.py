from django.apps import AppConfig


class MailtorConfig(AppConfig):
    name = 'mailtor'

    def ready(self):
        import mailtor.signals