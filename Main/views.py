# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import auth, User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404, redirect, reverse
from .forms import FormRole, FormResult, FormSearch, FormEmp, FormNotice, FormFilterCzn, FormFilterStatus, \
    FormRespons, FormMonth, FormReportDates
from .choices import RESULT_CHOICES, STATUS_CHOICES
from .models import UserProfile, TempEmployer, Employer, Event, Notify, Info, ConfigWatch
from Main import message, tools
from django.conf import settings
from pyexcel_ods3 import save_data
from collections import OrderedDict
import xlrd
import calendar
import mimetypes
import os

######################################################################################################################


@login_required
def index(request):

    profile = get_object_or_404(UserProfile, user=request.user)
    oAll = Employer.objects.all().count()
    if profile.role == 1:
        oEmp = Employer.objects.filter(Owner=profile)
        oAllMe = oEmp.count()
        oEdit = oEmp.filter(Status=1).count()
    else:
        oEmp = Employer.objects.all()
        oAllMe = 0
        oEdit = 0
    oDraft = oEmp.filter(Status=0).count() + oEmp.filter(Status=1).count()
    oCheck = oEmp.filter(Status=2).count()
    oReady = oEmp.filter(Status=9).count()
    oClosed = oEmp.filter(Status=12).count()
    oWork = 0
    for i in [3, 4, 5, 6, 7, 11]:
        oWork = oWork + oEmp.filter(Status=i).count()
    return render(request, 'index.html',
                  {'profile': profile, 'oAll': oAll, 'oDraft': oDraft, 'oCheck': oCheck, 'oWork': oWork,
                   'oReady': oReady, 'oEdit': oEdit, 'oClosed': oClosed, 'oAllMe': oAllMe, })

######################################################################################################################


def login(request):
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user:
            auth.login(request, user)
            #return redirect(request.META.get('HTTP_REFERER'))
            return redirect(settings.SUCCESS_URL)
        else:
            messages.info(request, 'Не правильно введенные данные')
            return redirect(reverse('login'))
    else:
        return render(request, 'login.html')

######################################################################################################################


def logout(request):
    auth.logout(request)
    return redirect(reverse('index'))

######################################################################################################################


def emp_list(request, status, breadcrumb):
    oEmp = []
    profile = get_object_or_404(UserProfile, user=request.user)
    search_form = FormSearch()
    filter_czn_form = FormFilterCzn()
    for i in status:
        if profile.role == 1 and not request.user.is_superuser:
            for emp in tools.emp_filter('', profile.user.id, i):
                oEmp.append(emp)
            filter_czn_form = FormFilterCzn({'czn': profile.user.id})
        else:
            for emp in tools.emp_filter('', '0', i):
                oEmp.append(emp)
    if status.__len__() == 1:
        filter_status_form = FormFilterStatus({'status': status[0]})
    else:
        filter_status_form = FormFilterStatus()

    emp_count = oEmp.__len__()
    page_count = emp_count // settings.COUNT_LIST
    if emp_count % settings.COUNT_LIST > 0:
        page_count += 1

    if request.GET:
        page_number = int(request.GET.get('page', 1))
        START_LIST = (page_number - 1) * settings.COUNT_LIST
        STOP_LIST = START_LIST + settings.COUNT_LIST
        oEmp = oEmp[START_LIST:STOP_LIST]
        return render(request, 'emp_list.html', {'oEmp': oEmp, })
    else:
        oEmp = oEmp[0:settings.COUNT_LIST]
        return render(request, 'list.html',
                      {'oEmp': oEmp, 'search_form': search_form, 'filter_czn_form': filter_czn_form,
                       'filter_status_form': filter_status_form, 'emp_count': emp_count, 'profile': profile,
                       'per_page': settings.COUNT_LIST, 'page_count': page_count, 'breadcrumb': breadcrumb, })

######################################################################################################################


