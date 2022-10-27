# -*- coding: utf-8 -*-

from turtle import st
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib import messages
from django.conf import settings
from datetime import datetime
from Main.decorators import permission_required
from Main.models import Employer, Event, Info, Notify, TempEmployer, UpdateEmployer, Widget, WidgetStatus, TypeStatus, \
    StatusEmployer
from Main.forms import FormReturn, FormResult, FormEmployer, FormNotice, FormProtocol, FormClose, \
    FormSearch, FormFilterCzn, FormInformation, FormNotify, FormEmployerNew
from Main.tools import create_event, e_date, get_profile
from Main.message import message_create
from Main.choices import RETURN_CHOICES, RESULT_CHOICES
from Main.employer.forms import FormSearchEmployer
from Main.employer.tools import get_count_find_employer, get_count_employer, get_count_page, get_list_employer, \
    get_list_existing_employer, emp_export_ods

######################################################################################################################


@permission_required(['czn', ])
def employer_create(request):
    """
    Создание карточки нарушителя вручную
    :param request:
    :return:
    """
    current_profile = get_profile(user=request.user)
    employer = Employer(Owner=current_profile, RegKatharsis=False, )
    employer.save()
    create_event(employer, employer.Owner, 'Создана карточка предприятия', None)
    return redirect(reverse('employer_edit', args=(employer.id,)))


######################################################################################################################


@permission_required(['control', 'assist', 'job', 'admin', 'czn', ])
def employer_find(request):
    """
    Отображение результата поиска карточек нарушителей
    :param request:
    :return:
    """
    if request.POST:
        form_search = FormSearchEmployer(request.POST)
        find = form_search['find'].value()
        czn = form_search['czn'].value()
        status = form_search['status'].value()
        count_employer = get_count_find_employer(find=find, czn=czn, list_status=status, )
        context = {
            'current_profile': get_profile(user=request.user),
            'title': 'Поиск',
            'per_page': settings.COUNT_LIST,
            'count_employer': count_employer,
            'count_page': get_count_page(count_employer=count_employer),
            'form_search': form_search,
            'find': find,
            'czn': czn,
            'status': status,
        }
        return render(request=request, template_name='employer/list.html', context=context, )
    if request.GET:
        number_page = int(request.GET.get('page', 1))
        start_count = (number_page - 1) * settings.COUNT_LIST
        stop_count = start_count + settings.COUNT_LIST
        list_employer = get_list_employer(
            find=request.GET.get('emp_find', None),
            czn=request.GET.get('emp_czn', None),
            list_status=request.GET.get('emp_status', None),
            start=start_count,
            stop=stop_count,
        )
        context = {
            'list_employer': list_employer,
        }
        return render(request=request, template_name='employer/slice.html', context=context, )
    return redirect(reverse('index'))


######################################################################################################################


@permission_required(['control', 'assist', 'job', 'admin', 'czn', ])
def employer_view(request, employer_id):
    """
    Просмотр карточки работодателя нарушителя
    :param request:
    :param employer_id:
    :return:
    """
    current_profile = get_profile(user=request.user)
    employer = get_object_or_404(Employer, id=employer_id)
    current_step = None
    for status in list(StatusEmployer.objects.filter(employer=employer)):
        if employer.owner_department == current_profile.department and status.type_status == TypeStatus.objects.first():
            return redirect(reverse('employer_edit', args=(employer.id,)))
        if current_profile.department.role == status.type_status.role_access:
            current_step = status.type_status.template_path
    context = {
        'current_profile': current_profile,
        'title': employer.Title,
        'employer': employer,
        'list_notify': list(Notify.objects.filter(EmpNotifyID=employer)),
        'list_event': list(Event.objects.filter(EmpEventID=employer)),
        'list_information': list(Info.objects.filter(EmpInfoID=employer)),
        'list_existing_employer': get_list_existing_employer(employer=employer),
        'form_close': FormClose(),
        'form_result': FormResult(),
        'form_notice': FormNotice(),
        'form_protocol': FormProtocol(),
        'form_return': FormReturn(),
        'step': current_step,
    }
    return render(request=request, template_name='employer/view.html', context=context, )


######################################################################################################################


