# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect, reverse
from .forms import FormRole
from .models import UserProfile
from .tools import admin_only

######################################################################################################################


@login_required
@admin_only
def profile_list(request):
    """
    Список пользователей
    :param request:
    :return:
    """
    for user in User.objects.all():
        user_profile, created = UserProfile.objects.get_or_create(user=user, )
        if created:
            user_profile.save()
    context = {
        'profile': get_object_or_404(UserProfile, user=request.user),
        'title': 'Список пользователей',
        'role_form': FormRole(),
        'list_profile': UserProfile.objects.all(),
    }
    return render(request, 'profile_list.html', context)


######################################################################################################################


@login_required
@admin_only
def profile_block(request):
    """
    Заблокировать пользователя
    :param request:
    :return:
    """
    if request.POST:
        profile = get_object_or_404(UserProfile, id=request.POST['profile_id'])
        profile.block()
    return redirect(reverse('profile_list'))


######################################################################################################################


@login_required
@admin_only
def profile_unblock(request):
    """
    Разблокироваь пользователя
    :param request:
    :return:
    """
    if request.POST:
        profile = get_object_or_404(UserProfile, id=request.POST['profile_id'])
        profile.unblock()
    return redirect(reverse('profile_list'))


######################################################################################################################


@login_required
@admin_only
def profile_role(request):
    """
    Смена роли пользователю
    :param request:
    :return:
    """
    if request.POST:
        profile = get_object_or_404(UserProfile, id=request.POST['profile_id'], )
        profile.role = request.POST['role']
        profile.save()
    return redirect(reverse('profile_list'))


######################################################################################################################
