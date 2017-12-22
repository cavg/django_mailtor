from django.contrib import admin

from .models import MailTemplateEntity, MailTemplate, Mail, Attachment

class MailTemplateEntityAdmin(admin.ModelAdmin):
    list_display = ('token', 'arg_name', 'instance_attr_name', 'kind', 'created_at', 'updated_at')
admin.site.register(MailTemplateEntity, MailTemplateEntityAdmin)


class MailTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'sender', 'subject', 'created_at', 'updated_at')
admin.site.register(MailTemplate, MailTemplateAdmin)


class MailAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receptor_to', 'subject', 'deliver_at', 'sent_at', 'error_code' ,'created_at', 'updated_at')
admin.site.register(Mail, MailAdmin)


class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('attachment', 'mail', 'created_at', 'updated_at')
admin.site.register(Attachment, AttachmentAdmin)