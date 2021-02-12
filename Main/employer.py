# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from datetime import datetime, date
from Main import tools, message
from Main.models import UserProfile, Employer, Event, Info, Notify, TempEmployer, ConfigWatch
from Main.forms import FormReturn, FormResult, FormEmployer, FormNotice, FormProtocol, FormClose, FormResponse, \
    FormSearch, FormFilterCzn, FormFilterStatus, FormInformation, FormNotify
from Main.tools import get_employer_count, get_list_employer, get_page_count, admin_only, emp_export_ods, \
    event_create, e_date, p_emp_list
from Main.message import message_create
from Main.choices import RETURN_CHOICES, RESULT_CHOICES
import xlrd
import os

######################################################################################################################


def employer_list(request, list_status, title):
    """
    Отображение списка карточек нарушителей в зависимости от статуса
    :param request:
    :param list_status:
    :param title:
    :return:
    """
    profile = get_object_or_404(UserProfile, user=request.user)
    if request.GET:
        page_number = int(request.GET.get('page', 1))
        start_count = (page_number - 1) * settings.COUNT_LIST
        stop_count = start_count + settings.COUNT_LIST
        czn = '0'
        if profile.role == 1 and not request.user.is_superuser:
            czn = profile
        list_employer = get_list_employer(
            search='',
            czn=czn,
            list_status=list_status,
            start=start_count,
            stop=stop_count,
        )
        return render(request, 'employer_slice.html', {'employer_list': list_employer, })
    else:
        if profile.role == 1 and not request.user.is_superuser:
            czn = profile
            form_filter_czn = FormFilterCzn({'czn': profile.user.id})
        else:
            czn = '0'
            form_filter_czn = FormFilterCzn()
        employer_count = get_employer_count(search='', czn=czn, list_status=list_status)
        context = {
            'profile': profile,
            'title': title,
            'per_page': settings.COUNT_LIST,
            'form_search': FormSearch(),
            'form_filter_czn': form_filter_czn,
            'form_filter_status': FormFilterStatus({'status': list_status[0]}),
            'employer_count': employer_count,
            'page_count': get_page_count(emp_count=employer_count),
        }
        return render(request, 'employer_list.html', context)


######################################################################################################################


