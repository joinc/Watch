# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib import messages
from django.contrib.auth.models import User
from Main.models import UserProfile, Department
from Main.profile.forms import FormProfile, FormPassword, FormDepartment
from Main.profile.tools import check_password
from Main.decorators import superuser_only, permission_required
from Main.tools import get_profile

######################################################################################################################


@permission_required(['control', 'assist', 'job', 'admin', 'czn'])
def profile_list(request):
    """
    Список пользователей
    :param request:
    :return:
    """
    current_profile = get_profile(user=request.user)
    context = {
        'current_profile': current_profile,
        'title': 'Список пользователей',
        'profile_edit': current_profile.user.is_superuser,
        'list_profile': UserProfile.objects.all(),
    }
    return render(request=request, template_name='profile/list.html', context=context, )


######################################################################################################################


@superuser_only
def profile_create(request):
    """
    Добавлоение пользователя
    :param request:
    :return:
    """
    if request.POST:
        form_profile = FormProfile(request.POST)
        username = form_profile['username'].value()
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        initial = {
            'email': form_profile['email'].value(),
            'username': username,
            'first_name': form_profile['first_name'].value(),
        }
        message_list = check_password(username=username, password=password, password2=password2)
        if form_profile.is_valid() and not message_list:
            user = form_profile.save()
            user.set_password(password)
            user.save()
            profile, created = UserProfile.objects.get_or_create(user=user, )
            profile.department = get_object_or_404(Department, id=request.POST.get('department'))
            profile.save()
            messages.success(request, 'Пользователь {0} успешно создан.'.format(profile))
            return redirect(reverse('profile_show', args=(profile.id, )))
        else:
            if User.objects.filter(username=username).exists():
                del initial['username']
                message_list.append('Пользователь ' + username + ' уже существует.')
        for message in message_list:
            messages.error(request, message)
        form_profile = FormProfile(
            initial=initial,
        )
        form_department = FormDepartment(
            initial={
                'department': request.POST.get('department'),
            },
        )
    else:
        form_profile = FormProfile()
        form_department = FormDepartment()
    context = {
        'current_profile': get_profile(user=request.user),
        'title': 'Добавление нового пользователя',
        'list_breadcrumb': ((reverse('profile_list'), 'Список пользователей'),),
        'form_profile': form_profile,
        'form_department': form_department,
        'form_password': FormPassword(),
    }
    return render(request=request, template_name='profile/create.html', context=context, )


######################################################################################################################


@permission_required(['control', 'assist', 'job', 'admin', 'czn'])
def profile_show(request, profile_id):
    """
    Страница профиля пользователя
    :param request:
    :param profile_id:
    :return:
    """
    current_profile = get_profile(user=request.user)
    profile = get_profile(profile=profile_id)
    if request.POST and (current_profile == profile or current_profile.user.is_superuser):
        form_password = FormPassword(request.POST)
        password = form_password['password'].value()
        password2 = form_password['password2'].value()
        message_list = check_password(username=profile.user.username, password=password, password2=password2)
        if message_list:
            for message in message_list:
                messages.error(request, message)
        else:
            messages.success(request, 'Пароль пользователя {0} успешно изменен.'.format(profile))
            profile.user.set_password(password)
            profile.user.save()
            return redirect(reverse('profile_show', args=(profile.id, )))
    context = {
        'current_profile': current_profile,
        'title': 'Пользователь ' + profile.__str__(),
        'list_breadcrumb': ((reverse('profile_list'), 'Список пользователей'),),
        'form_password': FormPassword(),
        'profile_edit': current_profile.user.is_superuser,
        'profile': profile,
    }
    return render(request=request, template_name='profile/show.html', context=context, )


######################################################################################################################


@superuser_only
def profile_edit(request, profile_id):
    """
    Страница профиля пользователя
    :param request:
    :param profile_id:
    :return:
    """
    profile = get_profile(profile=profile_id)
    if request.POST:
        form_profile = FormProfile(request.POST)
        FormDepartment(request.POST, instance=profile).save()
        profile.user.first_name = form_profile['first_name'].value()
        profile.user.email = form_profile['email'].value()
        profile.user.save()
        messages.success(request, 'Пользователь {0} успешно отредактирован и сохранен'.format(profile), )
        return redirect(reverse('profile_show', args=(profile.id, )))
    else:
        form_profile = FormProfile(instance=profile.user, )
        form_department = FormDepartment(instance=profile, )
    context = {
        'current_profile': get_profile(user=request.user),
        'title': 'Редактирование пользователя {0}'.format(profile),
        'list_breadcrumb': ((reverse('profile_list'), 'Список пользователей'),),
        'form_profile': form_profile,
        'form_department': form_department,
    }
    return render(request=request, template_name='profile/edit.html', context=context, )


######################################################################################################################


@superuser_only
def profile_blocked(request, profile_id):
    """
    Функция по блокировке или разблокировки профиля пользователя в зависимости от состояния
    :param request:
    :param profile_id:
    :return:
    """
    profile = get_profile(profile=profile_id)
    if profile.blocked:
        profile.unblock()
        messages.info(request, 'Пользователь {0} разблокирован'.format(profile), )
    else:
        profile.block()
        messages.error(request, 'Пользователь {0} заблокирован'.format(profile), )
    return redirect(reverse('profile_show', args=(profile_id, )))


######################################################################################################################