@login_required
def emp_find_list(request):

    def get_page_count(emp_count):
        page_count = emp_count // settings.COUNT_LIST
        if emp_count % settings.COUNT_LIST > 0:
            page_count += 1
        return page_count

    profile = get_object_or_404(UserProfile, user=request.user)
    breadcrumb = 'Поиск карточек'
    if request.POST:
        search_form = FormSearch(request.POST)
        filter_czn_form = FormFilterCzn(request.POST)
        filter_status_form = FormFilterStatus(request.POST)
        if search_form.is_valid():
            # Если нажата кнопка "Сформировать и скачать таблицу" то выгружается все записи
            emp_find = request.POST['find']
            emp_czn = request.POST['czn']
            emp_status = request.POST['status']
            oEmp = tools.emp_filter(emp_find, emp_czn, emp_status)[0:settings.COUNT_LIST]
            emp_count = tools.emp_filter(emp_find, emp_czn, emp_status).count()
        else:
            return redirect(reverse('all'))
    elif request.GET:
        page_number = int(request.GET.get('page', 1))
        emp_find = request.GET.get('emp_find', '')
        emp_czn = request.GET.get('emp_czn', '0')
        emp_status = request.GET.get('emp_status', '20')
        START_LIST = (page_number - 1) * settings.COUNT_LIST
        STOP_LIST = START_LIST + settings.COUNT_LIST
        oEmp = tools.emp_filter(emp_find, emp_czn, emp_status)[START_LIST:STOP_LIST]
        return render(request, 'emp_list.html', {'oEmp': oEmp, })
    else:
        search_form = FormSearch()
        filter_czn_form = FormFilterCzn()
        filter_status_form = FormFilterStatus()
        oEmp = Employer.objects.all()
        emp_count = Employer.objects.all().count()
        emp_find = ''
        emp_czn = '0'
        emp_status = '20'

    return render(request, 'list.html',
                  {'oEmp': oEmp, 'search_form': search_form, 'filter_czn_form': filter_czn_form,
                   'filter_status_form': filter_status_form, 'emp_count': emp_count, 'profile': profile,
                   'per_page': settings.COUNT_LIST, 'page_count': get_page_count(emp_count), 'emp_find': emp_find,
                   'emp_czn': emp_czn, 'emp_status': emp_status, 'breadcrumb': breadcrumb, })

######################################################################################################################


@login_required
def emp_all_list(request):
    # Выводит список всех карточек
    return emp_list(request, range(13), 'Все карточки')

######################################################################################################################


@login_required
def emp_draft_list(request):
    # Выводит список карточек в статусе Черновик
    return emp_list(request, ['0', '1'], 'Черновики')

######################################################################################################################


@login_required
def emp_check_list(request):
    # Выводит список карточек в статусе Карточки на проверке
    return emp_list(request, ['2'], 'Карточки на проверке')

######################################################################################################################


@login_required
def emp_work_list(request):
    # Выводит список карточек в статусе В работе
    return emp_list(request, ['3', '4', '5', '6', '7', '11'], 'Карточки в работе')

######################################################################################################################


@login_required
def emp_ready_list(request):
    # Выводит список карточек в статусе Вынесено постановлений
    return emp_list(request, ['9'], 'Вынесено постановлений')

######################################################################################################################


@login_required
def emp_closed_list(request):
    # Выводит список карточек в статусе Закрытые карточки
    return emp_list(request, ['12'], 'Закрытые карточки')

######################################################################################################################


@login_required
def emp_load(request):
    if not request.user.is_superuser:
        return redirect(reverse('index'))
    profile = get_object_or_404(UserProfile, user=request.user)

    return render(request, 'load.html', {'profile': profile, })

######################################################################################################################


@login_required
def emp_upload(request):
    if not request.user.is_superuser:
        return redirect(reverse('index'))

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
                oTempEmp = TempEmployer()
                oTempEmp.Number = row[0]
                oTempEmp.Title = row[1]
                oTempEmp.INN = row[2]
                oTempEmp.OGRN = row[3]
                oTempEmp.JurAddress = row[4]
                oTempEmp.FactAddress = row[5]
                oTempEmp.Contact = row[6]
                if row[7] != '':
                    td = xlrd.xldate_as_tuple(row[7], 0)
                    dd = date(td[0], td[1], td[2])
                    row[7] = dd.strftime("%Y-%m-%d")
                    oTempEmp.EventDate = dd

                oTempEmp.save()

        os.remove(file)
    UpDate = ConfigWatch()
    UpDate.UploadDate = datetime.now()
    UpDate.save()
    return redirect(reverse('emps'))

######################################################################################################################


@login_required
def export_to_spreadsheet(request):

    profile = get_object_or_404(UserProfile, user=request.user)
    all_fields = Employer._meta.get_fields(include_parents=False, include_hidden=False)
    default_on_fileds = ['Title', 'INN', 'OGRN', 'Status', 'Owner', 'CreateDate', ]
    default_view_fileds = default_on_fileds + ['Number', 'JurAddress', 'FactAddress', 'SendDate', 'Contact', 'Respons']
    if request.POST:
        czn = request.POST['czn']
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
        if profile.role == 1 and not request.user.is_superuser:
            filter_czn_form = FormFilterCzn({'czn': profile.user.id})
        else:
            filter_czn_form = FormFilterCzn()
        fields = []
        for field in all_fields:
            if field.name in default_view_fileds:
                if field.name in default_on_fileds:
                    fields.append([field.name, field.verbose_name, True])
                else:
                    fields.append([field.name, field.verbose_name, False])

    return render(request, 'export.html', {'profile': profile, 'fields': fields, 'filter_czn_form': filter_czn_form, })

