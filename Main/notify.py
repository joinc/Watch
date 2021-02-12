# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import login_required
from Main.models import UserProfile, Employer, Notify
from Main.forms import FormNotify

######################################################################################################################


@login_required
def notify_create(request, employer_id):
    """

    :param request:
    :param employer_id:
    :return:
    """
    if request.POST:
        notify = Notify(
            EmpNotifyID=get_object_or_404(Employer, id=employer_id),
            Owner=get_object_or_404(UserProfile, user=request.user),
        )
        formset_notify = FormNotify(request.POST, request.FILES, instance=notify)
        if formset_notify.is_valid():
            formset_notify.save()
    return redirect(reverse('employer_edit', args=(employer_id,)))


######################################################################################################################


@login_required
def notify_delete(request, notify_id):
    """
    Удаление notify
    :param request:
    :param notify_id:
    :return:
    """
    profile = get_object_or_404(UserProfile, user=request.user)
    notify = get_object_or_404(Notify, id=notify_id)
    employer_id = notify.EmpNotifyID_id
    if notify.EmpNotifyID.Owner == profile:
        notify.Attache.delete()
        notify.delete()
    return redirect(reverse('employer_edit', args=(employer_id,)))


######################################################################################################################