@login_required
def employer_find(request):
    """
    Отображение результата поиска карточек нарушителей
    :param request:
    :return:
    """
    context = {
        'profile': get_object_or_404(UserProfile, user=request.user),
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
            employer_count = get_employer_count(search=search, czn=czn, list_status=[status])
            context['employer_count'] = employer_count
            context['page_count'] = get_page_count(emp_count=employer_count)
            context['emp_find'] = search
            context['emp_czn'] = czn
            context['emp_status'] = status
            context['form_filter_czn'] = FormFilterCzn(request.POST)
            context['form_filter_status'] = FormFilterStatus(request.POST)
        else:
            return redirect(reverse('all'))
    elif request.GET:
        search = request.GET.get('emp_find', '')
        czn = request.GET.get('emp_czn', '0')
        status = request.GET.get('emp_status', '20')
        page_number = int(request.GET.get('page', 1))
        start = (page_number - 1) * settings.COUNT_LIST
        stop = start + settings.COUNT_LIST
        list_employer = get_list_employer(search=search, czn=czn, list_status=[status], start=start, stop=stop)
        return render(request, 'employer_slice.html', {'employer_list': list_employer, })
    else:
        context['form_search'] = FormSearch()
        context['form_filter_czn'] = FormFilterCzn()
        context['form_filter_status'] = FormFilterStatus()
        employer_count = Employer.objects.all().count()
        context['employer_count'] = employer_count
        context['page_count'] = get_page_count(emp_count=employer_count)
        context['emp_find'] = ''
        context['emp_czn'] = '0'
        context['emp_status'] = '20'
    return render(request, 'employer_list.html', context)


######################################################################################################################


@login_required
@admin_only
def emp_load(request):
    """

    :param request:
    :return:
    """
    context = {
        'profile': get_object_or_404(UserProfile, user=request.user),
        'title': 'Загрузить работодателей',
    }
    return render(request, 'load.html', context)


######################################################################################################################


@login_required
@admin_only
def emp_upload(request):
    """

    :param request:
    :return:
    """
    TempEmployer.objects.all().delete()
    for count, x in enumerate(request.FILES.getlist('files')):
        file = settings.UPLOAD_FILE + str(count)

        def process(f):
            with open(file, 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)

        process(x)

        rb = xlrd.open_workbook(file, formatting_info=False)
        sheet = rb.sheet_by_index(0)
        for rownum in range(sheet.nrows):
            if rownum > 1:
                row = sheet.row_values(rownum)
                temp_emp = TempEmployer()
                temp_emp.Number = row[0]
                temp_emp.Title = row[1]
                temp_emp.INN = row[2]
                temp_emp.OGRN = row[3]
                temp_emp.JurAddress = row[4]
                temp_emp.FactAddress = row[5]
                temp_emp.Contact = row[6]
                if row[7] != '':
                    td = xlrd.xldate_as_tuple(row[7], 0)
                    dd = date(td[0], td[1], td[2])
                    row[7] = dd.strftime("%Y-%m-%d")
                    temp_emp.EventDate = dd
                temp_emp.save()
        os.remove(file)
    update = ConfigWatch()
    update.UploadDate = datetime.now()
    update.save()
    return redirect(reverse('emps'))


######################################################################################################################


@login_required
def employer_create(request):
    """
    Создание карточки нарушителя вручную
    :param request:
    :return:
    """
    profile = get_object_or_404(UserProfile, user=request.user)
    employer = Employer(Owner=profile, RegKatharsis=False, )
    employer.save()
    tools.event_create(employer, employer.Owner, 'Создана карточка предприятия', None)
    return redirect(reverse('employer_edit', args=(employer.id,)))


######################################################################################################################


@login_required
def employer_view(request, employer_id):
    """
    Просмотр карточки нарушителя
    :param request:
    :param employer_id:
    :return:
    """
    profile = get_object_or_404(UserProfile, user=request.user)
    employer = get_object_or_404(Employer, id=employer_id)
    if employer.Owner == profile and (employer.Status == 0 or employer.Status == 1):
        return redirect(reverse('employer_edit', args=(employer.id,)))

    context = {
        'profile': profile,
        'title': 'Карточка учета работодателя',
        'employer': employer,
        'list_notify': Notify.objects.filter(EmpNotifyID=employer),
        'list_event': Event.objects.filter(EmpEventID=employer),
        'list_information': Info.objects.filter(EmpInfoID=employer),
        'pemp': tools.p_emp_list(employer.INN),
    }
    if profile.role == 4:
        context['form_response'] = FormResponse()
    else:
        context['form_close'] = FormClose()
        context['form_result'] = FormResult()
        context['form_notice'] = FormNotice()
        context['form_protocol'] = FormProtocol()
        if profile.role != 3:
            context['form_return'] = FormReturn()
    return render(request, 'employer_view.html', context)


######################################################################################################################


@login_required
def employer_save(request, employer_id):
    """

    :param request:
    :param employer_id:
    :return:
    """
    profile = get_object_or_404(UserProfile, user=request.user)
    if request.POST:
        emp = get_object_or_404(Employer, id=employer_id)
        emp.Title = request.POST.get('title', emp.Title)
        emp.JurAddress = request.POST.get('legal_address', emp.JurAddress)
        emp.FactAddress = request.POST.get('actual_address', emp.FactAddress)
        emp.INN = request.POST.get('inn', emp.INN)
        emp.OGRN = request.POST.get('ogrn', emp.OGRN)
        emp.VacancyDate = request.POST.get('vacancy_date', emp.VacancyDate)
        emp.VacancyComment = request.POST.get('vacancy_comment', emp.VacancyComment)
        emp.EventDate = request.POST.get('event_date', emp.EventDate)
        emp.EventComment = request.POST.get('event_comment', emp.EventComment)
        emp.Contact = request.POST.get('contact', emp.Contact)
        if 'notify' in request.POST:
            return redirect(reverse('employer_edit', args=(emp.id,)))
        elif 'send' in request.POST:
            emp.SendDate = datetime.now()
            emp.Status = 2
        emp.save()
        tools.event_create(emp, profile, 'Сохранена карточка предприятия, направлена на проверку в департамент '
                                         'занятости населения Министерства труда и социального развития', None)
        return redirect(reverse('employer_view', args=(emp.id,)))
    return redirect(reverse('index'))


######################################################################################################################


@login_required
def employer_edit(request, employer_id):
    """

    :param request:
    :param employer_id:
    :return:
    """
    employer = get_object_or_404(Employer, id=employer_id)
    profile = get_object_or_404(UserProfile, user=request.user)
    if employer.Owner != profile or (employer.Status != 0 and employer.Status != 1):
        return redirect(reverse('employer_view', args=(employer.id,)))
    if employer.Archive:
        return redirect(reverse('archive_edit', args=(employer.id,)))
    form = FormEmployer(
        initial={
            'title': employer.Title,
            'legal_address': employer.JurAddress,
            'actual_address': employer.FactAddress,
            'inn': employer.INN,
            'ogrn': employer.OGRN,
            'vacancy_date': tools.e_date(employer.VacancyDate),
            'vacancy_comment': employer.VacancyComment,
            'event_date': tools.e_date(employer.EventDate),
            'event_comment': employer.EventComment,
            'send_date': tools.e_date(employer.SendDate),
            'contact': employer.Contact,
        }
    )
#    notice_form = FormNotice()
    context = {
        'profile': profile,
        'title': 'Редактирование карточки предприятия',
        'form': form,
        'form_information': FormInformation(),
        'form_notify': FormNotify(),
        'employer': employer,
        'list_event': Event.objects.filter(EmpEventID=employer),
        'list_information': Info.objects.filter(EmpInfoID=employer),
        'list_notify': Notify.objects.filter(EmpNotifyID=employer),
        'pemp': tools.p_emp_list(employer.INN),
    }
    return render(request, 'employer_edit.html', context)


######################################################################################################################


@login_required
def employer_print(request, employer_id):
    """

    :param request:
    :param employer_id:
    :return:
    """
    employer = get_object_or_404(Employer, id=employer_id)
    context = {
        'profile': get_object_or_404(UserProfile, user=request.user),
        'emp': employer,
        'eventlist': Event.objects.filter(EmpEventID=employer),
        'infolist': Info.objects.filter(EmpInfoID=employer),
        'notifylist': Notify.objects.filter(EmpNotifyID=employer),
    }
    return render(request, 'employer_print.html', context)


######################################################################################################################


@login_required
def employer_delete(request, employer_id):
    """

    :param request:
    :param employer_id:
    :return:
    """
    profile = get_object_or_404(UserProfile, user=request.user)
    employer = get_object_or_404(Employer, id=employer_id)
    if (employer.Status == 0 and employer.Owner == profile) or profile.role == 3:
        employer.delete()
    return redirect(reverse('index'))


######################################################################################################################


@login_required
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
            tools.event_create(employer, profile, accept_message, None)
            message.message_create(employer.id, 0, accept_message, profile)
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
            tools.event_create(employer, profile, return_message, None)
            message.message_create(employer_id, 0, return_message, profile)
    return redirect(reverse('employer_view', args=(employer_id,)))


######################################################################################################################


@login_required
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
            tools.event_create(emp, profile, close_message, None)
            message.message_create(emp.id, 0, close_message, profile)
        return redirect(reverse('emp', args=(emp.id,)))
    return redirect(reverse('index'))


######################################################################################################################


@login_required
def employer_all(request):
    """
    Вывод списка всех карточек
    :param request:
    :return:
    """
    return employer_list(request, ['20'], 'Все карточки')


######################################################################################################################


@login_required
def employer_draft(request):
    """
    Вывод списка карточек в статусе Черновик
    :param request:
    :return:
    """
    return employer_list(request, ['0', '1'], 'Черновики карточек')


######################################################################################################################


@login_required
def employer_check(request):
    """
    Вывод списка карточек в статусе Карточки на проверке
    :param request:
    :return:
    """
    return employer_list(request, ['2'], 'Карточки на проверке')


######################################################################################################################


@login_required
def employer_work(request):
    """
    Вывод списка карточек в статусе В работе
    :param request:
    :return:
    """
    return employer_list(request, ['3', '4', '5', '6', '7', '11'], 'Карточки в работе')


######################################################################################################################


@login_required
def employer_ready(request):
    """
    Вывод списка карточек в статусе Вынесено постановлений
    :param request:
    :return:
    """
    return employer_list(request, ['9'], 'Вынесено постановлений')


######################################################################################################################


@login_required
def employer_closed(request):
    """
    Вывод списка карточек в статусе Закрытые карточки
    :param request:
    :return:
    """
    return employer_list(request, ['12'], 'Закрытые карточки')


######################################################################################################################


@login_required
def employer_temp_list(request):
    """

    :param request:
    :return:
    """
    oFind = ''
    if request.POST:
        search_form = FormSearch(request.POST)
        if search_form.is_valid():
            search = request.POST['find']
            temp_emp = TempEmployer.objects.filter(INN__startswith=search)
            if temp_emp.count() == 0:
                temp_emp = TempEmployer.objects.filter(Title__icontains=search)
            scnt = temp_emp.count()
            aEmp = temp_emp[settings.START_LIST:settings.STOP_LIST]
        else:
            return redirect(reverse('emps'))
    else:
        search_form = FormSearch()
        scnt = TempEmployer.objects.all().count()
        aEmp = TempEmployer.objects.all()[settings.START_LIST:settings.STOP_LIST]
    pemp = []
    for emp in aEmp:
        for emp_f in Employer.objects.filter(INN=emp.INN):
            pemp.append(emp_f)
    context = {
        'profile': get_object_or_404(UserProfile, user=request.user),
        'title': 'Работодатели из Катарсиса',
        'aEmp': aEmp,
        'search_form': search_form,
        'find': oFind,
        'scnt': scnt,
        'vcnt': aEmp.count(),
        'pemp': pemp,
        'update': ConfigWatch.objects.all().first(),
    }
    return render(request, 'emps.html', context)


######################################################################################################################


@login_required
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
        profile = get_object_or_404(UserProfile, user=request.user)
        context = {
            'profile': profile,
            'title': 'Выгрузка данных в файл',
        }
        if profile.role == 1 and not request.user.is_superuser:
            context['filter_czn_form'] = FormFilterCzn({'czn': profile.user.id})
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
        return render(request, 'export.html', context)


######################################################################################################################


@login_required
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
        event_create(emp, profile, comment, myfile)
        message_create(emp.id, 0, comment, profile)
        return redirect(reverse('emp', args=(emp.id,)))
    return redirect(reverse('index'))


######################################################################################################################


@login_required
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


@login_required
def temp_arch_new(request):
    """

    :param request:
    :return:
    """
    profile = get_object_or_404(UserProfile, user=request.user)
    emp = Employer(Status=0, Owner=profile, RegKatharsis=False, Archive=True)
    emp.save()
    event_create(emp, emp.Owner, 'Создана карточка предприятия', None)
    if profile.role == 3:
        return redirect(reverse('archedit', args=(emp.id,)))
    else:
        return redirect(reverse('delete', args=(emp.id,)))


######################################################################################################################


@login_required
def employer_arch_edit(request, employer_id):
    """

    :param request:
    :param employer_id:
    :return:
    """
    emp = get_object_or_404(Employer, id=employer_id)
    profile = get_object_or_404(UserProfile, user=request.user)
    if emp.Owner != profile or (emp.Status != 0 and emp.Status != 1):
        return redirect(reverse('emp', args=(emp.id,)))

    form = FormEmployer(
        initial={
            'oTitle': emp.Title,
            'oJurAddress': emp.JurAddress,
            'oFactAddress': emp.FactAddress,
            'oInn': emp.INN,
            'oOgrn': emp.OGRN,
            'oVacancyDate': e_date(emp.VacancyDate),
            'oVacancyComment': emp.VacancyComment,
            'oEventDate': e_date(emp.EventDate),
            'oEventComment': emp.EventComment,
            'oSendDate': e_date(emp.SendDate),
            'oContact': emp.Contact,
        }
    )
    result_form = FormResult()
    notice_form = FormNotice()
    eventlist = Event.objects.filter(EmpEventID=emp)
    context = {
        'profile': profile,
        'title': '',
        'form': form,
        'emp': emp,
        'eventlist': eventlist,
        'notice_form': notice_form,
        'result_form': result_form,
        'pemp': p_emp_list(emp.INN),
    }
    return render(request, 'arch.html', context)


######################################################################################################################


@login_required
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
        event_create(emp, profile, comment, myfile)
        message_create(emp.id, 0, comment, profile)
        return redirect(reverse('emp', args=(emp.id,)))

    return redirect(reverse('index'))


######################################################################################################################


@login_required
def create_temp_emp(request, temp_employer_id):
    """

    :param request:
    :param temp_employer_id:
    :return:
    """
    profile = get_object_or_404(UserProfile, user=request.user)
    temp_emp = get_object_or_404(TempEmployer, id=temp_employer_id)
    emp = Employer()
    emp.Status = 0
    emp.Title = temp_emp.Title
    emp.Number = temp_emp.Number
    emp.JurAddress = temp_emp.JurAddress
    emp.FactAddress = temp_emp.FactAddress
    emp.INN = temp_emp.INN
    emp.OGRN = temp_emp.OGRN
    emp.EventDate = temp_emp.EventDate
    emp.Owner = profile
    emp.RegKatharsis = True
    emp.Contact = temp_emp.Contact
    emp.Archive = False
    if profile.role == 3:
        emp.Archive = True
    emp.save()
    event_create(emp, emp.Owner, 'Создана карточка предприятия', None)
    if profile.role == 1:
        return redirect(reverse('edit', args=(emp.id,)))
    elif profile.role == 3:
        return redirect(reverse('archedit', args=(emp.id,)))
    else:
        return redirect(reverse('delete', args=(emp.id,)))


######################################################################################################################
