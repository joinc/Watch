# -*- coding: utf-8 -*-

from datetime import date, datetime
from django.http import HttpResponse
from django.shortcuts import redirect, reverse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from pyexcel_ods3 import save_data
from collections import OrderedDict
from Main.choices import STATUS_CHOICES
from Main.models import UserProfile, Employer, Event
import mimetypes
import os

######################################################################################################################


def admin_only(function):
    """
    Декоратор, проверят, что-бы пользователь обладал правами суперпользователя
    :param function:
    :return:
    """
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


def get_page_count(emp_count) -> int:
    """
    Возвращает количество страниц
    :param emp_count:
    :return:
    """
    page_count = emp_count // settings.COUNT_LIST
    if emp_count % settings.COUNT_LIST > 0:
        page_count += 1
    return page_count


######################################################################################################################


def get_employer_count(search, czn, list_status) -> int:
    """
    Возвращает количество карточек нарушителей по заданным критериям
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
                    count = Employer.objects.filter(Owner=czn).count()
                else:
                    count = Employer.objects.filter(INN__istartswith=search, Owner=czn).count() \
                            + Employer.objects.filter(Title__icontains=search, Owner=czn).count()
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
                    count += Employer.objects.filter(Status=status, Owner=czn).count()
                else:
                    count += Employer.objects.filter(INN__istartswith=search, Status=status, Owner=czn).count()
                    count += Employer.objects.filter(Title__icontains=search, Status=status, Owner=czn).count()
    return count


######################################################################################################################


def get_list_employer(search, czn, list_status, start, stop) -> list:
    """
    Возвращает список карточек нарушителей по заданным критериям
    :param search:
    :param czn:
    :param list_status:
    :param start:
    :param stop:
    :return:
    """
    class EmployerList:
        """
        Класс списка организаций
        """
        def __init__(self):
            self.list_employer = []

        def equal(self, query):
            """
            Присвоить список организаций
            :param query:
            :return:
            """
            self.list_employer.clear()
            self.append(query)

        def append(self, query):
            """
            Добавление в список организаций элементов из запроса
            :param query:
            :return:
            """
            for emp in query:
                self.list_employer.append(emp)

        def total(self):
            """
            Возвращает список организаций
            :return:
            """
            return self.list_employer

    list_employer = EmployerList()
    for status in list_status:
        if status == '20' or status == '':
            if czn == '0':
                if search == '':
                    list_employer.equal(Employer.objects.all())
                else:
                    list_employer.equal(Employer.objects.filter(INN__istartswith=search, ))
                    list_employer.append(Employer.objects.filter(Title__icontains=search, ))
            else:
                if search == '':
                    list_employer.equal(Employer.objects.filter(Owner=czn, ))
                else:
                    list_employer.equal(Employer.objects.filter(INN__istartswith=search, Owner=czn, ))
                    list_employer.append(Employer.objects.filter(Title__icontains=search, Owner=czn, ))
            # Прерываем цикл for, чтобы не задублировать записи
            break
        else:
            if czn == '0':
                if search == '':
                    list_employer.append(Employer.objects.filter(Status=status, ))
                else:
                    list_employer.append(Employer.objects.filter(INN__istartswith=search, Status=status, ))
                    list_employer.append(Employer.objects.filter(Title__icontains=search, Status=status, ))
            else:
                if search == '':
                    list_employer.append(Employer.objects.filter(Status=status, Owner=czn, ))
                else:
                    list_employer.append(Employer.objects.filter(INN__istartswith=search, Status=status, Owner=czn, ))
                    list_employer.append(Employer.objects.filter(Title__icontains=search, Status=status, Owner=czn, ))
    return list_employer.total()[start:stop]


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
