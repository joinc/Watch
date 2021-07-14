# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .forms import FormMonth, FormReportDates
from .models import UserProfile, Employer
from .tools import report_filter
import calendar


######################################################################################################################


@login_required
def report_list(request):
    """
    Список отчетов
    :param request:
    :return:
    """
    context = {
        'profile': get_object_or_404(UserProfile, user=request.user),
        'title': 'Список отчетов',
    }
    return render(request, 'report/list.html', context)


######################################################################################################################


@login_required
def report_month(request):
    """
    Построение отчета по изменениям в карточках за выбранный месяц
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
    return render(request, 'report/month.html', context)


######################################################################################################################


@login_required
def report_date(request):
    """
    Построение отчета по изменениям в карточках за выбранный период
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
    return render(request, 'report/date.html', context)


######################################################################################################################
