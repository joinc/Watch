# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib import messages
from django.conf import settings
from datetime import datetime
from Main.decorators import permission_required
from Main.models import UserProfile, Employer, Event, Info, Notify, TempEmployer, UpdateEmployer
from Main.forms import FormReturn, FormResult, FormEmployer, FormNotice, FormProtocol, FormClose, FormResponse, \
    FormSearch, FormFilterCzn, FormFilterStatus, FormInformation, FormNotify, FormEmployerNew
from Main.tools import get_count_employer, get_list_employer, get_count_page, emp_export_ods, create_event, e_date, \
    get_list_existing_employer
from Main.message import message_create
from Main.choices import RETURN_CHOICES, RESULT_CHOICES

######################################################################################################################


@permission_required(['control', 'assist', 'job', 'admin', 'czn', ])
def employer_list(request, list_status, title):
    """
    Отображение списка карточек нарушителей в зависимости от статуса
    :param request:
    :param list_status:
    :param title:
    :return:
    """
    current_profile = get_object_or_404(UserProfile, user=request.user)
    czn = current_profile.id if current_profile.is_allowed(['czn']) else '0'
    if request.GET:
        number_page = int(request.GET.get('page', 1))
        start_count = (number_page - 1) * settings.COUNT_LIST
        stop_count = start_count + settings.COUNT_LIST
        list_employer = get_list_employer(
            search='',
            czn=czn,
            list_status=list_status,
            start=start_count,
            stop=stop_count,
        )
        context = {
            'list_employer': list_employer,
        }
        return render(request=request, template_name='employer/slice.html', context=context, )
    else:
        count_employer = get_count_employer(
            search='',
            czn=czn,
            list_status=list_status,
        )
        context = {
            'current_profile': current_profile,
            'title': title,
            'per_page': settings.COUNT_LIST,
            'form_search': FormSearch(),
            'form_filter_czn': FormFilterCzn({'czn': czn}),
            'form_filter_status': FormFilterStatus({'status': list_status[0]}),
            'count_employer': count_employer,
            'count_page': get_count_page(count_employer=count_employer),
        }
        return render(request=request, template_name='employer/list.html', context=context, )

######################################################################################################################


@permission_required(['control', 'assist', 'job', 'admin', 'czn', ])
def employer_find(request):
    """
    Отображение результата поиска карточек нарушителей
    :param request:
    :return:
    """
    if request.GET:
        search = request.GET.get('emp_find', '')
        czn = request.GET.get('emp_czn', '0')
        status = request.GET.get('emp_status', '20')
        page_number = int(request.GET.get('page', 1))
        start = (page_number - 1) * settings.COUNT_LIST
        stop = start + settings.COUNT_LIST
        list_employer = get_list_employer(search=search, czn=czn, list_status=[status], start=start, stop=stop)
        context = {
            'list_employer': list_employer,
        }
        return render(request=request, template_name='employer/slice.html', context=context, )
    else:
        context = {
            'current_profile': get_object_or_404(UserProfile, user=request.user),
            'title': 'Поиск карточек',
            'per_page': settings.COUNT_LIST,
        }
        if request.POST:
            search_form = FormSearch(request.POST)
            if search_form.is_valid():
                search = request.POST.get('find', '')
                czn = request.POST.get('czn', '0')
                status = request.POST.get('status', '20')
                context['form_search'] = search_form
                count_employer = get_count_employer(search=search, czn=czn, list_status=[status])
                context['employer_count'] = count_employer
                context['page_count'] = get_count_page(count_employer=count_employer)
                context['emp_find'] = search
                context['emp_czn'] = czn
                context['emp_status'] = status
                context['form_filter_czn'] = FormFilterCzn(request.POST)
                context['form_filter_status'] = FormFilterStatus(request.POST)
            else:
                return redirect(reverse('all'))
        else:
            count_employer = Employer.objects.all().count()
            context['form_search'] = FormSearch()
            context['form_filter_czn'] = FormFilterCzn()
            context['form_filter_status'] = FormFilterStatus()
            context['employer_count'] = count_employer
            context['page_count'] = get_count_page(count_employer=count_employer)
            context['emp_find'] = ''
            context['emp_czn'] = '0'
            context['emp_status'] = '20'
        return render(request=request, template_name='employer/list.html', context=context, )