@permission_required(['control', 'assist', 'job', 'admin', 'czn', ])
def employer_edit(request, employer_id):
    """

    :param request:
    :param employer_id:
    :return:
    """
    current_profile = get_profile(user=request.user)
    employer = get_object_or_404(Employer, id=employer_id)
    if request.POST:
        formset = FormEmployerNew(request.POST, instance=employer)
        if formset.is_valid():
            formset.save()
            if 'send' in request.POST:
                create_status = False
                list_current_status = list(StatusEmployer.objects.filter(employer=employer))
                list_violations = Info.objects.filter(EmpInfoID=employer)
                for violation in list_violations:
                    next_status = violation.type_violations.next_status
                    if not StatusEmployer.objects.filter(employer=employer, type_status=next_status).exists():
                        StatusEmployer.objects.create(employer=employer, type_status=next_status)
                        if not create_status:
                            for current_status in list_current_status:
                                current_status.delete()
                            create_status = True
                if create_status:
                    create_event(
                        employer=employer,
                        profile=current_profile,
                        comment='Сохранена карточка предприятия, направлена на проверку в департамент занятости '
                                'населения Министерства труда и социального развития Омской области',
                        attache=None,
                    )
            return redirect(reverse('employer_view', args=(employer.id,)))
        else:
            messages.error(
                request,
                'Ошибка сохранения карточки предприятия. Проверьте данные и сохраните снова.'
            )
            return redirect(reverse('employer_edit', args=(employer.id,)))
    else:
        first_status = TypeStatus.objects.first()
        if employer.owner_department == current_profile.department \
                and StatusEmployer.objects.filter(employer=employer, type_status=first_status).exists():
            if employer.Archive:
                return redirect(reverse('archive_edit', args=(employer.id,)))
            else:
                form_employer = FormEmployerNew(instance=employer)
                context = {
                    'current_profile': current_profile,
                    'title': 'Редактирование карточки работодателя нарушителя',
                    'form_employer': form_employer,
                    'form_information': FormInformation(),
                    'form_notify': FormNotify(),
                    'employer': employer,
                    'list_event': Event.objects.filter(EmpEventID=employer),
                    'list_information': Info.objects.filter(EmpInfoID=employer),
                    'list_notify': Notify.objects.filter(EmpNotifyID=employer),
                    'list_existing_employer': Employer.objects.filter(INN=int(employer.INN)).exclude(id=employer.id),
                }
                return render(request=request, template_name='employer/edit.html', context=context, )
        else:
            return redirect(reverse('employer_view', args=(employer.id,)))


######################################################################################################################


@permission_required(['control', 'assist', 'job', 'admin', 'czn', ])
def employer_print(request, employer_id):
    """

    :param request:
    :param employer_id:
    :return:
    """
    employer = get_object_or_404(Employer, id=employer_id)
    context = {
        'current_profile': get_profile(user=request.user),
        'employer': employer,
        'list_event': Event.objects.filter(EmpEventID=employer),
        'list_info': Info.objects.filter(EmpInfoID=employer),
        'list_notify': Notify.objects.filter(EmpNotifyID=employer),
    }
    return render(request=request, template_name='employer/print.html', context=context, )


######################################################################################################################


@permission_required(['control', 'czn', ])
def employer_delete(request, employer_id):
    """

    :param request:
    :param employer_id:
    :return:
    """
    current_profile = get_profile(user=request.user)
    employer = get_object_or_404(Employer, id=employer_id)
    if (employer.Status == 0 and employer.Owner == current_profile) or current_profile.is_allowed(['control']):
        employer.delete()
    return redirect(reverse('index'))


######################################################################################################################


