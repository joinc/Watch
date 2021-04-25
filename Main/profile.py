# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib import messages
from Main.forms import FormRole
from Main.models import UserProfile
from Main.tools import admin_only

######################################################################################################################


@login_required
@admin_only
def profile_list(request):
    """
    Список пользователей
    :param request:
    :return:
    """
    if request.POST:
        profile = get_object_or_404(UserProfile, id=request.POST.get('id_profile'))
        formset = FormRole(request.POST, instance=profile)
        new_role = formset['new_role'].value()
        if formset.is_valid() and new_role:
            formset.save()
            messages.success(
                request,
                'Пользователю {0} установлена роль - {1}.'.format(profile, profile.new_role)
            )
        else:
            if new_role:
                messages.warning(
                    request,
                    'Роль пользователя {1} не изменена на "{1}"'.format(profile, new_role)
                )
            else:
                messages.warning(
                    request,
                    'Не указана новая роль пользователя {0}'.format(profile)
                )

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
