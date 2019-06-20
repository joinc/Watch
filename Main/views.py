# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.views.generic.edit import FormView
from Main.models import UserProfile, TempEmployer, Employer, Event, Notify, ConfigWatch
from Main import message, tools
from datetime import date, datetime, timedelta
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .forms import FormRole, FormResult, FormSearch, FormEmp, FormNotice, FormFilterCzn, FormFilterStatus, \
    FormRespons, FormMonth
from .choices import RESULT_CHOICES
from django.conf import settings
import xlrd
import calendar
from pyexcel_ods3 import save_data
from collections import OrderedDict
import mimetypes, os

######################################################################################################################


def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

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


def emp_list(request, profile, status, breadcrumb):

    oEmp = []
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
    acnt = oEmp.__len__()
    oEmp = oEmp[settings.START_LIST:settings.STOP_LIST]
    vcnt = oEmp.__len__()
    return render(request, 'list.html',
                  {'oEmp': oEmp, 'search_form': search_form, 'filter_czn_form': filter_czn_form,
                   'filter_status_form': filter_status_form, 'acnt': acnt, 'vcnt': vcnt, 'profile': profile,
                   'breadcrumb': breadcrumb})

######################################################################################################################


def emp_find_list(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    profile = get_object_or_404(UserProfile, user=request.user)
    breadcrumb = 'Все карточки'
    if request.POST:
        search_form = FormSearch(request.POST)
        filter_czn_form = FormFilterCzn(request.POST)
        filter_status_form = FormFilterStatus(request.POST)
        if search_form.is_valid():
            oEmp = tools.emp_filter(request.POST['find'], request.POST['czn'], request.POST['status'])
        else:
            return HttpResponseRedirect(reverse('all'))
        if 'export' in request.POST:
            now = datetime.now()
            file_name = 'export' + now.strftime('%y%m%d-%H%M%S') + '.ods'
            data_emp = [['ID', 'Название', 'ИНН']]
            data = OrderedDict()
            for emp in oEmp:
                data_emp.append([emp.id, emp.Title, emp.INN])
            data.update({'Данные': data_emp})
            save_data(file_name, data)
            fp = open(file_name, 'rb')
            response = HttpResponse(fp.read())
            fp.close()
            file_type = mimetypes.guess_type(file_name)
            if file_type is None:
                file_type = 'application/octet-stream'
            response['Content-Type'] = file_type
            response['Content-Length'] = str(os.stat(file_name).st_size)
            response['Content-Disposition'] = "attachment; filename=" + file_name
            os.remove(file_name)

            return response
    else:
        search_form = FormSearch()
        filter_czn_form = FormFilterCzn()
        filter_status_form = FormFilterStatus()
        oEmp = Employer.objects.all()


    acnt = oEmp.count()
    oEmp = oEmp[settings.START_LIST:settings.STOP_LIST]
    vcnt = oEmp.count()
    return render(request, 'list.html', {'oEmp': oEmp, 'search_form': search_form, 'filter_czn_form': filter_czn_form,
                                         'filter_status_form': filter_status_form, 'acnt': acnt, 'vcnt': vcnt,
                                         'profile': profile, 'breadcrumb': breadcrumb})

######################################################################################################################
# Выводит список всех карточек

def emp_all_list(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    profile = get_object_or_404(UserProfile, user=request.user)
    return emp_list(request, profile, range(11), 'Все карточки')


######################################################################################################################
# Выводит список карточек в статусе Черновик

def emp_draft_list(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    profile = get_object_or_404(UserProfile, user=request.user)
    return emp_list(request, profile, ['0', '1'], 'Черновики')

######################################################################################################################
# Выводит список карточек в статусе Карточки на проверке

def emp_check_list(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    profile = get_object_or_404(UserProfile, user=request.user)
    return emp_list(request, profile, ['2'], 'Карточки на проверке')

######################################################################################################################
# Выводит список карточек в статусе В работе

def emp_work_list(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    profile = get_object_or_404(UserProfile, user=request.user)
    return emp_list(request, profile, ['3', '4', '5', '6', '7', '11'], 'Карточки в работе')

######################################################################################################################
# Выводит список карточек в статусе Вынесено постановлений

def emp_ready_list(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    profile = get_object_or_404(UserProfile, user=request.user)
    return emp_list(request, profile, ['9'], 'Вынесено постановлений')

######################################################################################################################
# Выводит список карточек в статусе Закрытые карточки

def emp_closed_list(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    profile = get_object_or_404(UserProfile, user=request.user)
    return emp_list(request, profile, ['12'], 'Закрытые карточки')

######################################################################################################################


def emp_load(request):
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse('index'))
    profile = get_object_or_404(UserProfile, user=request.user)

    return render(request, 'load.html', {'profile': profile, })

######################################################################################################################


def emp_upload(request):
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse('index'))

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
    return HttpResponseRedirect(reverse('emps'))

######################################################################################################################


def emp_export(request):
    now = datetime.now()
    file_name = 'export' + now.strftime('%y%m%d-%H%M%S') + '.ods'
    data = OrderedDict()
    data.update({'Sheet 1': [['ID', 'AGE', 'SCORE'], [1, 22, 5], [2, 15, 6], [3, 28, 9]]})
    data.update({'Sheet 2': [['X', 'Y', 'Z'], [1, 2, 3], [4, 5, 6], [7, 8, 9]]})
    data.update({'Sheet 3': [['M', 'N', 'O', 'P'], [10, 11, 12, 13], [14, 15, 16, 17], [18, 19, 20, 21]]})
    save_data(file_name, data)
    fp = open(file_name, 'rb')
    response = HttpResponse(fp.read())
    fp.close()
    file_type = mimetypes.guess_type(file_name)
    if file_type is None:
        file_type = 'application/octet-stream'
    response['Content-Type'] = file_type
    response['Content-Length'] = str(os.stat(file_name).st_size)
    response['Content-Disposition'] = "attachment; filename=" + file_name
    os.remove(file_name)

    return response

######################################################################################################################


def create_temp_emp(request, temp_employer_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

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
        return HttpResponseRedirect(reverse('edit', args=(emp.id,)))
    elif profile.role == 3:
        return HttpResponseRedirect(reverse('archedit', args=(emp.id,)))
    else:
        return HttpResponseRedirect(reverse('delete', args=(emp.id, )))

######################################################################################################################


def temp_arch_new(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    profile = get_object_or_404(UserProfile, user=request.user)
    emp = Employer()
    emp.Status = 0
    emp.Owner = profile
    emp.RegKatharsis = False
    emp.Archive = True
    emp.save()
    tools.event_create(emp, emp.Owner, 'Создана карточка предприятия', None)
    if profile.role == 3:
        return HttpResponseRedirect(reverse('archedit', args=(emp.id,)))
    else:
        return HttpResponseRedirect(reverse('delete', args=(emp.id, )))

######################################################################################################################


def temp_emp_list(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    oFind = ''
    profile = get_object_or_404(UserProfile, user=request.user)
    if request.POST:
        search_form = FormSearch(request.POST)
        if search_form.is_valid():
            oFind = request.POST['find']
            scnt = TempEmployer.objects.filter(INN__istartswith=oFind).count()
            aEmp = TempEmployer.objects.filter(INN__istartswith=oFind)[settings.START_LIST:settings.STOP_LIST]
        else:
            return HttpResponseRedirect(reverse('emps'))
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


class LoginFormView(FormView):
    form_class = AuthenticationForm

    # Аналогично регистрации, только используем шаблон аутентификации.
    template_name = "login.html"
    # В случае успеха перенаправим на главную.
    success_url = settings.SUCCESS_URL

    def form_valid(self, form):
        # Получаем объект пользователя на основе введённых в форму данных.
        self.user = form.get_user()
        # Выполняем аутентификацию пользователя.
        login(self.request, self.user)

        return super(LoginFormView, self).form_valid(form)

######################################################################################################################


def Logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

######################################################################################################################


def employer_arch_edit(request, employer_id):

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    emp = get_object_or_404(Employer, id=employer_id)
    profile = get_object_or_404(UserProfile, user=request.user)
    if emp.Owner != profile or (emp.Status != 0 and emp.Status != 1):
        return HttpResponseRedirect(reverse('emp', args=(emp.id,)))

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


def employer_arch_save(request, employer_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

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
        return HttpResponseRedirect(reverse('emp', args=(emp.id,)))

    return HttpResponseRedirect(reverse('index'))

######################################################################################################################


def notify_add(request, employer_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

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
        return HttpResponseRedirect(reverse('emp', args=(emp.id,)))

######################################################################################################################


def notify_delete(request, notify_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    profile = get_object_or_404(UserProfile, user=request.user)
    noti = get_object_or_404(Notify, id=notify_id)
    emp_id = noti.EmpNotifyID_id
    if noti.EmpNotifyID.Owner == profile:
        noti.Attache.delete()
        noti.delete()
    return HttpResponseRedirect(reverse('emp', args=(emp_id,)))

######################################################################################################################


def event_add(request, employer_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

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
                    status = 12
                if protocol_form == '3':
                    comment = 'Работодатель (индивидуальный предприниматель) не получил уведомление, не явился на ' \
                              'составление протокола. Карточка закрыта.'
                    status = 12
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

        return HttpResponseRedirect(reverse('emp', args=(emp.id,)))

    return HttpResponseRedirect(reverse('index'))

######################################################################################################################


def report_list(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    profile = get_object_or_404(UserProfile, user=request.user)
    breadcrumb = 'Список отчетов'
    month_form = FormMonth()
    return render(request, 'reports.html',
                  {'profile': profile, 'breadcrumb': breadcrumb, 'month_form': month_form, })

######################################################################################################################


def report_view(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    profile = get_object_or_404(UserProfile, user=request.user)
    breadcrumb = 'Отчет на выбранную дату'
    if request.POST:
        month = int(request.POST['month'])
        month_form = FormMonth({'month': month})
    else:
        return HttpResponseRedirect(reverse('reportlist'))
    curr_date = datetime(2018, 10, 1)
    i = 0
    while i < month:
        days = calendar.monthrange(curr_date.year, curr_date.month)[1]
        curr_date = curr_date + timedelta(days=days)
        i += 1
    plist = UserProfile.objects.filter(role=1)
    elist = []
    aw = 0
    ac = 0
    ar = 0
    emp_all = 0
    for u in plist:
        emp_count = Employer.objects.filter(SendDate__month=curr_date.month).filter(Owner=u).count()
        emp_closed = Employer.objects.filter(SendDate__month=curr_date.month).filter(Owner=u).filter(Status=12).count()
        emp_ready = Employer.objects.filter(SendDate__month=curr_date.month).filter(Owner=u).filter(Status=9).count()
        emp_work = emp_count - emp_closed - emp_ready
        percent_closed = 100*emp_closed//emp_count if emp_count else 0
        percent_ready = 100*emp_ready//emp_count if emp_count else 0
        percent_work = 100*emp_work//emp_count if emp_count else 0
        if emp_count > 0:
            emp_all += emp_count
            aw += emp_work
            ac += emp_closed
            ar += emp_ready
            elist.append([u, emp_count, emp_work, emp_closed, emp_ready, percent_work, percent_closed, percent_ready])

    return render(request, 'report_view.html',
                  {'profile': profile, 'breadcrumb': breadcrumb, 'curr_date': curr_date, 'month_form': month_form,
                   'elist': elist, 'aw': aw, 'ac': ac, 'ar': ar, 'emp_all': emp_all })

######################################################################################################################


def respons_list(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    profile = get_object_or_404(UserProfile, user=request.user)
    breadcrumb = 'Назначение ответственных лиц'
    respons_form = FormRespons()
    elist = Employer.objects.filter(Respons__isnull=True)[settings.START_LIST:settings.STOP_LIST]

    return render(request, 'respons.html',
                  {'elist': elist, 'profile': profile, 'breadcrumb': breadcrumb, 'respons_form': respons_form, })

######################################################################################################################


def respons_set(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    if request.POST:
        oRespons = request.POST['respons']
        oEmp = request.POST['emp']
    else:
        return HttpResponseRedirect(reverse('responslist'))

    emp = get_object_or_404(Employer, id=oEmp)
    respons = get_object_or_404(UserProfile, id=oRespons)
    emp.Respons = respons
    emp.save()

    return HttpResponseRedirect(reverse('responslist'))

######################################################################################################################


def user_list(request):
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse('index'))

    profile = get_object_or_404(UserProfile, user=request.user)
    role_form = FormRole()
    userlist = User.objects.all()
    plist = UserProfile.objects.all()
    ulist = []
    for u in userlist:
        if UserProfile.objects.filter(user=u).count() == 0:
            ulist.append(u)

    return render(request, 'users.html', {'ulist': ulist, 'plist': plist, 'role_form': role_form, 'profile': profile, })

######################################################################################################################


def user_role(request):
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse('index'))

    if request.POST:
        oRole = request.POST['role']
        oUser = request.POST['user']
    else:
        return HttpResponseRedirect(reverse('users'))

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

    return HttpResponseRedirect(reverse('users'))

######################################################################################################################


def send_email(request):
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse('index'))

    email = ['yubelyakov@omskzan.ru']
    data = """
    Привет.
    Это тестовое письмо.
    ---
    С Уважением Робот.
    """
    send_mail('Заголовок', data, settings.DEFAULT_FROM_EMAIL, email, fail_silently=False)
    return HttpResponseRedirect(reverse('index'))
