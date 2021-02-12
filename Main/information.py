# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import login_required
from Main.models import UserProfile, Employer, Info
from Main.forms import FormInformation

######################################################################################################################


@login_required
def information_create(request, employer_id):
    if request.POST:
        information = Info(
            EmpInfoID=get_object_or_404(Employer, id=employer_id),
        )
        formset_information = FormInformation(request.POST, request.FILES, instance=information)
        if formset_information.is_valid():
            formset_information.save()
    return redirect(reverse('employer_edit', args=(employer_id,)))


######################################################################################################################


@login_required
def information_delete(request, information_id):
    """
    Удаление записи о непредставленной информации
    :param request:
    :param information_id:
    :return:
    """
    profile = get_object_or_404(UserProfile, user=request.user)
    information = get_object_or_404(Info, id=information_id)
    employer_id = information.EmpInfoID_id
    if information.EmpInfoID.Owner == profile:
        information.Attache.delete()
        information.delete()
    return redirect(reverse('employer_edit', args=(employer_id,)))


######################################################################################################################