######################################################################################################################


def emp_export_ods(czn, fields):
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
    tools.event_create(emp, emp.Owner, 'Создана карточка предприятия', None)
    if profile.role == 1:
        return redirect(reverse('edit', args=(emp.id,)))
    elif profile.role == 3:
        return redirect(reverse('archedit', args=(emp.id,)))
    else:
        return redirect(reverse('delete', args=(emp.id, )))

######################################################################################################################


@login_required
def temp_arch_new(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    emp = Employer()
    emp.Status = 0
    emp.Owner = profile
    emp.RegKatharsis = False
    emp.Archive = True
    emp.save()
    tools.event_create(emp, emp.Owner, 'Создана карточка предприятия', None)
    if profile.role == 3:
        return redirect(reverse('archedit', args=(emp.id,)))
    else:
        return redirect(reverse('delete', args=(emp.id, )))

######################################################################################################################


@login_required
def temp_emp_list(request):
    oFind = ''
    profile = get_object_or_404(UserProfile, user=request.user)
    if request.POST:
        search_form = FormSearch(request.POST)
        if search_form.is_valid():
            oFind = request.POST['find']
            oTempEmp = TempEmployer.objects.filter(INN__startswith=oFind)
            if oTempEmp.count() == 0:
                oTempEmp = TempEmployer.objects.filter(Title__icontains=oFind)
            scnt = oTempEmp.count()
            aEmp = oTempEmp[settings.START_LIST:settings.STOP_LIST]
        else:
            return redirect(reverse('emps'))
    else:
        search_form = FormSearch
        scnt = TempEmployer.objects.all().count()
        aEmp = TempEmployer.objects.all()[settings.START_LIST:settings.STOP_LIST]
    vcnt = aEmp.count()
    pemp = []
    for emp in aEmp:
        for emp_f in Employer.objects.filter(INN=emp.INN):
            pemp.append(emp_f)
    update = ConfigWatch.objects.all().first()

    return render(request, 'emps.html',
                  {'aEmp': aEmp, 'profile': profile, 'search_form': search_form, 'find': oFind, 'scnt': scnt,
                   'vcnt': vcnt, 'pemp': pemp, 'update': update, })

######################################################################################################################


@login_required
def employer_arch_edit(request, employer_id):
    emp = get_object_or_404(Employer, id=employer_id)
    profile = get_object_or_404(UserProfile, user=request.user)
    if emp.Owner != profile or (emp.Status != 0 and emp.Status != 1):
        return redirect(reverse('emp', args=(emp.id,)))

    form = FormEmp(initial={'oTitle': emp.Title,
                            'oJurAddress': emp.JurAddress,
                            'oFactAddress': emp.FactAddress,
                            'oInn': emp.INN,
                            'oOgrn': emp.OGRN,
                            'oVacancyDate': tools.e_date(emp.VacancyDate),
                            'oVacancyComment': emp.VacancyComment,
                            'oEventDate': tools.e_date(emp.EventDate),
                            'oEventComment': emp.EventComment,
                            'oSendDate': tools.e_date(emp.SendDate),
                            'oContact': emp.Contact, })

    result_form = FormResult()
    notice_form = FormNotice()
    eventlist = Event.objects.filter(EmpEventID=emp)

    return render(request, 'arch.html',
                  {'form': form, 'profile': profile, 'emp': emp, 'eventlist': eventlist, 'notice_form': notice_form,
                   'result_form': result_form, 'pemp': tools.p_emp_list(emp.INN), })

######################################################################################################################


@login_required
def employer_arch_save(request, employer_id):
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
        tools.event_create(emp, profile, comment, myfile)
        message.message_create(emp.id, 0, comment, profile)
        return redirect(reverse('emp', args=(emp.id,)))

    return redirect(reverse('index'))

######################################################################################################################


@login_required
def notify_add(request, employer_id):
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
        tools.event_create(emp, profile, comment, myfile)
        message.message_create(emp.id, 0, comment, profile)

        return redirect(reverse('emp', args=(emp.id,)))

    return redirect(reverse('index'))

######################################################################################################################


@login_required
def report_list(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    breadcrumb = 'Список отчетов'
    return render(request, 'reports.html',
                  {'profile': profile, 'breadcrumb': breadcrumb, })

######################################################################################################################


@login_required
def report_month(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    curr_date = datetime(2018, 10, 1)
    breadcrumb = 'Отчет за месяц'
    if request.POST:
        month = int(request.POST['month'])
    else:
        now = datetime.now()
        month = (now.year - curr_date.year) * 12 + now.month - curr_date.month
    month_form = FormMonth({'month': month})
    i = 0
    while i < month:
        days = calendar.monthrange(curr_date.year, curr_date.month)[1]
        curr_date = curr_date + timedelta(days=days)
        i += 1
    emps = Employer.objects.filter(SendDate__month=curr_date.month)
    elist, aw, ac, ar, emp_all = tools.report_filter(emps)
    '''
    plist = UserProfile.objects.filter(role=1)
    elist = []
    aw = 0
    ac = 0
    ar = 0
    emp_all = 0
    for u in plist:
        emp_count = emps.filter(Owner=u).count()
        emp_closed = emps.filter(Owner=u).filter(Status=12).count()
        emp_ready = emps.filter(Owner=u).filter(Status=9).count()
        emp_work = emp_count - emp_closed - emp_ready
        percent_closed = 100 * emp_closed // emp_count if emp_count else 0
        percent_ready = 100 * emp_ready // emp_count if emp_count else 0
        percent_work = 100 * emp_work // emp_count if emp_count else 0
        if emp_count > 0:
            emp_all += emp_count
            aw += emp_work
            ac += emp_closed
            ar += emp_ready
            elist.append([u, emp_count, emp_work, emp_closed, emp_ready, percent_work, percent_closed, percent_ready])
    '''
    return render(request, 'report_month.html',
                  {'profile': profile, 'breadcrumb': breadcrumb, 'month_form': month_form, 'elist': elist, 'aw': aw,
                   'ac': ac, 'ar': ar, 'emp_all': emp_all, })

######################################################################################################################


@login_required
def report_date(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    breadcrumb = 'Отчет за выбранный период'
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
        elist, aw, ac, ar, emp_all = tools.report_filter(emps)
        return render(request, 'report_date.html',
                      {'profile': profile, 'breadcrumb': breadcrumb, 'date_form': date_form, 'elist': elist, 'aw': aw,
                       'ac': ac, 'ar': ar, 'emp_all': emp_all, })
    else:
        date_form = FormReportDates()

    return render(request, 'report_date.html',
                  {'profile': profile, 'breadcrumb': breadcrumb, 'date_form': date_form, })

######################################################################################################################


@login_required
def respons_list(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    breadcrumb = 'Назначение ответственных лиц'
    respons_form = FormRespons()
    elist = Employer.objects.filter(Respons__isnull=True)[settings.START_LIST:settings.STOP_LIST]

    return render(request, 'respons.html',
                  {'elist': elist, 'profile': profile, 'breadcrumb': breadcrumb, 'respons_form': respons_form, })

######################################################################################################################


@login_required
def respons_set(request):
    if request.POST:
        oRespons = request.POST['respons']
        oEmp = request.POST['emp']
    else:
        return redirect(reverse('responslist'))

    emp = get_object_or_404(Employer, id=oEmp)
    respons = get_object_or_404(UserProfile, id=oRespons)
    emp.Respons = respons
    emp.save()

    return redirect(reverse('responslist'))

######################################################################################################################


def user_list(request):
    if not request.user.is_superuser:
        return redirect(reverse('index'))

    profile = get_object_or_404(UserProfile, user=request.user)
    role_form = FormRole()
    userlist = User.objects.all()
    plist = UserProfile.objects.all()
    ulist = []
    for u in userlist:
        if UserProfile.objects.filter(user=u).count() == 0:
            ulist.append(u)

    return render(request, 'users.html',
                  {'ulist': ulist, 'plist': plist, 'role_form': role_form, 'profile': profile, })

######################################################################################################################


def user_role(request):
    if not request.user.is_superuser:
        return redirect(reverse('index'))

    if request.POST:
        oRole = request.POST['role']
        oUser = request.POST['user']
    else:
        return redirect(reverse('users'))

    profiles = UserProfile.objects.filter(user_id=oUser)
    if len(profiles) > 0:
        user_profile = profiles[0]
        user_profile.role = oRole
        user_profile.save()
    else:
        user_profile = UserProfile()
        user_profile.user = get_object_or_404(User, id=oUser)
        user_profile.role = oRole
        user_profile.save()

    return redirect(reverse('users'))

######################################################################################################################


def send_email(request):
    if not request.user.is_superuser:
        return redirect(reverse('index'))

    email = ['yubelyakov@omskzan.ru']
    data = """
    Привет.
    Это тестовое письмо.
    ---
    С Уважением Робот.
    """
    send_mail('Заголовок', data, settings.DEFAULT_FROM_EMAIL, email, fail_silently=False)
    return redirect(reverse('index'))

######################################################################################################################
