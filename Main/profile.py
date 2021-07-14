# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib import messages
from Main.forms import FormRole
from Main.models import UserProfile
from Main.decorators import admin_only

######################################################################################################################


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
        super_role = formset['super_role'].value()
        if formset.is_valid() and super_role:
            formset.save()
            messages.success(
                request,
                'Пользователю {0} установлена роль - {1}.'.format(profile, profile.get_super_role_display())
            )
        else:
            if super_role:
                messages.warning(
                    request,
                    'Роль пользователя {1} не изменена на "{1}"'.format(profile, super_role)
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
        'current_profile': get_object_or_404(UserProfile, user=request.user),
        'title': 'Список пользователей',
        'role_form': FormRole(),
        'list_profile': UserProfile.objects.all(),
    }
    return render(request, 'profile/list.html', context)


######################################################################################################################


@admin_only
def profile_change_blocked(request, profile_id):
    """
    Функция по блокировке или разблокировки профиля пользователя в зависимости от состояния
    :param request:
    :param profile_id:
    :return:
    """
    profile = get_object_or_404(UserProfile, id=profile_id)
    print(profile.get_menu())
    if profile.blocked:
        profile.unblock()
        messages.info(
            request,
            'Пользователь {0} разблокирован'.format(profile)
        )
    else:
        profile.block()
        messages.warning(
            request,
            'Пользователь {0} заблокирован'.format(profile)
        )
    return redirect(reverse('profile_list'))


######################################################################################################################
