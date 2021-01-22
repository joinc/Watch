# -*- coding: utf-8 -*-

from datetime import date, datetime
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from pyexcel_ods3 import save_data
from collections import OrderedDict
from Main.forms import FormResult, FormSearch, FormEmp, FormNotice, FormFilterCzn
from Main.choices import RESULT_CHOICES, STATUS_CHOICES
from Main.models import UserProfile, TempEmployer, Employer, Event, Notify, Info, ConfigWatch
from Main.message import message_create
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


def event_create(employer_id, profile, comment, attache):
    """

    :param employer_id:
    :param profile:
    :param comment:
    :param attache:
    :return:
    """
    event = Event(EmpEventID=employer_id, Owner=profile, Comment=comment)
    if attache:
        event.Attache.save(attache.name, attache)
    else:
        event.Attache = None
    event.save()


######################################################################################################################


def e_date(emp_date):
    """

    :param emp_date:
    :return:
    """
    return_date = None
    if emp_date is not None:
        return_date = emp_date.__format__('%Y-%m-%d')

    return return_date


######################################################################################################################


def p_emp_list(inn):
    """

    :param inn:
    :return:
    """
    pemp = []
    emps = Employer.objects.filter(INN__exact=inn)
    for emp in emps:
        pemp.append(emp)

    return pemp


######################################################################################################################


def report_filter(emps):
    """

    :param emps:
    :return:
    """
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
    result = [elist, aw, ac, ar, emp_all]
    return result


######################################################################################################################


def get_page_count(emp_count):
    """

    :param emp_count:
    :return:
    """
    page_count = emp_count // settings.COUNT_LIST
    if emp_count % settings.COUNT_LIST > 0:
        page_count += 1
    return page_count


######################################################################################################################


def get_emp_count(search, czn, list_status):
    """

    :param search:
    :param czn:
    :param list_status:
    :return:
    """
    count = 0
    for status in list_status:
        if status == '20' or status == '':
            if czn == '0':
                if search == '':
                    count = Employer.objects.all().count()
                else:
                    count = Employer.objects.filter(INN__istartswith=search).count() \
                            + Employer.objects.filter(Title__icontains=search).count()
            else:
                if search == '':
                    count = Employer.objects.filter(Owner__user=czn).count()
                else:
                    count = Employer.objects.filter(INN__istartswith=search, Owner__user=czn).count() \
                            + Employer.objects.filter(Title__icontains=search, Owner__user=czn).count()
            return count
        else:
            if czn == '0':
                if search == '':
                    count += Employer.objects.filter(Status=status).count()
                else:
                    count += Employer.objects.filter(INN__istartswith=search, Status=status).count()
                    count += Employer.objects.filter(Title__icontains=search, Status=status).count()
            else:
                if search == '':
                    count += Employer.objects.filter(Status=status, Owner__user=czn).count()
                else:
                    count += Employer.objects.filter(INN__istartswith=search, Status=status, Owner__user=czn).count()
                    count += Employer.objects.filter(Title__icontains=search, Status=status, Owner__user=czn).count()
    return count


######################################################################################################################


def get_emp_list(search, czn, list_status, start, stop):
    class EmpList:
        """
        Класс списка организаций
        """
        def __init__(self):
            self.list_emp = []

        def equal(self, query):
            """
            Присвоить список организаций
            :param query:
            :return:
            """
            self.list_emp.clear()
            self.append(query)

        def append(self, query):
            """
            Добавление в список организаций элементов из запроса
            :param query:
            :return:
            """
            for emp in query:
                self.list_emp.append(emp)

        def total(self):
            """
            Возвращает список организаций
            :return:
            """
            return self.list_emp

    emp_list = EmpList()
    for status in list_status:
        if status == '20' or status == '':
            if czn == '0':
                if search == '':
                    emp_list.equal(Employer.objects.all())
                else:
                    emp_list.equal(Employer.objects.filter(INN__istartswith=search))
                    emp_list.append(Employer.objects.filter(Title__icontains=search))
            else:
                if search == '':
                    emp_list.equal(Employer.objects.filter(Owner__user=czn))
                else:
                    emp_list.equal(Employer.objects.filter(INN__istartswith=search, Owner__user=czn))
                    emp_list.append(Employer.objects.filter(Title__icontains=search, Owner__user=czn))
            # Прерываем цикл for, чтобы не задублировать записи
            break
        else:
            if czn == '0':
                if search == '':
                    emp_list.append(Employer.objects.filter(Status=status))
                else:
                    emp_list.append(Employer.objects.filter(INN__istartswith=search, Status=status))
                    emp_list.append(Employer.objects.filter(Title__icontains=search, Status=status))
            else:
                if search == '':
                    emp_list.append(Employer.objects.filter(Status=status, Owner__user=czn))
                else:
                    emp_list.append(Employer.objects.filter(INN__istartswith=search, Status=status, Owner__user=czn))
                    emp_list.append(Employer.objects.filter(Title__icontains=search, Status=status, Owner__user=czn))
    return emp_list.total()[start:stop]


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
    default_view_fileds = default_on_fileds + ['Number', 'JurAddress', 'FactAddress', 'SendDate', 'Contact', 'Response']
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
    Удаление notify
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
