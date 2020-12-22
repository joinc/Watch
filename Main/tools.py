# -*- coding: utf-8 -*-

from Main.models import Event, Employer, UserProfile

######################################################################################################################


def event_create(empid, profile, comment, attache):
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
    return_date = None
    if emp_date is not None:
        return_date = emp_date.__format__('%Y-%m-%d')

    return return_date

######################################################################################################################


def p_emp_list(inn):
    pemp = []
    emps = Employer.objects.filter(INN__exact=inn)
    for emp in emps:
        pemp.append(emp)

    return pemp

######################################################################################################################


def emp_filter(oFind, oCzn, oStatus):
    # Функция отбора карточек предприятий
    oEmp = Employer.objects.filter(INN__istartswith=oFind)
    if oEmp.count() == 0:
        oEmp = Employer.objects.filter(Title__icontains=oFind)
    if oCzn != '0':
        oEmp = oEmp.filter(Owner__user=oCzn)
    if oStatus != '20' and oStatus != '':
        oEmp = oEmp.filter(Status=oStatus)
    oEmp = oEmp.order_by('Status')

    return oEmp


######################################################################################################################


def report_filter(emps):
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