@permission_required(['assist', 'job', ])
def employer_audit(request, employer_id):
    """
    Функция проверки карточек работодателей нарушителей, которыую центры занятости создали и направили на проверку.
    Проверкой занимаются отдела Депаратмента занятотси населения
    :param request:
    :param employer_id:
    :return:
    """
    if request.POST:
        current_profile = get_profile(user=request.user)
        employer = get_object_or_404(Employer, id=employer_id)
        list_current_status = list(StatusEmployer.objects.filter(employer=employer))
        if 'accept' in request.POST:
            next_status = None
            for status in list_current_status:
                if status.type_status.role_access == current_profile.department.role:
                    next_status = status.type_status.next_status
                    status.delete()
            if next_status and not StatusEmployer.objects.filter(employer=employer).exists():
                StatusEmployer.objects.create(employer=employer, type_status=next_status)
                accept_message = 'Карточка предприятия согласована, направлена для составления протокола об ' \
                                 'административном правонарушении'
            else:
                accept_message = 'Карточка предприятия согласована'
            create_event(employer=employer, profile=current_profile, comment=accept_message, attache=None)
            message_create(employer=employer, group=0, text=accept_message, sender=current_profile)
        elif 'return' in request.POST:
            for status in list_current_status:
                status.delete()
            StatusEmployer.objects.create(employer=employer, type_status=TypeStatus.objects.first())
            try:
                return_result = int(request.POST['return_result'])
            except ValueError:
                return_result = 1
            comment = request.POST['return_comment']
            return_message = f'Карточка предприятия возвращена по причине: {dict(RETURN_CHOICES).get(return_result)}'
            if comment != '':
                return_message = return_message + ' (' + comment + ')'
            create_event(employer, current_profile, return_message, None)
            message_create(employer, 0, return_message, current_profile)
    return redirect(reverse('employer_view', args=(employer_id,)))


######################################################################################################################


@permission_required(['control', 'assist', 'job', 'admin', 'czn', ])
def employer_close(request, employer_id):
    """

    :param request:
    :param employer_id:
    :return:
    """
    if request.POST:
        profile = get_profile(user=request.user)
        emp = get_object_or_404(Employer, id=employer_id)
        if profile.role == 3:
            emp.Status = 12
            emp.save()
            comment = request.POST['close_comment']
            close_message = f'Карточка предприятия закрыта по причине: {comment}'
            create_event(emp, profile, close_message, None)
            message_create(emp, 0, close_message, profile)
        return redirect(reverse('emp', args=(emp.id,)))
    return redirect(reverse('index'))


######################################################################################################################


@permission_required(['control', 'czn', ])
def employer_temp_list(request):
    """

    :param request:
    :return:
    """
    if request.GET:
        id_temp_employer = int(request.GET.get('id', 0))
        temp_employer = get_object_or_404(TempEmployer, id=id_temp_employer)
        list_existent_employer = list(Employer.objects.filter(INN=int(temp_employer.INN)))
        context = {
            'temp_employer': temp_employer,
            'list_existent_employer': list_existent_employer,
        }
        return render(request=request, template_name='temp_employer/modal.html', context=context, )
    else:
        if request.POST:
            search_form = FormSearch(request.POST)
            if search_form.is_valid():
                search_query = request.POST['find']
                list_temp_employer = list(
                    TempEmployer.objects.filter(INN__startswith=search_query).values_list('id', 'Title')
                )
                list_temp_employer.extend(
                    list(
                        TempEmployer.objects.filter(Title__icontains=search_query).values_list('id', 'Title')
                    )
                )
                list_employer = list_temp_employer[settings.START_LIST:settings.STOP_LIST]
                messages.info(
                    request,
                    f'Найдено работодателей из Катарсиса - {len(list_temp_employer)}. '
                    f'Отображается - {len(list_employer)}.'
                )
            else:
                return redirect(reverse('employer_temp_list'))
        else:
            search_form = FormSearch()
            list_employer = []

        context = {
            'current_profile': get_profile(user=request.user),
            'title': 'Работодатели из Катарсиса',
            'count_total_employer': TempEmployer.objects.all().count(),
            'upload_date': UpdateEmployer.objects.first().create_date,
            'search_form': search_form,
            'list_employer': list_employer,
        }
        return render(request=request, template_name='temp_employer/list.html', context=context, )


######################################################################################################################


