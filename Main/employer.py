# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from datetime import datetime, date
from Main import tools, message
from Main.models import UserProfile, Employer, Event, Info, Notify, TempEmployer, ConfigWatch
from Main.forms import FormReturn, FormResult, FormEmp, FormNotice, FormProtocol, FormClose, FormResponse, FormSearch, \
    FormFilterCzn, FormFilterStatus
from Main.tools import get_emp_count, get_emp_list, get_page_count, admin_only
from Main.choices import RETURN_CHOICES
import xlrd
import os

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
def employer_new(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    employer = Employer(Owner=profile, RegKatharsis=False, )
    employer.save()
    tools.event_create(employer, employer.Owner, 'Создана карточка предприятия', None)
    return redirect(reverse('edit', args=(employer.id,)))


######################################################################################################################


@login_required
def employer_view(request, employer_id):
    profile = get_object_or_404(UserProfile, user=request.user)
    employer = get_object_or_404(Employer, id=employer_id)
    if employer.Owner == profile and (employer.Status == 0 or employer.Status == 1):
        return redirect(reverse('edit', args=(employer.id,)))

    context = {
        'profile': profile,
        'title': 'Карточка учета работодателя',
        'form': FormEmp(),
        'emp': employer,
        'notifylist': Notify.objects.filter(EmpNotifyID=employer),
        'eventlist': Event.objects.filter(EmpEventID=employer),
        'infolist': Info.objects.filter(EmpInfoID=employer),
        'pemp': tools.p_emp_list(employer.INN),
    }
    if profile.role == 4:
        context['response_form'] = FormResponse()
    else:
        context['close_form'] = FormClose()
        context['result_form'] = FormResult()
        context['notice_form'] = FormNotice()
        context['protocol_form'] = FormProtocol()
        if profile.role != 3:
            context['return_form'] = FormReturn()
    return render(request, 'emp.html', context)


######################################################################################################################


@login_required
def employer_save(request, employer_id):
    profile = get_object_or_404(UserProfile, user=request.user)
    if request.POST:
        emp = get_object_or_404(Employer, id=employer_id)
        emp.Title = request.POST['oTitle']
        emp.JurAddress = request.POST['oJurAddress']
        emp.FactAddress = request.POST['oFactAddress']
        emp.INN = request.POST['oInn']
        emp.OGRN = request.POST['oOgrn']
        if request.POST['oVacancyDate']:
            emp.VacancyDate = request.POST['oVacancyDate']
        if request.POST['oEventDate']:
            emp.EventDate = request.POST['oEventDate']
        emp.VacancyComment = request.POST['oVacancyComment']
        emp.EventComment = request.POST['oEventComment']
        emp.Contact = request.POST['oContact']
        if 'info' in request.POST:
            inf = Info()
            inf.EmpInfoID = emp
            if request.FILES:
                myfile = request.FILES['oInfAttach']
                inf.Attache.save(myfile.name, myfile)
            inf.Comment = request.POST['oInfComment']
            inf.Name = request.POST['oInfName']
            inf.save()
            emp.save()
            return redirect(reverse('edit', args=(emp.id,)))
        elif 'notify' in request.POST:
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
            emp.save()
            return redirect(reverse('edit', args=(emp.id,)))
        elif 'send' in request.POST:
            emp.SendDate = datetime.now()
            emp.Status = 2
        emp.save()
        tools.event_create(emp, profile, 'Сохранена карточка предприятия, направлена на проверку в департамент '
                                         'занятости населения Министерства труда и социального развития', None)
        return redirect(reverse('emp', args=(emp.id,)))
    return redirect(reverse('index'))


######################################################################################################################


@login_required
def employer_edit(request, employer_id):
    emp = get_object_or_404(Employer, id=employer_id)
    profile = get_object_or_404(UserProfile, user=request.user)
    if emp.Owner != profile or (emp.Status != 0 and emp.Status != 1):
        return redirect(reverse('emp', args=(emp.id,)))
    if emp.Archive:
        return redirect(reverse('archedit', args=(emp.id,)))

    form = FormEmp(
        initial={
            'oTitle': emp.Title,
            'oJurAddress': emp.JurAddress,
            'oFactAddress': emp.FactAddress,
            'oInn': emp.INN,
            'oOgrn': emp.OGRN,
            'oVacancyDate': tools.e_date(emp.VacancyDate),
            'oVacancyComment': emp.VacancyComment,
            'oEventDate': tools.e_date(emp.EventDate),
            'oEventComment': emp.EventComment,
            'oSendDate': tools.e_date(emp.SendDate),
            'oContact': emp.Contact,
        }
    )
#    notice_form = FormNotice()
    context = {
        'profile': profile,
        'title': 'Редактирование карточки предприятия',
        'form': form,
        'emp': emp,
        'eventlist': Event.objects.filter(EmpEventID=emp),
        'infolist': Info.objects.filter(EmpInfoID=emp),
        'notifylist': Notify.objects.filter(EmpNotifyID=emp),
        'pemp': tools.p_emp_list(emp.INN),
    }
    return render(request, 'edit.html', context)


######################################################################################################################


@login_required
def employer_print(request, employer_id):
    employer = get_object_or_404(Employer, id=employer_id)
    context = {
        'profile': get_object_or_404(UserProfile, user=request.user),
        'emp': employer,
        'eventlist': Event.objects.filter(EmpEventID=employer),
        'infolist': Info.objects.filter(EmpInfoID=employer),
        'notifylist': Notify.objects.filter(EmpNotifyID=employer),
    }
    return render(request, 'print.html', context)


######################################################################################################################


@login_required
def employer_delete(request, employer_id):
    profile = get_object_or_404(UserProfile, user=request.user)
    emp = get_object_or_404(Employer, id=employer_id)
    if (emp.Status == 0 and emp.Owner == profile) or profile.role == 3:
        emp.delete()
    return redirect(reverse('index'))


######################################################################################################################


@login_required
def employer_audit(request, employer_id):
    if request.POST:
        profile = get_object_or_404(UserProfile, user=request.user)
        emp = get_object_or_404(Employer, id=employer_id)
        if 'accept' in request.POST:
            emp.Status = 3
            emp.save()
            accept_message = 'Карточка предприятия согласована, направлена для составления протокола об ' \
                             'административном правонарушении'
            tools.event_create(emp, profile, accept_message, None)
            message.message_create(emp.id, 0, accept_message, profile)
        elif 'return' in request.POST:
            emp.Status = 1
            emp.save()
            try:
                oReturn = int(request.POST['return_result'])
            except ValueError:
                oReturn = 1
            oComment = request.POST['return_comment']
            return_message = 'Карточка предприятия возвращена по причине: ' + dict(RETURN_CHOICES).get(oReturn)
            if oComment != '':
                return_message = return_message + ' (' + oComment + ')'
            tools.event_create(emp, profile, return_message, None)
            message.message_create(emp.id, 0, return_message, profile)
        return redirect(reverse('emp', args=(emp.id,)))
    return redirect(reverse('index'))


######################################################################################################################


@login_required
def employer_close(request, employer_id):
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
    return emp_list(request, ['20'], 'Все карточки')


######################################################################################################################


@login_required
def employer_draft(request):
    """
    Вывод списка карточек в статусе Черновик
    :param request:
    :return:
    """
    return emp_list(request, ['0', '1'], 'Черновики')


######################################################################################################################


@login_required
def employer_check(request):
    """
    Вывод списка карточек в статусе Карточки на проверке
    :param request:
    :return:
    """
    return emp_list(request, ['2'], 'Карточки на проверке')


######################################################################################################################


@login_required
def employer_work(request):
    """
    Вывод списка карточек в статусе В работе
    :param request:
    :return:
    """
    return emp_list(request, ['3', '4', '5', '6', '7', '11'], 'Карточки в работе')


######################################################################################################################


@login_required
def employer_ready(request):
    """
    Вывод списка карточек в статусе Вынесено постановлений
    :param request:
    :return:
    """
    return emp_list(request, ['9'], 'Вынесено постановлений')


######################################################################################################################


@login_required
def employer_closed(request):
    """
    Вывод списка карточек в статусе Закрытые карточки
    :param request:
    :return:
    """
    return emp_list(request, ['12'], 'Закрытые карточки')


######################################################################################################################
