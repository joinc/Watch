# -*- coding: utf-8 -*-

from django.http import HttpResponseNotFound
from django.shortcuts import get_object_or_404
from Main.models import UserProfile, Event

######################################################################################################################


def create_event(employer_id, profile, comment, attache):
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


def get_profile(profile=None, user=None) -> UserProfile:
    """
    ПОлучение профиля пользователя
    :param profile:
    :param user:
    :return: UserProfile
    """
    if profile:
        return get_object_or_404(UserProfile, id=profile)
    if user:
        return get_object_or_404(UserProfile, user=user)
    return HttpResponseNotFound()


######################################################################################################################