@permission_required(['control', 'assist', 'job', 'admin', 'czn', ])
def export_to_spreadsheet(request):
    """
    Выгрузка данных в файл
    :param request:
    :return:
    """
    all_fields = Employer._meta.get_fields(include_parents=False, include_hidden=False)
    default_on_fields = ['Title', 'INN', 'OGRN', 'Status', 'Owner', 'CreateDate', ]
    default_view_fields = default_on_fields + ['Number', 'JurAddress', 'FactAddress', 'SendDate', 'Contact', 'Response']
    if request.POST:
        czn = request.POST.get('czn', False)
        field_list = request.POST.getlist('fields')
        fields = []
        for field in all_fields:
            if field.name in default_view_fields:
                if field.name in field_list:
                    fields.append([field.name, field.verbose_name, True])
                else:
                    fields.append([field.name, field.verbose_name, False])
        return emp_export_ods(czn, field_list)
    else:
        current_profile = get_profile(user=request.user)
        context = {
            'current_profile': current_profile,
            'title': 'Выгрузка данных в файл',
        }
        if current_profile.role == 1 and not request.user.is_superuser:
            context['filter_czn_form'] = FormFilterCzn({'czn': current_profile.user.id})
        else:
            context['filter_czn_form'] = FormFilterCzn()
        fields = []
        for field in all_fields:
            if field.name in default_view_fields:
                if field.name in default_on_fields:
                    fields.append([field.name, field.verbose_name, True])
                else:
                    fields.append([field.name, field.verbose_name, False])
        context['fields'] = fields
        return render(request=request, template_name='export.html', context=context, )


######################################################################################################################


@permission_required(['control', 'assist', 'job', 'admin', 'czn', ])
def event_add(request, employer_id):
    """

    :param request:
    :param employer_id:
    :return:
    """
    current_profile = get_profile(user=request.user)
    employer = get_object_or_404(Employer, id=employer_id)
    if request.POST:
        event_file = None
        comment = ''
        if 'comment' in request.POST:
            comment = request.POST['comment']
            print(f'{comment}')
        if 'status' in request.POST:
            ...
            # status = request.POST['status']
        if request.FILES:
            event_file = request.FILES['notice']

        list_current_status = list(StatusEmployer.objects.filter(employer=employer))
        next_status = None
        for status in list_current_status:
            if status.type_status.role_access == current_profile.department.role:
                next_status = status.type_status.next_status
                if next_status:
                    status.delete()
        if next_status and not StatusEmployer.objects.filter(employer=employer).exists():
            StatusEmployer.objects.create(employer=employer, type_status=next_status)
        create_event(employer=employer, profile=current_profile, comment=comment, attache=event_file)
        message_create(employer=employer, group=0, text=comment, sender=current_profile)
        return redirect(reverse('employer_view', args=(employer.id,)))
    else:
        return redirect(reverse('index'))

    # if request.POST:
    #     comment = request.POST['comment']
    #     status = request.POST['status']
    #     myfile = None
    #     if status == '4' or status == '5' or status == '6' or status == '7' or status == '9' or status == '10':
    #         if request.FILES:
    #             myfile = request.FILES['notice']
    #     if status == '5':
    #         employer_form = request.POST['employer']
    #         protocol_form = request.POST['protocol']
    #         if employer_form == '1':
    #             if protocol_form == '1':
    #                 comment = 'Работодатель (юридическое лицо) получил уведомление, явился на составление протокола. ' \
    #                           'Отделом правовой работы, государственной службы и кадров Главного управления ' \
    #                           'составляется протокол об административном правонарушении.'
    #             if protocol_form == '2':
    #                 comment = 'Работодатель (юридическое лицо) получил уведомление, не явился на составление ' \
    #                           'протокола. Отделом правовой работы, государственной службы и кадров Главного ' \
    #                           'управления (в отсутствие работодателя) составляется протокол об административном ' \
    #                           'правонарушении.'
    #             if protocol_form == '3':
    #                 comment = 'Работодатель (юридическое лицо) не получил уведомление, не явился на составление ' \
    #                           'протокола. Отделом правовой работы, государственной службы и кадров Главного ' \
    #                           'управления (в отсутствие работодателя) составляется протокол об административном ' \
    #                           'правонарушении.'
    #         if employer_form == '2':
    #             if protocol_form == '1':
    #                 comment = 'Работодатель (индивидуальный предприниматель) получил уведомление, явился на ' \
    #                           'составление протокола. Отделом правовой работы, государственной службы и кадров ' \
    #                           'Главного управления составляется протокол об административном правонарушении.'
    #             if protocol_form == '2':
    #                 comment = 'Работодатель (индивидуальный предприниматель) получил уведомление, не явился на ' \
    #                           'составление протокола. Карточка закрыта.'
    #             if protocol_form == '3':
    #                 comment = 'Работодатель (индивидуальный предприниматель) не получил уведомление, не явился на ' \
    #                           'составление протокола. Карточка закрыта.'
    #     if status == '10':
    #         eventlist = Event.objects.filter(EmpEventID=employer_id)
    #         for event in eventlist:
    #             if event.Comment == 'Работодатель (юридическое лицо) получил уведомление, явился на составление ' \
    #                                 'протокола. Отделом правовой работы, государственной службы и кадров Главного ' \
    #                                 'управления составляется протокол об административном правонарушении.':
    #                 status = 6
    #     if status == '9' and emp.Result != 2:
    #         resultat = int(request.POST['resultat'])
    #         emp.Result = resultat
    #         if resultat == 2:
    #             status = 11
    #         comment = comment + '. ' + dict(RESULT_CHOICES).get(resultat)
    #     emp.Status = status
    #     emp.save()
    #     create_event(emp, profile, comment, myfile)
    #     message_create(emp.id, 0, comment, profile)


