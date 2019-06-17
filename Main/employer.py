# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from Main.models import UserProfile, Employer, Event, Info, Notify
from Main import tools, message
from datetime import datetime
from .forms import FormReturn, FormResult, FormEmp, FormNotice, FormProtocol, FormClose
from .choices import RETURN_CHOICES

######################################################################################################################


def employer_new(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    profile = get_object_or_404(UserProfile, user=request.user)
    emp = Employer()
    emp.Owner = profile
    emp.RegKatharsis = False
    emp.save()
    tools.event_create(emp, emp.Owner, 'Создана карточка предприятия', None)
    return HttpResponseRedirect(reverse('edit', args=(emp.id,)))

######################################################################################################################


def employer_view(request, employer_id):

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    profile = get_object_or_404(UserProfile, user=request.user)
    emp = get_object_or_404(Employer, id=employer_id)
    if emp.Owner == profile and (emp.Status == 0 or emp.Status == 1):
        return HttpResponseRedirect(reverse('edit', args=(emp.id,)))

    return_form = FormReturn()
    result_form = FormResult()
    notice_form = FormNotice()
    close_form = FormClose()
    protocol_form = FormProtocol()
    eventlist = Event.objects.filter(EmpEventID=emp)
    infolist = Info.objects.filter(EmpInfoID=emp)
    notifylist = Notify.objects.filter(EmpNotifyID=emp)
    form = FormEmp()

    if profile.role == 4:
        return render(request, 'emp.html',
                      {'emp': emp, 'form': form, 'profile': profile, 'eventlist': eventlist, 'infolist': infolist,
                       'notifylist': notifylist, 'pemp': tools.p_emp_list(emp.INN)})
    elif profile.role == 3:
        return render(request, 'emp.html',
               {'emp': emp, 'form': form, 'profile': profile, 'close_form': close_form, 'result_form': result_form,
                'eventlist': eventlist, 'infolist': infolist, 'notifylist': notifylist,
                'pemp': tools.p_emp_list(emp.INN), 'notice_form': notice_form, 'protocol_form': protocol_form})
    else:
        return render(request, 'emp.html',
                      {'emp': emp, 'form': form, 'profile': profile, 'return_form': return_form,
                       'close_form': close_form, 'result_form': result_form, 'eventlist': eventlist,
                       'infolist': infolist, 'notifylist': notifylist, 'pemp': tools.p_emp_list(emp.INN),
                       'notice_form': notice_form, 'protocol_form': protocol_form})

######################################################################################################################


def employer_save(request, employer_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

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
            return HttpResponseRedirect(reverse('edit', args=(emp.id,)))
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
            return HttpResponseRedirect(reverse('edit', args=(emp.id,)))
        elif 'send' in request.POST:
            emp.SendDate = datetime.now()
            emp.Status = 2
        emp.save()
        tools.event_create(emp, profile, 'Сохранена карточка предприятия, направлена на проверку в отдел '
                                         'трудоустройства и специальных программ Главного управления', None)
        return HttpResponseRedirect(reverse('emp', args=(emp.id,)))

    return HttpResponseRedirect(reverse('index'))

######################################################################################################################


def employer_edit(request, employer_id):

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    emp = get_object_or_404(Employer, id=employer_id)
    profile = get_object_or_404(UserProfile, user=request.user)
    if emp.Owner != profile or (emp.Status != 0 and emp.Status != 1):
        return HttpResponseRedirect(reverse('emp', args=(emp.id,)))

    if emp.Archive:
        return HttpResponseRedirect(reverse('archedit', args=(emp.id,)))

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
#    notice_form = FormNotice()
    eventlist = Event.objects.filter(EmpEventID=emp)
    infolist = Info.objects.filter(EmpInfoID=emp)
    notifylist = Notify.objects.filter(EmpNotifyID=emp)

    return render(request, 'edit.html', {'form': form, 'profile': profile, 'emp': emp, 'eventlist': eventlist,
                                         'infolist': infolist, 'notifylist': notifylist,
                                         'pemp': tools.p_emp_list(emp.INN), })

######################################################################################################################


def employer_print(request, employer_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    profile = get_object_or_404(UserProfile, user=request.user)
    emp = get_object_or_404(Employer, id=employer_id)
    eventlist = Event.objects.filter(EmpEventID=emp)
    infolist = Info.objects.filter(EmpInfoID=emp)
    notifylist = Notify.objects.filter(EmpNotifyID=emp)

    return render(request, 'print.html', {'emp': emp, 'profile': profile, 'eventlist': eventlist, 'infolist': infolist, 'notifylist': notifylist, })

######################################################################################################################


def employer_delete(request, employer_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    profile = get_object_or_404(UserProfile, user=request.user)
    emp = get_object_or_404(Employer, id=employer_id)
    if (emp.Status == 0 and emp.Owner == profile) or profile.role == 3:
        emp.delete()
    return HttpResponseRedirect(reverse('index'))

######################################################################################################################


def employer_audit(request, employer_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    if request.POST:
        profile = get_object_or_404(UserProfile, user=request.user)
        emp = get_object_or_404(Employer, id=employer_id)
        if 'accept' in request.POST:
            emp.Status = 3
            emp.save()
            accept_message = 'Карточка предприятия согласована, направлена для составления протокола об административном правонарушении'
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

        return HttpResponseRedirect(reverse('emp', args=(emp.id,)))

    return HttpResponseRedirect(reverse('index'))

######################################################################################################################


def employer_close(request, employer_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    if request.POST:
        profile = get_object_or_404(UserProfile, user=request.user)
        emp = get_object_or_404(Employer, id=employer_id)
        if profile.role == 3:
            emp.Status = 12
            emp.save()
            oComment = request.POST['close_comment']
            close_message = 'Карточка предприятия закрыта по причине: ' + oComment
            tools.event_create(emp, profile, close_message, None)
            message.message_create(emp.id, 0, close_message, profile)
        return HttpResponseRedirect(reverse('emp', args=(emp.id,)))
    return HttpResponseRedirect(reverse('index'))