######################################################################################################################


@permission_required(['czn', ])
def employer_create(request):
    """
    Создание карточки нарушителя вручную
    :param request:
    :return:
    """
    current_profile = get_object_or_404(UserProfile, user=request.user)
    employer = Employer(Owner=current_profile, RegKatharsis=False, )
    employer.save()
    create_event(employer, employer.Owner, 'Создана карточка предприятия', None)
    return redirect(reverse('employer_edit', args=(employer.id,)))


######################################################################################################################


@permission_required(['control', 'assist', 'job', 'admin', 'czn', ])
def employer_view(request, employer_id):
    """
    Просмотр карточки нарушителя
    :param request:
    :param employer_id:
    :return:
    """
    current_profile = get_object_or_404(UserProfile, user=request.user)
    employer = get_object_or_404(Employer, id=employer_id)
    if employer.Owner == current_profile and (employer.Status == 0 or employer.Status == 1):
        return redirect(reverse('employer_edit', args=(employer.id,)))

    context = {
        'current_profile': current_profile,
        'title': 'Карточка учета работодателя',
        'employer': employer,
        'list_notify': Notify.objects.filter(EmpNotifyID=employer),
        'list_event': Event.objects.filter(EmpEventID=employer),
        'list_information': Info.objects.filter(EmpInfoID=employer),
        'list_existing_employer': get_list_existing_employer(employer=employer),
    }
    if current_profile.role == 4:
        context['form_response'] = FormResponse()
    else:
        context['form_close'] = FormClose()
        context['form_result'] = FormResult()
        context['form_notice'] = FormNotice()
        context['form_protocol'] = FormProtocol()
        if current_profile.role != 3:
            context['form_return'] = FormReturn()
    return render(request=request, template_name='employer/view.html', context=context, )


######################################################################################################################


@permission_required(['czn', ])
def employer_save(request, employer_id):
    """

    :param request:
    :param employer_id:
    :return:
    """
    current_profile = get_object_or_404(UserProfile, user=request.user)
    if request.POST:
        employer = get_object_or_404(Employer, id=employer_id)

        formset = FormEmployerNew(request.POST, instance=employer)
        if formset.is_valid():
            formset.save()
        else:
            messages.error(
                request,
                'Ошибка сохранения карточки предприятия. Проверьте данные и сохраните снова.'
            )

        # emp = get_object_or_404(Employer, id=employer_id)
        # emp.Title = request.POST.get('title', emp.Title)
        # emp.JurAddress = request.POST.get('legal_address', emp.JurAddress)
        # emp.FactAddress = request.POST.get('actual_address', emp.FactAddress)
        # emp.INN = request.POST.get('inn', emp.INN)
        # emp.OGRN = request.POST.get('ogrn', emp.OGRN)
        # emp.VacancyDate = request.POST.get('vacancy_date', emp.VacancyDate)
        # emp.VacancyComment = request.POST.get('vacancy_comment', emp.VacancyComment)
        # emp.EventDate = request.POST.get('event_date', emp.EventDate)
        # emp.EventComment = request.POST.get('event_comment', emp.EventComment)
        # emp.Contact = request.POST.get('contact', emp.Contact)
        if 'notify' in request.POST:
            return redirect(reverse('employer_edit', args=(employer_id,)))
        elif 'send' in request.POST:
            employer.SendDate = datetime.now()
            employer.Status = 2
        employer.save()
        create_event(employer, current_profile, 'Сохранена карточка предприятия, направлена на проверку в департамент '
                                                'занятости населения Министерства труда и социального развития', None)
        return redirect(reverse('employer_view', args=(employer_id,)))
    return redirect(reverse('index'))


######################################################################################################################


