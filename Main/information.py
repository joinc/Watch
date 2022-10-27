# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404, redirect, reverse
from Main.decorators import permission_required
from Main.models import Employer, Info
from Main.forms import FormInformation
from Main.tools import get_profile

######################################################################################################################


@permission_required(['czn'])
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


@permission_required(['czn'])
def information_delete(request, information_id):
    """
    Удаление записи о непредставленной информации
    :param request:
    :param information_id:
    :return:
    """
    current_profile = get_profile(user=request.user)
    information = get_object_or_404(Info, id=information_id)
    employer_id = information.EmpInfoID_id
    if information.EmpInfoID.owner_department == current_profile.department:
        information.Attache.delete()
        information.delete()
    return redirect(reverse('employer_edit', args=(employer_id,)))


######################################################################################################################
