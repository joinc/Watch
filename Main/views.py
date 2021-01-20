# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import auth, User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404, redirect, reverse
from .forms import FormRole, FormResult, FormSearch, FormEmp, FormNotice, FormFilterCzn, FormFilterStatus, \
    FormResponse, FormMonth, FormReportDates
from .choices import RESULT_CHOICES, STATUS_CHOICES
from .models import UserProfile, TempEmployer, Employer, Event, Notify, Info, ConfigWatch
from .tools import event_create, e_date, get_page_count, p_emp_list, report_filter, get_emp_count, get_emp_list
from .message import message_create
from django.conf import settings
from pyexcel_ods3 import save_data
from collections import OrderedDict
import xlrd
import calendar
import mimetypes
import os


######################################################################################################################


def admin_only(function):
    def _inner(request, *args, **kwargs):
        if not request.user.is_superuser:
            return redirect(reverse('index'))
        else:
            return function(request, *args, **kwargs)

    return _inner


######################################################################################################################


@login_required
def index(request) -> HttpResponse:
    """
    Отображение главной страницы
    :param request:
    :return: HttpResponse
    """
    list_czn = UserProfile.objects.filter(role=1).order_by('user')
    CZN_CHOICES = [[0, 'Все ЦЗН']]
    for i in list_czn:
        CZN_CHOICES.append([i.id, i.user.get_full_name()])
    print(CZN_CHOICES, )

    profile = get_object_or_404(UserProfile, user=request.user)
    czn = profile.id if profile.role == 1 else '0'
    context = {
        'profile': profile,
        'title': 'Главная',
        'count_all': get_emp_count(search='', czn='0', list_status=['20']),
        'count_my': get_emp_count(search='', czn=profile.id, list_status=['20']),
        'count_edit': get_emp_count(search='', czn=profile.id, list_status=['1']),
        'count_draft': get_emp_count(search='', czn=czn, list_status=['0', '1']),
        'count_check': get_emp_count(search='', czn=czn, list_status=['2']),
        'count_work': get_emp_count(search='', czn=czn, list_status=['3', '4', '5', '6', '7', '11']),
        'count_ready': get_emp_count(search='', czn=czn, list_status=['9']),
        'count_closed': get_emp_count(search='', czn=czn, list_status=['12']),
    }
    return render(request, 'index.html', context)


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
            messages.info(request, 'Не правильно введенные данные')
            return redirect(reverse('login'))
    else:
        context = {'title': 'Авторизация',
                   'next': request.GET.get('next') if request.GET.get('next') else settings.SUCCESS_URL}
        return render(request, 'login.html', context)


######################################################################################################################


def logout(request) -> HttpResponse:
    """
    Выход пользователя
    :param request:
    :return:
    """
    auth.logout(request)
    return redirect(reverse('index'))


######################################################################################################################


def emp_list(request, list_status, title):
    """
    Отображение списка карточек в зависимости от статуса
    :param request:
    :param list_status:
    :param title:
    :return:
    """
    profile = get_object_or_404(UserProfile, user=request.user)
    if request.GET:
        page_number = int(request.GET.get('page', 1))
        start = (page_number - 1) * settings.COUNT_LIST
        stop = start + settings.COUNT_LIST
        if profile.role == 1 and not request.user.is_superuser:
            list_emp = get_emp_list(search='', czn=profile.user.id, list_status=list_status, start=start, stop=stop)
        else:
            list_emp = get_emp_list(search='', czn='0', list_status=list_status, start=start, stop=stop)
        return render(request, 'emp_list.html', {'emp_list': list_emp, })
    else:
        if profile.role == 1 and not request.user.is_superuser:
            emp_count = get_emp_count(search='', czn=profile.user.id, list_status=list_status)
            filter_czn_form = FormFilterCzn({'czn': profile.user.id})
        else:
            emp_count = get_emp_count(search='', czn='0', list_status=list_status)
            filter_czn_form = FormFilterCzn()
        context = {
            'profile': profile,
            'title': title,
            'per_page': settings.COUNT_LIST,
            'search_form': FormSearch(),
            'filter_czn_form': filter_czn_form,
            'filter_status_form': FormFilterStatus({'status': list_status[0]}),
            'emp_count': emp_count,
            'page_count': get_page_count(emp_count=emp_count),
        }
        return render(request, 'list.html', context)


