# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from Main.models import UserProfile, Employer, Message
from django.conf import settings

######################################################################################################################


def message_create(empid, group, text, sender):

    emp = get_object_or_404(Employer, id=empid)
    if group == 0:
        oMessage = Message()
        oMessage.EmpMessageID = emp
        oMessage.Recipient = emp.Owner
        oMessage.Reading = False
        oMessage.Text = text
        oMessage.Sender = sender
        oMessage.save()

"""
    if group == 2:
        recipients = UserProfile.objects.filter(role=2)
    elif group == 3:
        recipients = UserProfile.objects.filter(role=3)
    else:
        recipients = []
        recipients.append(emp.Owner)

    for res in recipients:
        oMessage = Message()
        oMessage.EmpMessageID = empid
        oMessage.Recipient = res
        oMessage.Reading = False
        oMessage.Text = text
        oMessage.save()
"""

######################################################################################################################


def message_list(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    breadcrumb = 'Уведомления'
    profile = get_object_or_404(UserProfile, user=request.user)
    mlist = Message.objects.filter(Recipient=profile)[settings.START_LIST:settings.STOP_LIST]
    mall = Message.objects.filter(Recipient=profile).count()
    mnew = Message.objects.filter(Recipient=profile).exclude(Reading=True).count()
    return render(request, 'messages.html', {'mlist': mlist, 'profile': profile, 'mall': mall, 'mnew': mnew, 'breadcrumb': breadcrumb, })

######################################################################################################################


def message_read(request, Message_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    oMessage = get_object_or_404(Message, id=Message_id)
    oMessage.Reading = True
    oMessage.save()
    return HttpResponseRedirect(reverse('messagelist'))

