# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, reverse, redirect
from Main.models import UserProfile, Employer, Message
from django.conf import settings

######################################################################################################################


def message_create(employer_id, group, text, sender):
    """
    Создание сообщения
    :param employer_id:
    :param group:
    :param text:
    :param sender:
    :return:
    """
    employer = get_object_or_404(Employer, id=employer_id)
    if group == 0:
        message = Message(EmpMessageID=employer, Recipient=employer.Owner, Reading=False, Text=text, Sender=sender, )
        message.save()


######################################################################################################################


@login_required
def message_list(request):
    """
    Список сообщений
    :param request:
    :return:
    """
    profile = get_object_or_404(UserProfile, user=request.user)
    context = {
        'current_profile': profile,
        'title': 'Уведомления',
        'message_list': Message.objects.filter(Recipient=profile)[settings.START_LIST:settings.STOP_LIST],
        'message_all': Message.objects.filter(Recipient=profile).count(),
        'message_new': Message.objects.filter(Recipient=profile).exclude(Reading=True).count(),
    }
    return render(request, 'message_list.html', context)


######################################################################################################################

@login_required
def message_read(request, message_id):
    """
    Отметка о прочтении сообщения
    :param request:
    :param message_id:
    :return:
    """
    if Message.objects.filter(Recipient__user=request.user, id=message_id).exists():
        message = get_object_or_404(Message, id=message_id)
        message.Reading = True
        message.save()
    return redirect(reverse('message_list'))


######################################################################################################################
