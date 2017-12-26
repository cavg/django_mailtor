from django.shortcuts import render, redirect
from django.forms import modelform_factory

from .models import MailTemplateEntity, MailTemplate, MailTemplateEntityForm

def create_template(request):
    mtes = MailTemplateEntity.objects.filter()
    escape = MailTemplateEntity._get_escape()

    if request.method == 'POST':
        name = request.POST.get('name', '')
        body = request.POST.get('body', '')
        sender = request.POST.get('sender', '')
        subject = request.POST.get('subject', '')
        mt = MailTemplate.build(
            MailTemplate,
            name = name,
            body = body,
            sender = sender,
            subject = subject
        )
        return redirect('mailtor')
    return render(request, "create_template.html", locals())


def create_entity(request):
    mailEntity = modelform_factory(
        MailTemplateEntity, fields = (
            'token',
            'arg_name',
            'instance_attr_name',
            'kind'
        )
    )
    if request.method == 'POST':
        formset = mailEntity(request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('mailtor')
    else:
        formset = mailEntity()

    return render(request, 'create_entity.html', locals())

def index(request):
    return render(request, "index.html")