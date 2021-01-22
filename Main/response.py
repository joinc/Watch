# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect, reverse
from .forms import FormResponse
from .models import UserProfile, Employer
from django.conf import settings


######################################################################################################################


@login_required
def response_list(request):
    """
    Список ответственных за работу с карточками
    :param request:
    :return:
    """
    profile = get_object_or_404(UserProfile, user=request.user)
    if profile.role == 4:
        context = {
            'profile': profile,
            'title': 'Назначение ответственных лиц',
            'list_emp': Employer.objects.filter(Response__isnull=True)[:settings.STOP_LIST],
            'response_form': FormResponse(),
        }
        return render(request, 'response_list.html', context)
    else:
        redirect(reverse('index'))


######################################################################################################################


@login_required
def response_set(request):
    """
    Назначение ответственного за работу с карточкой
    :param request:
    :return:
    """
    print(1)
    if request.POST and UserProfile.objects.filter(user=request.user, role=4, ).exists():
        print(2)
        response_id = request.POST['response']
        employer_id = request.POST['employer']
        employer = get_object_or_404(Employer, id=employer_id)
        response = get_object_or_404(UserProfile, id=response_id)
        employer.Response = response
        employer.save()
    print(3)
    return redirect(request.META.get('HTTP_REFERER', '/'))


######################################################################################################################
