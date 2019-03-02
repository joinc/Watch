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


def e_date(empDate):
    returnDate = None
    if empDate != None:
        returnDate = empDate.__format__('%Y-%m-%d')

    return returnDate

######################################################################################################################


def p_emp_list(inn):
    pemp = []
    emps = Employer.objects.filter(INN__exact=inn)
    for emp in emps:
        pemp.append(emp)

    return pemp

######################################################################################################################