######################################################################################################################


@login_required
def emp_find(request):
    """
    Отображение результата поиска карточек
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
        context['filter_czn_form'] = FormFilterCzn(request.POST)
        context['filter_status_form'] = FormFilterStatus(request.POST)
        if search_form.is_valid():
            search = request.POST.get('find', '')
            czn = request.POST.get('czn', '0')
            status = request.POST.get('status', '20')
            context['search_form'] = search_form
            emp_count = get_emp_count(search=search, czn=czn, list_status=[status])
            context['emp_count'] = emp_count
            context['page_count'] = get_page_count(emp_count=emp_count)
            context['emp_find'] = search
            context['emp_czn'] = czn
            context['emp_status'] = status
        else:
            return redirect(reverse('all'))
    elif request.GET:
        search = request.GET.get('emp_find', '')
        czn = request.GET.get('emp_czn', '0')
        status = request.GET.get('emp_status', '20')
        page_number = int(request.GET.get('page', 1))
        start = (page_number - 1) * settings.COUNT_LIST
        stop = start + settings.COUNT_LIST
        list_emp = get_emp_list(search=search, czn=czn, list_status=[status], start=start, stop=stop)
        return render(request, 'emp_list.html', {'emp_list': list_emp, })
    else:
        context['search_form'] = FormSearch()
        context['filter_czn_form'] = FormFilterCzn()
        context['filter_status_form'] = FormFilterStatus()
        emp_count = Employer.objects.all().count()
        context['emp_count'] = emp_count
        context['page_count'] = get_page_count(emp_count=emp_count)
        context['emp_find'] = ''
        context['emp_czn'] = '0'
        context['emp_status'] = '20'
    return render(request, 'list.html', context)


######################################################################################################################


@login_required
def emp_all_list(request):
    """
    Вывод списка всех карточек
    :param request:
    :return:
    """
    return emp_list(request, ['20'], 'Все карточки')


######################################################################################################################


@login_required
def emp_draft_list(request):
    """
    Вывод списка карточек в статусе Черновик
    :param request:
    :return:
    """
    return emp_list(request, ['0', '1'], 'Черновики')


######################################################################################################################


@login_required
def emp_check_list(request):
    """
    Вывод списка карточек в статусе Карточки на проверке
    :param request:
    :return:
    """
    return emp_list(request, ['2'], 'Карточки на проверке')


######################################################################################################################


@login_required
def emp_work_list(request):
    """
    Вывод списка карточек в статусе В работе
    :param request:
    :return:
    """
    return emp_list(request, ['3', '4', '5', '6', '7', '11'], 'Карточки в работе')


######################################################################################################################


@login_required
def emp_ready_list(request):
    """
    Вывод списка карточек в статусе Вынесено постановлений
    :param request:
    :return:
    """
    return emp_list(request, ['9'], 'Вынесено постановлений')


######################################################################################################################


@login_required
def emp_closed_list(request):
    """
    Вывод списка карточек в статусе Закрытые карточки
    :param request:
    :return:
    """
    return emp_list(request, ['12'], 'Закрытые карточки')


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
def export_to_spreadsheet(request):
    """
    Выгрузка данных в файл
    :param request:
    :return:
    """
    all_fields = Employer._meta.get_fields(include_parents=False, include_hidden=False)
    default_on_fileds = ['Title', 'INN', 'OGRN', 'Status', 'Owner', 'CreateDate', ]
    default_view_fileds = default_on_fileds + ['Number', 'JurAddress', 'FactAddress', 'SendDate', 'Contact', 'Respons']
    if request.POST:
        czn = request.POST.get('czn', '0')
        field_list = request.POST.getlist('fields')
        fields = []
        for field in all_fields:
            if field.name in default_view_fileds:
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
            if field.name in default_view_fileds:
                if field.name in default_on_fileds:
                    fields.append([field.name, field.verbose_name, True])
                else:
                    fields.append([field.name, field.verbose_name, False])
        context['fields'] = fields
        return render(request, 'export.html', context)


######################################################################################################################


def emp_export_ods(czn, fields):
    """

    :param czn:
    :param fields:
    :return:
    """
    all_fields = Employer._meta.get_fields(include_parents=False, include_hidden=False)
    now = datetime.now()
    file_name = 'export' + now.strftime('%y%m%d-%H%M%S') + '.ods'
    file = settings.EXPORT_FILE + file_name
    if czn != '0':
        emps = Employer.objects.filter(Owner__user=czn)
    else:
        emps = Employer.objects.all()
    data_field = []
    for field in all_fields:
        if field.name in fields:
            data_field.append(field.verbose_name)
    data_emp = [data_field]
    for emp in emps:
        data_field = []
        for field in all_fields:
            if field.name in fields:
                value = getattr(emp, field.name)
                if value:
                    if isinstance(value, UserProfile):
                        data_field.append(value.user.get_full_name())
                    elif isinstance(value, datetime) or isinstance(value, date):
                        data_field.append(value.strftime('%d-%m-%G'))
                    else:
                        if field.name == 'Status':
                            data_field.append(dict(STATUS_CHOICES).get(emp.Status))
                        else:
                            data_field.append(value)
                else:
                    data_field.append('')
        data_emp.append(data_field)
    data = OrderedDict()
    data.update({'Данные': data_emp})
    save_data(file, data)
    fp = open(file, 'rb')
    response = HttpResponse(fp.read())
    fp.close()
    file_type = mimetypes.guess_type(file)
    if file_type is None:
        file_type = 'application/octet-stream'
    response['Content-Type'] = file_type
    response['Content-Length'] = str(os.stat(file).st_size)
    response['Content-Disposition'] = "attachment; filename=" + file_name
    os.remove(file)

    return response


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
def temp_emp_list(request):
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

    form = FormEmp(
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
def inf_delete(request, inf_id):
    """

    :param request:
    :param inf_id:
    :return:
    """
    profile = get_object_or_404(UserProfile, user=request.user)
    inf = get_object_or_404(Info, id=inf_id)
    emp_id = inf.EmpInfoID_id
    if inf.EmpInfoID.Owner == profile:
        inf.Attache.delete()
        inf.delete()
    return redirect(reverse('emp', args=(emp_id,)))


######################################################################################################################


@login_required
def notify_delete(request, notify_id):
    """

    :param request:
    :param notify_id:
    :return:
    """
    profile = get_object_or_404(UserProfile, user=request.user)
    noti = get_object_or_404(Notify, id=notify_id)
    emp_id = noti.EmpNotifyID_id
    if noti.EmpNotifyID.Owner == profile:
        noti.Attache.delete()
        noti.delete()
    return redirect(reverse('emp', args=(emp_id,)))


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
def report_list(request):
    """

    :param request:
    :return:
    """
    context = {
        'profile': get_object_or_404(UserProfile, user=request.user),
        'title': 'Список отчетов',
    }
    return render(request, 'report_list.html', context)


######################################################################################################################


@login_required
def report_month(request):
    """
    Строит отчет за изменения в карточках за выбранный месяц
    :param request:
    :return:
    """
    curr_date = datetime(2018, 10, 1)
    if request.POST:
        if request.POST['month'].isdigit():
            month = int(request.POST['month'])
        else:
            month = datetime.now().month
    else:
        now = datetime.now()
        month = (now.year - curr_date.year) * 12 + now.month - curr_date.month
    i = 0
    while i < month:
        days = calendar.monthrange(curr_date.year, curr_date.month)[1]
        curr_date = curr_date + timedelta(days=days)
        i += 1
    emps = Employer.objects.filter(SendDate__month=curr_date.month)
    elist, aw, ac, ar, emp_all = report_filter(emps)
    context = {
        'profile': get_object_or_404(UserProfile, user=request.user),
        'title': 'Отчет за месяц',
        'month_form': FormMonth(initial={'month': month}),
        'elist': elist,
        'aw': aw,
        'ac': ac,
        'ar': ar,
        'emp_all': emp_all,
    }
    return render(request, 'report_month.html', context)


######################################################################################################################


@login_required
def report_date(request):
    """

    :param request:
    :return:
    """
    context = {
        'profile': get_object_or_404(UserProfile, user=request.user),
        'title': 'Отчет за выбранный период',
    }
    if request.POST:
        date_form = FormReportDates(request.POST)
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        if start_date and not end_date:
            emps = Employer.objects.filter(SendDate__gte=start_date)
        elif not start_date and end_date:
            emps = Employer.objects.filter(SendDate__lte=end_date)
        elif start_date and end_date:
            emps = Employer.objects.filter(SendDate__gte=start_date).filter(SendDate__lte=end_date)
        else:
            emps = Employer.objects.all()
        elist, aw, ac, ar, emp_all = report_filter(emps)
        context['date_form'] = date_form
        context['elist'] = elist
        context['aw'] = aw
        context['ac'] = ac
        context['ar'] = ar
        context['emp_all'] = emp_all
    else:
        context['date_form'] = FormReportDates()
    return render(request, 'report_date.html', context)


######################################################################################################################


@login_required
def response_list(request):
    """
    Список ответственных за работу с карточками
    :param request:
    :return:
    """
    profile = get_object_or_404(UserProfile, user=request.user)
    if profile.role == 4:
        context = {
            'profile': profile,
            'title': 'Назначение ответственных лиц',
            'list_emp': Employer.objects.filter(Respons__isnull=True)[:settings.STOP_LIST],
            'response_form': FormResponse(),
        }
        return render(request, 'response.html', context)
    else:
        redirect(reverse('index'))


######################################################################################################################


@login_required
def response_set(request):
    """
    Назначение ответственного за работу с карточкой
    :param request:
    :return:
    """
    profile = get_object_or_404(UserProfile, user=request.user)
    if profile.role == 4:
        if request.POST:
            id_response = request.POST['response']
            id_emp = request.POST['emp']
            emp = get_object_or_404(Employer, id=id_emp)
            response = get_object_or_404(UserProfile, id=id_response)
            emp.Respons = response
            emp.save()
    return redirect(reverse('responslist'))


######################################################################################################################

@login_required
@admin_only
def user_list(request):
    """
    Список пользователей
    :param request:
    :return:
    """
    list_all_user = User.objects.all()
    list_user = []
    for user in list_all_user:
        if not UserProfile.objects.filter(user=user).exists():
            list_user.append(user)
    context = {
        'profile': get_object_or_404(UserProfile, user=request.user),
        'title': 'Cписок пользователей',
        'role_form': FormRole(),
        'list_profile': UserProfile.objects.all(),
        'list_user': list_user,
    }
    return render(request, 'users.html', context)


######################################################################################################################


@login_required
@admin_only
def user_role_change(request):
    """
    Смена роли пользователю
    :param request:
    :return:
    """
    if request.POST:
        role = request.POST['role']
        user = request.POST['user']
        user_profile, created = UserProfile.objects.get_or_create(user_id=user, )
        if created:
            user_profile.user = get_object_or_404(User, id=user, )
        user_profile.role = role
        user_profile.save()
    return redirect(reverse('users'))


######################################################################################################################

@login_required
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
    return redirect(reverse('index'))


######################################################################################################################
