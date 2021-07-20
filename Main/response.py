# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.conf import settings
from Main.decorators import permission_required
from Main.forms import FormResponse
from Main.models import UserProfile, Employer


######################################################################################################################


@permission_required(['admin', ])
def response_list(request):
    """
    Список ответственных за работу с карточками
    :param request:
    :return:
    """
    context = {
        'current_profile': get_object_or_404(UserProfile, user=request.user),
        'title': 'Назначение ответственных лиц',
        'list_emp': Employer.objects.filter(Response__isnull=True)[:settings.STOP_LIST],
        'response_form': FormResponse(),
    }
    return render(request=request, template_name='response/list.html', context=context, )


######################################################################################################################


@permission_required(['admin', ])
def response_set(request):
    """
    Назначение ответственного за работу с карточкой
    :param request:
    :return:
    """
    if request.POST and UserProfile.objects.filter(user=request.user, role=4, ).exists():
        response_id = request.POST['response']
        employer_id = request.POST['employer']
        employer = get_object_or_404(Employer, id=employer_id)
        response = get_object_or_404(UserProfile, id=response_id)
        employer.Response = response
        employer.save()
    return redirect(reverse('response_list'))


######################################################################################################################
