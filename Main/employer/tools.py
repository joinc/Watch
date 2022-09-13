# -*- coding: utf-8 -*-

from datetime import date, datetime
from django.http import HttpResponse
from django.conf import settings
from pyexcel_ods3 import save_data
from collections import OrderedDict
from Main.choices import STATUS_CHOICES
from Main.models import UserProfile, Employer, WidgetStatus, Widget
import mimetypes
import os

######################################################################################################################


def get_count_page(count_employer) -> int:
    """
    Возвращает количество страниц
    :param count_employer:
    :return:
    """
    count_page = count_employer // settings.COUNT_LIST
    if count_employer % settings.COUNT_LIST > 0:
        count_page += 1
    return count_page


######################################################################################################################


def get_count_employer(profile, widget_id):
    """
    Получение количества карточек нарушителя для выбранного виджета, по его id, и с фильтрацие по роли отдела профиля,
    если роль ЦЗН, то считаются только карточки принадлежащие данному ЦЗН, остальным отправляется общее количество
    карточек нарушителей в выбранном виджете.
    :param profile:
    :param widget_id:
    :return: Количество карточек в определенном виджете для пользователя
    """
    list_status = WidgetStatus.objects.filter(widget__id=widget_id, checked=True, )
    if profile.department.role == 'czn':
        return Employer.objects.filter(
            status_new__StatusWidget__in=list_status,
            Owner__department=profile.department,
        ).count()
    else:
        return Employer.objects.filter(
            status_new__StatusWidget__in=list_status,
        ).count()


######################################################################################################################


def get_count_find_employer(find, czn, list_status) -> int:
    """
    Возвращает количество карточек нарушителей по заданным критериям
    :param find:
    :param czn:
    :param list_status:
    :return:
    """
    if find and czn and list_status:
        return len(
            set(
                list(
                    Employer.objects.filter(
                        INN__icontains=find,
                        Owner__department__id=czn,
                        status_new__StatusWidget__in=list_status,
                    ).values_list('id', flat=True)
                ) + list(
                    Employer.objects.filter(
                        Title__icontains=find,
                        Owner__department__id=czn,
                        status_new__StatusWidget__in=list_status,
                    ).values_list('id', flat=True)
                )
            )
        )
    elif find and czn and not list_status:
        return len(
            set(
                list(
                    Employer.objects.filter(
                        INN__icontains=find,
                        Owner__department__id=czn,
                    ).values_list('id', flat=True)
                ) + list(
                    Employer.objects.filter(
                        Title__icontains=find,
                        Owner__department__id=czn,
                    ).values_list('id', flat=True)
                )
            )
        )
    elif find and not czn and list_status:
        return len(
            set(
                list(
                    Employer.objects.filter(
                        INN__icontains=find,
                        status_new__StatusWidget__in=list_status,
                    ).values_list('id', flat=True)
                ) + list(
                    Employer.objects.filter(
                        Title__icontains=find,
                        status_new__StatusWidget__in=list_status,
                    ).values_list('id', flat=True)
                )
            )
        )
    elif find and not czn and not list_status:
        return len(
            set(
                list(
                    Employer.objects.filter(INN__icontains=find, ).values_list('id', flat=True)
                ) + list(
                    Employer.objects.filter(Title__icontains=find, ).values_list('id', flat=True)
                )
            )
        )
    elif not find and czn and list_status:
        return Employer.objects.filter(Owner__department__id=czn, status_new__StatusWidget__in=list_status, ).count()
    elif not find and czn and not list_status:
        return Employer.objects.filter(Owner__department__id=czn, ).count()
    elif not find and not czn and list_status:
        return Employer.objects.filter(status_new__StatusWidget__in=list_status, ).count()
    else:
        return Employer.objects.all().count()


######################################################################################################################


def get_list_employer(find, czn, list_status, start, stop) -> list:
    """
    Возвращает список карточек нарушителей по заданным критериям
    :param find:
    :param czn:
    :param list_status:
    :param start:
    :param stop:
    :return:
    """
    if find and czn and list_status:
        list_search_id_employer = list(
            set(
                list(
                    Employer.objects.filter(
                        INN__icontains=find,
                        Owner__department__id=czn,
                        status_new__StatusWidget__in=list_status,
                    ).values_list('id', flat=True)
                ) + list(
                    Employer.objects.filter(
                        Title__icontains=find,
                        Owner__department__id=czn,
                        status_new__StatusWidget__in=list_status,
                    ).values_list('id', flat=True)
                )
            )
        )
    elif find and czn and not list_status:
        list_search_id_employer = list(
            set(
                list(
                    Employer.objects.filter(
                        INN__icontains=find,
                        Owner__department__id=czn,
                    ).values_list('id', flat=True)
                ) + list(
                    Employer.objects.filter(
                        Title__icontains=find,
                        Owner__department__id=czn,
                    ).values_list('id', flat=True)
                )
            )
        )
    elif find and not czn and list_status:
        list_search_id_employer = list(
            set(
                list(
                    Employer.objects.filter(
                        INN__icontains=find,
                        status_new__StatusWidget__in=list_status,
                    ).values_list('id', flat=True)
                ) + list(
                    Employer.objects.filter(
                        Title__icontains=find,
                        status_new__StatusWidget__in=list_status,
                    ).values_list('id', flat=True)
                )
            )
        )
    elif find and not czn and not list_status:
        list_search_id_employer = list(
            set(
                list(
                    Employer.objects.filter(
                        INN__icontains=find,
                    ).values_list('id', flat=True)
                ) + list(
                    Employer.objects.filter(
                        Title__icontains=find,
                    ).values_list('id', flat=True)
                )
            )
        )
    elif not find and czn and list_status:
        list_search_id_employer = list(
            Employer.objects.filter(
                Owner__department__id=czn,
                status_new__StatusWidget__in=list_status,
            ).values_list('id', flat=True)
        )
    elif not find and czn and not list_status:
        list_search_id_employer = list(
            Employer.objects.filter(
                Owner__department__id=czn,
            ).values_list('id', flat=True)
        )
    elif not find and not czn and list_status:
        list_search_id_employer = list(
            Employer.objects.filter(
                status_new__StatusWidget__in=list_status,
            ).values_list('id', flat=True)
        )
    else:
        list_search_id_employer = list(Employer.objects.all().values_list('id', flat=True))
    list_search_employer = Employer.objects.filter(id__in=list_search_id_employer)[start:stop]
    return list_search_employer


######################################################################################################################


def get_list_widget(profile):
    """
    Функция возвращает объект Widget и количество карточек подходящих
    :param profile:
    :return:
    """
    list_widget = []
    for widget in Widget.objects.all():
        count = get_count_employer(profile=profile, widget_id=widget.id)
        list_widget.append((widget, count))
    return list_widget


######################################################################################################################


def get_list_existing_employer(employer):
    """

    :param employer:
    :return:
    """
    result = list(Employer.objects.filter(INN__exact=employer.INN).exclude(id=employer.id))
    return result


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