######################################################################################################################


@permission_required(['control', 'assist', 'job', 'admin', 'czn', ])
def notify_add(request, employer_id):
    """

    :param request:
    :param employer_id:
    :return:
    """
    profile = get_profile(user=request.user)
    emp = get_object_or_404(Employer, id=employer_id)
    if request.POST:
        noti = Notify()
        noti.EmpNotifyID = emp
        noti.Owner = profile
        noti.Method = request.POST['oNotifyMethod']
        if request.POST['oNotifyDate']:
            noti.NotifyDate = request.POST['oNotifyDate']
        if request.FILES:
            myfile = request.FILES['oNotifyAttach']
            noti.Attache.save(myfile.name, myfile)
        noti.Comment = request.POST['oNotifyComment']
        noti.save()
        return redirect(reverse('emp', args=(emp.id,)))


######################################################################################################################


@permission_required(['control', 'assist', 'job', 'admin', 'czn', ])
def temp_arch_new(request):
    """

    :param request:
    :return:
    """
    profile = get_profile(user=request.user)
    employer = Employer(Status=0, Owner=profile, RegKatharsis=False, Archive=True)
    employer.save()
    create_event(employer, employer.Owner, 'Создана карточка предприятия', None)
    if profile.role == 3:
        return redirect(reverse('archive_edit', args=(employer.id,)))
    else:
        return redirect(reverse('employer_delete', args=(employer.id,)))


######################################################################################################################


@permission_required(['control', 'assist', 'job', 'admin', 'czn', ])
def employer_arch_edit(request, employer_id):
    """

    :param request:
    :param employer_id:
    :return:
    """
    employer = get_object_or_404(Employer, id=employer_id)
    current_profile = get_profile(user=request.user)
    if employer.Owner != current_profile or (employer.Status != 0 and employer.Status != 1):
        return redirect(reverse('emp', args=(employer.id,)))

    form = FormEmployer(
        initial={
            'oTitle': employer.Title,
            'oJurAddress': employer.JurAddress,
            'oFactAddress': employer.FactAddress,
            'oInn': employer.INN,
            'oOgrn': employer.OGRN,
            'oVacancyDate': e_date(employer.VacancyDate),
            'oVacancyComment': employer.VacancyComment,
            'oEventDate': e_date(employer.EventDate),
            'oEventComment': employer.EventComment,
            'oSendDate': e_date(employer.SendDate),
            'oContact': employer.Contact,
        }
    )
    result_form = FormResult()
    notice_form = FormNotice()
    event_list = Event.objects.filter(EmpEventID=employer.id)
    context = {
        'current_profile': current_profile,
        'title': '',
        'form': form,
        'emp': employer,
        'eventlist': event_list,
        'notice_form': notice_form,
        'result_form': result_form,
        'list_existing_employer': Employer.objects.filter(INN__exact=employer.INN).exclude(id=employer.id),
    }
    return render(request=request, template_name='arch.html', context=context, )


