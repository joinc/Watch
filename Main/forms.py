# -*- coding: utf-8 -*-

from django import forms
from Main.models import UserProfile
from .choices import ROLE_CHOICES, EMPLOYER_CHOICES, PROTOCOL_CHOICES, RETURN_CHOICES, INFO_CHOICES, STATUS_CHOICES, METHOD_CHOICES, RESULT_CHOICES
from datetime import date, datetime, timedelta
import locale
import calendar

######################################################################################################################


class FormRole(forms.Form):
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        label='',
        initial=0,
        widget=forms.Select(attrs={'class': 'custom-select mb-0 mr-sm-2 mb-sm-0', 'id': 'inlineFormCustomSelect'}),
        required=True
    )

######################################################################################################################


class FormReturn(forms.Form):

    return_result = forms.ChoiceField(
        choices=RETURN_CHOICES,
        label='',
        initial=0,
        widget=forms.Select(attrs={'class': 'custom-select'}),
        required=True
    )

    return_comment = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'placeholder': 'Оставить комментарий', }),
        required=False,
    )

######################################################################################################################


class FormClose(forms.Form):

    close_comment = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'placeholder': 'Укажите причину', }),
        required=True,
    )

######################################################################################################################


class FormResult(forms.Form):

    resultat = forms.ChoiceField(
        choices=RESULT_CHOICES,
        label='',
        initial=0,
        widget=forms.Select(attrs={'class': 'custom-select'}),
        required=True
    )

######################################################################################################################


class FormSearch(forms.Form):

    find = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={'size': '40', 'placeholder': 'Введите ИНН или наименование организации', 'type': 'text', 'class': 'form-control', 'aria-label': 'Введите ИНН или наименование организации'}),
        required=False,
    )

######################################################################################################################


class FormEmp(forms.Form):

    oTitle = forms.CharField(
        label='Наименование работодателя',
        widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', }),
        required=True,
    )

    oJurAddress = forms.CharField(
        label='Юридический адрес',
        widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', }),
        required=True,
    )

    oFactAddress = forms.CharField(
        label='Фактический адрес',
        widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', }),
        required=True,
    )

    oInn = forms.CharField(
        label='ИНН',
        widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', }),
        required=True,
    )

    oOgrn = forms.CharField(
        label='ОГРН',
        widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', }),
        required=False,
    )

    oVacancyDate = forms.DateField(
        label='Дата размещения вакансии',
        widget=forms.widgets.DateInput(attrs={'type': 'date', }),
        input_formats=('%d.%m.%Y', '%d/%m/%Y', '%d-%m-%Y'),
        initial=date.today().__format__('%d.%m.%Y'),
        required=False,
    )

    oVacancyComment = forms.CharField(
        label='Комментарий даты размещения вакансии',
        widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'placeholder': 'Оставить комментарий', }),
        required=False,
    )

    oEventDate = forms.DateField(
        label='Дата последнего взаимодействия работодателя и центра занятости',
        widget=forms.widgets.DateInput(attrs={'type': 'date', }),
        input_formats=('%d.%m.%Y', '%d/%m/%Y', '%d-%m-%Y'),
        initial=date.today().__format__('%d.%m.%Y'),
        required=False,
    )

    oEventComment = forms.CharField(
        label='Комментарий даты взаимодействия',
        widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'placeholder': 'Оставить комментарий', }),
        required=False,
    )

    oSendDate = forms.DateField(
        label='Дата направления информации в отдел трудоустройства и специальных программ Главного управления государственной службы занятости населения Омской области',
        widget=forms.widgets.DateInput(attrs={'type': 'date', }),
        input_formats=('%d.%m.%Y', '%d/%m/%Y', '%d-%m-%Y'),
        initial=date.today().__format__('%d.%m.%Y'),
        required=False,
    )

    oContact = forms.CharField(
        label='Контакт основной',
        widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', }),
        required=False,
    )

    oInfName = forms.ChoiceField(
        choices=INFO_CHOICES,
        label='',
        initial=0,
        widget=forms.Select(attrs={'class': 'custom-select', }),
        required=True
    )

    oInfAttach = forms.FileField(
        label='',
        widget=forms.FileInput(attrs={'class': 'form-control-file'}),
        required=False,
    )

    oInfComment = forms.CharField(
        label='Комментарий',
        widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'placeholder': 'Оставить комментарий', }),
        required=False,
    )

    oNotifyMethod = forms.ChoiceField(
        choices=METHOD_CHOICES,
        label='Информирования работодателя центром занятости о необходимости предоставления информации о наличии свободных рабочих мест и вакантных должностей',
        initial=1,
        widget=forms.Select(attrs={'class': 'custom-select', 'placeholder': 'Выберите метод уведомления', }),
        required=True
    )

    oNotifyDate = forms.DateField(
        label='',
        widget=forms.widgets.DateInput(attrs={'type': 'date', }),
        input_formats=('%d.%m.%Y', '%d/%m/%Y', '%d-%m-%Y'),
        initial=date.today().__format__('%d.%m.%Y'),
        required=False,
    )

    oNotifyAttach = forms.FileField(
        label='',
        widget=forms.FileInput(attrs={'class': 'form-control-file'}),
        required=False,
    )

    oNotifyComment = forms.CharField(
        label='Комментарий',
        widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'placeholder': 'Оставить комментарий', }),
        required=False,
    )

