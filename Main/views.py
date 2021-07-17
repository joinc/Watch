# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import auth
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.conf import settings
from Main.models import UserProfile, Config
from Main.tools import get_count_employer
from Main.decorators import admin_only

######################################################################################################################


@login_required
def index(request) -> HttpResponse:
    """
    Отображение главной страницы
    :param request:
    :return: HttpResponse
    """
    current_profile = get_object_or_404(UserProfile, user=request.user)
    czn = current_profile.id if current_profile.is_allowed(['czn']) else '0'
    context = {
        'current_profile': current_profile,
        'title': 'Главная',
        'count_all': get_count_employer(search='', czn='0', list_status=['20']),
        'count_my': get_count_employer(search='', czn=current_profile.id, list_status=['20']),
        'count_edit': get_count_employer(search='', czn=current_profile.id, list_status=['1']),
        'count_draft': get_count_employer(search='', czn=czn, list_status=['0', '1']),
        'count_check': get_count_employer(search='', czn=czn, list_status=['2']),
        'count_work': get_count_employer(search='', czn=czn, list_status=['3', '4', '5', '6', '7', '11']),
        'count_ready': get_count_employer(search='', czn=czn, list_status=['9']),
        'count_closed': get_count_employer(search='', czn=czn, list_status=['12']),
    }
    return render(request=request, template_name='index.html', context=context)


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
            messages.error(request, 'Не правильно введенные данные')
            return redirect(reverse('login'))
    else:
        context = {
            'title': 'Авторизация',
            'next': request.GET.get('next') if request.GET.get('next') else settings.SUCCESS_URL,
        }
        return render(request=request, template_name='login.html', context=context)


######################################################################################################################


@login_required
def logout(request) -> HttpResponse:
    """
    Выход пользователя
    :param request:
    :return:
    """
    auth.logout(request)
    return redirect(reverse('login'))


######################################################################################################################


@admin_only
def config_show(request) -> HttpResponse:
    """
    Отображение конфигураций для настроки и обслуживанию информационной системы
    :param request:
    :return:
    """
    context = {
        'current_profile': get_object_or_404(UserProfile, user=request.user),
        'title': 'Настройки',
        'list_config': Config.objects.all(),
    }
    return render(request=request, template_name='config/config_show.html', context=context)


######################################################################################################################