######################################################################################################################


@permission_required(['control', 'assist', 'job', 'admin', 'czn', ])
def employer_arch_save(request, employer_id):
    """

    :param request:
    :param employer_id:
    :return:
    """
    profile = get_profile(user=request.user)
    if request.POST:
        comment = request.POST['comment']
        status = request.POST['status']
        myfile = None

        emp = get_object_or_404(Employer, id=employer_id)
        emp.Title = request.POST['oTitle']
        emp.JurAddress = request.POST['oJurAddress']
        emp.FactAddress = request.POST['oFactAddress']
        emp.INN = request.POST['oInn']
        emp.OGRN = request.POST['oOgrn']
        emp.Contact = request.POST['oContact']
        emp.SendDate = datetime.now()
        emp.Status = status
        if request.FILES:
            myfile = request.FILES['notice']
        resultat = int(request.POST['resultat'])
        emp.Result = resultat
        comment = comment + '. Результат - ' + dict(RESULT_CHOICES).get(resultat)
        emp.Archive = True
        emp.save()
        create_event(emp, profile, comment, myfile)
        message_create(emp, 0, comment, profile)
        return redirect(reverse('emp', args=(emp.id,)))
    return redirect(reverse('index'))


######################################################################################################################


@permission_required(['control', 'czn', ])
def employer_temp_create(request, temp_employer_id):
    """

    :param request:
    :param temp_employer_id:
    :return:
    """
    current_profile = get_profile(user=request.user)
    temp_employer = get_object_or_404(TempEmployer, id=temp_employer_id)
    archive = True if current_profile.is_allowed(['control']) else False
    employer = Employer.objects.create(
        Status=0,
        Title=temp_employer.Title,
        Number=temp_employer.Number,
        JurAddress=temp_employer.JurAddress,
        FactAddress=temp_employer.FactAddress,
        INN=temp_employer.INN,
        OGRN=temp_employer.OGRN,
        EventDate=temp_employer.EventDate,
        Owner=current_profile,
        RegKatharsis=True,
        Contact=temp_employer.Contact,
        Archive=archive,
        status_new=TypeStatus.objects.first(),
        owner_department=current_profile.department
    )
    StatusEmployer.objects.create(employer=employer, type_status=TypeStatus.objects.first(), )
    create_event(employer, current_profile, 'Создана карточка предприятия', None)
    if current_profile.is_allowed(['czn']):
        return redirect(reverse('employer_edit', args=(employer.id,)))
    if current_profile.is_allowed(['control']):
        return redirect(reverse('archive_edit', args=(employer.id,)))
    return redirect(reverse('employer_delete', args=(employer.id,)))


######################################################################################################################


@permission_required(['control', 'assist', 'job', 'admin', 'czn', ])
def employer_widget_show(request, widget_id):
    """
    Отображение списка карточек нарушителей в зависимости от выбранного виджкта
    :param request:
    :param widget_id:
    :return:
    """
    current_profile = get_profile(user=request.user)
    widget = get_object_or_404(Widget, id=widget_id)
    if request.GET:
        number_page = int(request.GET.get('page', 1))
        start_count = (number_page - 1) * settings.COUNT_LIST
        stop_count = start_count + settings.COUNT_LIST
        context = {
            'list_employer': get_list_employer(
                find=None,
                czn=current_profile.department.id if current_profile.department.is_czn else None,
                list_status=list(
                    WidgetStatus.objects.filter(widget__id=widget_id, checked=True, ).values_list('status', flat=True)
                ),
                start=start_count,
                stop=stop_count,
            ),
        }
        return render(request=request, template_name='employer/slice.html', context=context, )
    else:
        count_employer = get_count_employer(widget_id=widget.id, profile=current_profile, )
        context = {
            'current_profile': current_profile,
            'title': widget.title,
            'per_page': settings.COUNT_LIST,
            'count_employer': count_employer,
            'count_page': get_count_page(count_employer=count_employer),
            'form_search': FormSearchEmployer(
                initial={
                    'czn': current_profile.department.id if current_profile.department.is_czn else None
                }
            ),
        }
        return render(request=request, template_name='employer/list.html', context=context, )


######################################################################################################################