######################################################################################################################


class FormNotice(forms.Form):

    notice = forms.FileField(
        label='',
        widget=forms.FileInput(attrs={'class': 'form-control-input'}),
        required=True,
    )

######################################################################################################################


class FormProtocol(forms.Form):

    employer = forms.ChoiceField(
        choices=EMPLOYER_CHOICES,
        label='',
        initial=0,
        widget=forms.Select(attrs={'class': 'custom-select mb-0 mr-sm-2 mb-sm-0', 'id': 'inlineFormCustomSelect'}),
        required=True
    )

    protocol = forms.ChoiceField(
        choices=PROTOCOL_CHOICES,
        label='',
        initial=0,
        widget=forms.Select(attrs={'class': 'custom-select mb-0 mr-sm-2 mb-sm-0', 'id': 'inlineFormCustomSelect'}),
        required=True
    )

    notice = forms.FileField(
        label='',
        widget=forms.FileInput(attrs={'class': 'form-control-input'}),
        required=False,
    )

######################################################################################################################


class FormFilterCzn(forms.Form):

    CZN_CHOICES = []
    CznList = UserProfile.objects.filter(role=1).order_by('user')
    CZN_CHOICES.append([0, 'Все ЦЗН'])
    for iCzn in CznList:
        CZN_CHOICES.append([iCzn.id, iCzn.user.get_full_name()])

    czn = forms.ChoiceField(
        choices=CZN_CHOICES,
        label='',
        initial=0,
        widget=forms.Select(attrs={'class': 'custom-select'}),
        required=True
    )

######################################################################################################################


class FormRespons(forms.Form):

    RESPONS_CHOICES = []
    ResponsList = UserProfile.objects.filter(role=3).order_by('user')
    for iRespons in ResponsList:
        RESPONS_CHOICES.append([iRespons.id, iRespons.user.get_full_name()])

    respons = forms.ChoiceField(
        choices=RESPONS_CHOICES,
        label='',
        widget=forms.Select(attrs={'class': 'custom-select'}),
        required=True
    )

######################################################################################################################


class FormFilterStatus(forms.Form):

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        label='',
        initial=20,
        widget=forms.Select(attrs={'class': 'custom-select'}),
        required=True
    )

######################################################################################################################


class FormMonth(forms.Form):

    MONTH_CHOICES = []
    locale.setlocale(locale.LC_ALL, 'ru')
    start_date = datetime(2018, 10, 1)
    curr_date = start_date
    today_date = datetime.now()
    count = (today_date.year - start_date.year) * 12 + today_date.month - start_date.month
    i = 0
    MONTH_CHOICES.append([i, start_date.strftime('%B %Y г.')])
    while i < count:
        days = calendar.monthrange(start_date.year, start_date.month)[1]
        curr_date = curr_date + timedelta(days=days)
        i += 1
        MONTH_CHOICES.append([i, curr_date.strftime('%B %Y г.')])

    month = forms.ChoiceField(
        choices=MONTH_CHOICES,
        label='',
        widget=forms.Select(attrs={'class': 'custom-select'}),
        required=True
    )

######################################################################################################################
