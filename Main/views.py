# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import auth
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.conf import settings
from Main.models import UserProfile
from Main.tools import get_emp_count

######################################################################################################################


@login_required
def index(request) -> HttpResponse:
    """
    Отображение главной страницы
    :param request:
    :return: HttpResponse
    """
    profile = get_object_or_404(UserProfile, user=request.user)
    czn = profile.id if profile.role == 1 else '0'
    context = {
        'profile': profile,
        'title': 'Главная',
        'count_all': get_emp_count(search='', czn='0', list_status=['20']),
        'count_my': get_emp_count(search='', czn=profile.id, list_status=['20']),
        'count_edit': get_emp_count(search='', czn=profile.id, list_status=['1']),
        'count_draft': get_emp_count(search='', czn=czn, list_status=['0', '1']),
        'count_check': get_emp_count(search='', czn=czn, list_status=['2']),
        'count_work': get_emp_count(search='', czn=czn, list_status=['3', '4', '5', '6', '7', '11']),
        'count_ready': get_emp_count(search='', czn=czn, list_status=['9']),
        'count_closed': get_emp_count(search='', czn=czn, list_status=['12']),
    }
    return render(request, 'index.html', context)


######################################################################################################################


def login(request) -> HttpResponse:
    """
    Вход пользователя
    :param request:
    :return: HttpResponse
    """
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user:
            auth.login(request, user)
            return redirect(request.POST['next'])
        else:
            messages.info(request, 'Не правильно введенные данные')
            return redirect(reverse('login'))
    else:
        context = {'title': 'Авторизация',
                   'next': request.GET.get('next') if request.GET.get('next') else settings.SUCCESS_URL}
        return render(request, 'login.html', context)


######################################################################################################################


def logout(request) -> HttpResponse:
    """
    Выход пользователя
    :param request:
    :return:
    """
    auth.logout(request)
    return redirect(reverse('index'))


######################################################################################################################