@permission_required(['control', 'assist', 'job', 'admin', 'czn', ])
def employer_edit(request, employer_id):
    """

    :param request:
    :param employer_id:
    :return:
    """
    current_profile = get_object_or_404(UserProfile, user=request.user)
    employer = get_object_or_404(Employer, id=employer_id)
    if request.POST:
        formset = FormEmployerNew(request.POST, instance=employer)
        if formset.is_valid():
            formset.save()
        else:
            messages.error(
                request,
                'Ошибка сохранения карточки предприятия. Проверьте данные и сохраните снова.'
            )

        ...
    else:
        ...
    if employer.Owner != current_profile or (employer.Status != 0 and employer.Status != 1):
        return redirect(reverse('employer_view', args=(employer.id,)))
    if employer.Archive:
        return redirect(reverse('archive_edit', args=(employer.id,)))
    form_employer = FormEmployerNew(instance=employer)
    context = {
        'current_profile': current_profile,
        'title': 'Редактирование карточки предприятия',
        'form_employer': form_employer,
        'form_information': FormInformation(),
        'form_notify': FormNotify(),
        'employer': employer,
        'list_event': Event.objects.filter(EmpEventID=employer),
        'list_information': Info.objects.filter(EmpInfoID=employer),
        'list_notify': Notify.objects.filter(EmpNotifyID=employer),
        'list_existing_employer': Employer.objects.filter(INN__exact=employer.INN).exclude(id=employer.id),
    }
    return render(request=request, template_name='employer/edit.html', context=context, )


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
        'current_profile': get_object_or_404(UserProfile, user=request.user),
        'employer': employer,
        'list_event': Event.objects.filter(EmpEventID=employer),
        'list_info': Info.objects.filter(EmpInfoID=employer),
        'list_notify': Notify.objects.filter(EmpNotifyID=employer),
    }
    return render(request=request, template_name='employer/print.html', context=context, )


######################################################################################################################


@permission_required(['control', 'assist', 'job', 'admin', 'czn', ])
def employer_delete(request, employer_id):
    """

    :param request:
    :param employer_id:
    :return:
    """
    current_profile = get_object_or_404(UserProfile, user=request.user)
    employer = get_object_or_404(Employer, id=employer_id)
    if (employer.Status == 0 and employer.Owner == current_profile) or current_profile.is_allowed(['control']):
        employer.delete()
    return redirect(reverse('index'))


######################################################################################################################


@permission_required(['control', 'assist', 'job', 'admin', 'czn', ])
def employer_audit(request, employer_id):
    """

    :param request:
    :param employer_id:
    :return:
    """
    if request.POST:
        profile = get_object_or_404(UserProfile, user=request.user)
        employer = get_object_or_404(Employer, id=employer_id)
        if 'accept' in request.POST:
            employer.Status = 3
            employer.save()
            accept_message = 'Карточка предприятия согласована, направлена для составления протокола об ' \
                             'административном правонарушении'
            create_event(employer, profile, accept_message, None)
            message_create(employer.id, 0, accept_message, profile)
        elif 'return' in request.POST:
            employer.Status = 1
            employer.save()
            try:
                oReturn = int(request.POST['return_result'])
            except ValueError:
                oReturn = 1
            comment = request.POST['return_comment']
            return_message = 'Карточка предприятия возвращена по причине: ' + dict(RETURN_CHOICES).get(oReturn)
            if comment != '':
                return_message = return_message + ' (' + comment + ')'
            create_event(employer, profile, return_message, None)
            message_create(employer_id, 0, return_message, profile)
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
        profile = get_object_or_404(UserProfile, user=request.user)
        emp = get_object_or_404(Employer, id=employer_id)
        if profile.role == 3:
            emp.Status = 12
            emp.save()
            comment = request.POST['close_comment']
            close_message = 'Карточка предприятия закрыта по причине: ' + comment
            create_event(emp, profile, close_message, None)
            message_create(emp.id, 0, close_message, profile)
        return redirect(reverse('emp', args=(emp.id,)))
    return redirect(reverse('index'))


