# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.models import User
from django.conf import settings
from datetime import datetime
from openpyxl import load_workbook
from Main.models import UserProfile, Configure, TempEmployer, UpdateEmployer, Widget, Status
from Main.decorators import admin_only
from Main.forms import FormRole
import os

######################################################################################################################


@admin_only
def configure_list(request) -> HttpResponse:
    """
    Отображение конфигураций для настроки и обслуживанию информационной системы
    :param request:
    :return:
    """
    context = {
        'current_profile': get_object_or_404(UserProfile, user=request.user),
        'title': 'Список конфигураций',
        'list_configure': Configure.objects.all(),
    }
    return render(request=request, template_name='configure/configure_list.html', context=context)


######################################################################################################################


@admin_only
def send_email(request):
    """
    Тестирование отправки сообщения на электронную почту
    :param request:
    :return:
    """
    if not request.user.is_superuser:
        return redirect(reverse('index'))

    email = ['yubelyakov@mtsr.omskportal.ru']
    data = """
    Привет.
    Это тестовое письмо.
    ---
    С Уважением Робот.
    """
    send_mail('Заголовок', data, settings.DEFAULT_FROM_EMAIL, email, fail_silently=False)
    messages.info(
        request,
        'Отправлено тестовое электронное письмо на адрес {0}.'.format(email)
    )

    return redirect(reverse('configure_list'))


######################################################################################################################


@admin_only
def employer_load(request):
    """
    Загрузка информации об организациях из подготовленного файла в Катарсисе
    :param request:
    :return:
    """

    if request.POST:

        def send_blank(value):
            if value:
                return value
            else:
                return ''

        start_time = datetime.now()
        TempEmployer.objects.all().delete()
        for count, x in enumerate(request.FILES.getlist('files')):
            file = settings.UPLOAD_FILE + str(count) + '.xlsx'

            def process(f):
                with open(file, 'wb+') as destination:
                    for chunk in f.chunks():
                        destination.write(chunk)

            process(x)
            workbook = load_workbook(filename=file)
            sheet = workbook.active
            if sheet.max_row > 2:
                list_temp_employer = []
                for row in range(3, sheet.max_row + 1):
                    temp_employer = TempEmployer(
                        Number=send_blank(sheet.cell(row=row, column=1).value),
                        Title=send_blank(sheet.cell(row=row, column=2).value),
                        INN=send_blank(sheet.cell(row=row, column=3).value),
                        OGRN=send_blank(sheet.cell(row=row, column=4).value),
                        JurAddress=send_blank(sheet.cell(row=row, column=5).value),
                        FactAddress=send_blank(sheet.cell(row=row, column=6).value),
                        Contact=send_blank(sheet.cell(row=row, column=7).value),
                    )
                    event_date = send_blank(sheet.cell(row=row, column=8).value)
                    if isinstance(event_date, datetime):
                        temp_employer.EventDate = event_date.strftime("%Y-%m-%d")
                    list_temp_employer.append(temp_employer)
                TempEmployer.objects.bulk_create(list_temp_employer)

                messages.info(
                    request,
                    'Файл {0} содержит записей организаций - {1}.'.format(x.name, sheet.max_row - 2)
                )
            else:
                messages.error(
                    request,
                    'Файл {0} не содержит данные.'.format(x.name)
                )
            workbook.close()
            os.remove(file)
        update_employer = UpdateEmployer(
            upload_date=datetime.now(),
            count_employer=TempEmployer.objects.all().count(),
            time_spent=(datetime.now() - start_time).seconds,
        )
        update_employer.save()
        messages.success(
            request,
            'Успешно загружено {0} записей организаций из Катарсис за {1} секунд.'.format(
                update_employer.count_employer,
                update_employer.time_spent,
            )
        )

    context = {
        'current_profile': get_object_or_404(UserProfile, user=request.user),
        'title': 'Загрузить работодателей',
        'list_breadcrumb': (('configure_list', 'Список конфигураций'),),
    }
    return render(request=request, template_name='configure/employer_load.html', context=context)


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
        'list_breadcrumb': (('configure_list', 'Список конфигураций'),),
        'role_form': FormRole(),
        'list_profile': UserProfile.objects.all(),
    }
    return render(request, 'configure/profile_list.html', context)


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


@admin_only
def filter_list(request):
    """
    Список фильтров статусов
    :param request:
    :return:
    """
    list_widget = Widget.objects.all()
    list_status = Status.objects.all()
    # list_filter_status = []
    # for filter in list_filter:
    #     for status in list_status:
    #         a1, created = FilterStatus.objects.get_or_create(filter=filter, status=status)
    #         print(a1)

    # if request.POST:
    #     profile = get_object_or_404(UserProfile, id=request.POST.get('id_profile'))
    #     formset = FormRole(request.POST, instance=profile)
    #     super_role = formset['super_role'].value()
    #     if formset.is_valid() and super_role:
    #         formset.save()
    #         messages.success(
    #             request,
    #             'Пользователю {0} установлена роль - {1}.'.format(profile, profile.get_super_role_display())
    #         )
    #     else:
    #         if super_role:
    #             messages.warning(
    #                 request,
    #                 'Роль пользователя {1} не изменена на "{1}"'.format(profile, super_role)
    #             )
    #         else:
    #             messages.warning(
    #                 request,
    #                 'Не указана новая роль пользователя {0}'.format(profile)
    #             )
    #
    # for user in User.objects.all():
    #     user_profile, created = UserProfile.objects.get_or_create(user=user, )
    #     if created:
    #         user_profile.save()
    context = {
        'current_profile': get_object_or_404(UserProfile, user=request.user),
        'title': 'Список фильтров',
        'list_breadcrumb': (('configure_list', 'Список конфигураций'),),
        # 'role_form': FormRole(),
        'list_widget': list_widget,
        'list_status': list_status,
    }
    return render(request, 'configure/filter_list.html', context)
