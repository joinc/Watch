# -*- coding: utf-8 -*-

from django.shortcuts import redirect, reverse, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import auth
from Main.models import UserProfile

######################################################################################################################


def permission_required(list_permission):
    """
    Декорато позволяет выполнять функции, если пользователь находится в определенных группах доступа, которым разешено
    выполнение данной функции
    :param list_permission:
    :return:
    """
    def check_permission(function):
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated:
                profile = get_object_or_404(UserProfile, user=request.user)
                if profile.blocked:
                    auth.logout(request)
                    messages.info(request, 'Выша учетная запись заблокирована, обратитесь к администратору.')
                    return redirect(reverse('login'))
                if profile.is_allowed(list_permission=list_permission):
                    return function(request, *args, **kwargs)
                return redirect(reverse('index'))
            return redirect(reverse('login'))
        return wrapper
    return check_permission


######################################################################################################################


def admin_only(function):
    """
    Декоратор, проверят, что-бы пользователь обладал правами суперпользователя
    :param function:
    :return:
    """
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return function(request, *args, **kwargs)
            else:
                return redirect(reverse('index'))
        return redirect(reverse('login'))
    return wrapper


######################################################################################################################