######################################################################################################################


@permission_required(['control', 'assist', 'job', 'admin', 'czn', ])
def employer_all(request):
    """
    Вывод списка всех карточек
    :param request:
    :return:
    """
    return employer_list(request, [0], 'Все карточки')


######################################################################################################################


@permission_required(['control', 'assist', 'job', 'admin', 'czn', ])
def employer_draft(request):
    """
    Вывод списка карточек в статусе Черновик
    :param request:
    :return:
    """
    return employer_list(request, ['0', '1'], 'Черновики карточек')


######################################################################################################################


@permission_required(['control', 'assist', 'job', 'admin', 'czn', ])
def employer_check(request):
    """
    Вывод списка карточек в статусе Карточки на проверке
    :param request:
    :return:
    """
    return employer_list(request, ['2'], 'Карточки на проверке')


######################################################################################################################


@permission_required(['control', 'assist', 'job', 'admin', 'czn', ])
def employer_work(request):
    """
    Вывод списка карточек в статусе В работе
    :param request:
    :return:
    """
    return employer_list(request, ['3', '4', '5', '6', '7', '11'], 'Карточки в работе')


######################################################################################################################


@permission_required(['control', 'assist', 'job', 'admin', 'czn', ])
def employer_ready(request):
    """
    Вывод списка карточек в статусе Вынесено постановлений
    :param request:
    :return:
    """
    return employer_list(request, ['9'], 'Вынесено постановлений')


######################################################################################################################


@permission_required(['control', 'assist', 'job', 'admin', 'czn', ])
def employer_closed(request):
    """
    Вывод списка карточек в статусе Закрытые карточки
    :param request:
    :return:
    """
    return employer_list(request, ['12'], 'Закрытые карточки')


######################################################################################################################


