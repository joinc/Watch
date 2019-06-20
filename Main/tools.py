# -*- coding: utf-8 -*-

from Main.models import Event, Employer

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
    if emp_date != None:
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

    oEmp = Employer.objects.all()
    if oFind != '':
        oEmp = oEmp.filter(INN__istartswith=oFind)
        if oEmp.count() == 0:
            oEmp = Employer.objects.filter(Title__icontains=oFind)
    if oCzn != '0':
        oEmp = oEmp.filter(Owner__user=oCzn)
    if oStatus != '20':
        oEmp = oEmp.filter(Status=oStatus)

    return oEmp
