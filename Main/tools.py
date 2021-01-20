# -*- coding: utf-8 -*-

from Main.models import Event, Employer, UserProfile
from django.conf import settings

######################################################################################################################


def event_create(empid, profile, comment, attache):
    """

    :param empid:
    :param profile:
    :param comment:
    :param attache:
    :return:
    """
    oEvent = Event()
    oEvent.EmpEventID = empid
    oEvent.Owner = profile
    oEvent.Comment = comment
    if attache:
        oEvent.Attache.save(attache.name, attache)
    else:
        oEvent.Attache = None
    oEvent.save()

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
    page_count = emp_count // settings.COUNT_LIST
    if emp_count % settings.COUNT_LIST > 0:
        page_count += 1
    return page_count


######################################################################################################################


def get_emp_count(search, czn, list_status):
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