@permission_required(['control', 'assist', 'job', 'admin', 'czn', ])
def employer_temp_list(request):
    """

    :param request:
    :return:
    """
    if request.GET:
        id_temp_employer = int(request.GET.get('id', 0))
        temp_employer = get_object_or_404(TempEmployer, id=id_temp_employer)
        list_existent_employer = Employer.objects.filter(INN=temp_employer.INN)
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
                    'Найдено работодателей из Катарсиса - {0}. Отображается - {1}.'.format(
                        len(list_temp_employer),
                        len(list_employer),
                    )
                )
            else:
                return redirect(reverse('employer_temp_list'))
        else:
            search_form = FormSearch()
            list_employer = []

        context = {
            'current_profile': get_object_or_404(UserProfile, user=request.user),
            'title': 'Работодатели из Катарсиса',
            'count_total_employer': TempEmployer.objects.all().count(),
            'upload_date': UpdateEmployer.objects.first().upload_date,
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
        czn = request.POST.get('czn', '0')
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
        current_profile = get_object_or_404(UserProfile, user=request.user)
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
    profile = get_object_or_404(UserProfile, user=request.user)
    emp = get_object_or_404(Employer, id=employer_id)
    if request.POST:
        comment = request.POST['comment']
        status = request.POST['status']
        myfile = None
        if status == '4' or status == '5' or status == '6' or status == '7' or status == '9' or status == '10':
            if request.FILES:
                myfile = request.FILES['notice']
        if status == '5':
            employer_form = request.POST['employer']
            protocol_form = request.POST['protocol']
            if employer_form == '1':
                if protocol_form == '1':
                    comment = 'Работодатель (юридическое лицо) получил уведомление, явился на составление протокола. ' \
                              'Отделом правовой работы, государственной службы и кадров Главного управления ' \
                              'составляется протокол об административном правонарушении.'
                if protocol_form == '2':
                    comment = 'Работодатель (юридическое лицо) получил уведомление, не явился на составление ' \
                              'протокола. Отделом правовой работы, государственной службы и кадров Главного ' \
                              'управления (в отсутствие работодателя) составляется протокол об административном ' \
                              'правонарушении.'
                if protocol_form == '3':
                    comment = 'Работодатель (юридическое лицо) не получил уведомление, не явился на составление ' \
                              'протокола. Отделом правовой работы, государственной службы и кадров Главного ' \
                              'управления (в отсутствие работодателя) составляется протокол об административном ' \
                              'правонарушении.'
            if employer_form == '2':
                if protocol_form == '1':
                    comment = 'Работодатель (индивидуальный предприниматель) получил уведомление, явился на ' \
                              'составление протокола. Отделом правовой работы, государственной службы и кадров ' \
                              'Главного управления составляется протокол об административном правонарушении.'
                if protocol_form == '2':
                    comment = 'Работодатель (индивидуальный предприниматель) получил уведомление, не явился на ' \
                              'составление протокола. Карточка закрыта.'
                if protocol_form == '3':
                    comment = 'Работодатель (индивидуальный предприниматель) не получил уведомление, не явился на ' \
                              'составление протокола. Карточка закрыта.'
        if status == '10':
            eventlist = Event.objects.filter(EmpEventID=employer_id)
            for event in eventlist:
                if event.Comment == 'Работодатель (юридическое лицо) получил уведомление, явился на составление ' \
                                    'протокола. Отделом правовой работы, государственной службы и кадров Главного ' \
                                    'управления составляется протокол об административном правонарушении.':
                    status = 6
        if status == '9' and emp.Result != 2:
            resultat = int(request.POST['resultat'])
            emp.Result = resultat
            if resultat == 2:
                status = 11
            comment = comment + '. ' + dict(RESULT_CHOICES).get(resultat)
        emp.Status = status
        emp.save()
        create_event(emp, profile, comment, myfile)
        message_create(emp.id, 0, comment, profile)
        return redirect(reverse('emp', args=(emp.id,)))
    return redirect(reverse('index'))


######################################################################################################################


@permission_required(['control', 'assist', 'job', 'admin', 'czn', ])
def notify_add(request, employer_id):
    """

    :param request:
    :param employer_id:
    :return:
    """
    profile = get_object_or_404(UserProfile, user=request.user)
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
    profile = get_object_or_404(UserProfile, user=request.user)
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
    current_profile = get_object_or_404(UserProfile, user=request.user)
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
    eventlist = Event.objects.filter(EmpEventID=employer.id)
    context = {
        'current_profile': current_profile,
        'title': '',
        'form': form,
        'emp': employer,
        'eventlist': eventlist,
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
    profile = get_object_or_404(UserProfile, user=request.user)
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
        message_create(emp.id, 0, comment, profile)
        return redirect(reverse('emp', args=(emp.id,)))
    return redirect(reverse('index'))


######################################################################################################################


@permission_required(['control', 'assist', 'job', 'admin', 'czn', ])
def employer_temp_create(request, temp_employer_id):
    """

    :param request:
    :param temp_employer_id:
    :return:
    """
    current_profile = get_object_or_404(UserProfile, user=request.user)
    temp_emp = get_object_or_404(TempEmployer, id=temp_employer_id)
    employer = Employer(
        Status=0,
        Title=temp_emp.Title,
        Number=temp_emp.Number,
        JurAddress=temp_emp.JurAddress,
        FactAddress=temp_emp.FactAddress,
        INN=temp_emp.INN,
        OGRN=temp_emp.OGRN,
        EventDate=temp_emp.EventDate,
        Owner=current_profile,
        RegKatharsis=True,
        Contact=temp_emp.Contact,
        Archive=False,
    )
    if current_profile.is_allowed(['control']):
        employer.Archive = True
    employer.save()
    create_event(employer, current_profile, 'Создана карточка предприятия', None)
    if current_profile.is_allowed(['czn']):
        return redirect(reverse('employer_edit', args=(employer.id,)))
    if current_profile.is_allowed(['control']):
        return redirect(reverse('archive_edit', args=(employer.id,)))
    return redirect(reverse('employer_delete', args=(employer.id,)))


######################################################################################################################
