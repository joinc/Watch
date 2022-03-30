# -*- coding: utf-8 -*-

from django import forms
from django.conf import settings
from datetime import date, datetime, timedelta
from Main.models import User, UserProfile, Info, Notify, Employer, Status
from Main.choices import EMPLOYER_CHOICES, PROTOCOL_CHOICES, RETURN_CHOICES, RESULT_CHOICES
import locale
import calendar

######################################################################################################################


class FormRole(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'super_role',
        ]
        widgets = {
            'super_role': forms.Select(
                attrs={
                    'class': 'custom-select',
                }
            ),
        }
        labels = {
            'super_role': 'Выберите новую роль:',
        }


######################################################################################################################


class FormReturn(forms.Form):
    return_result = forms.ChoiceField(
        choices=RETURN_CHOICES,
        label='',
        initial=0,
        widget=forms.Select(
            attrs={
                'class': 'custom-select',
            }
        ),
        required=True
    )
    return_comment = forms.CharField(
        label='',
        widget=forms.TextInput(
            attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Оставить комментарий',
            }
        ),
        required=False,
    )


######################################################################################################################


class FormClose(forms.Form):
    close_comment = forms.CharField(
        label='',
        widget=forms.TextInput(
            attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Укажите причину',
            }
        ),
        required=True,
    )


######################################################################################################################


class FormResult(forms.Form):
    result = forms.ChoiceField(
        choices=RESULT_CHOICES,
        label='',
        initial=0,
        widget=forms.Select(
            attrs={
                'class': 'custom-select',
            }
        ),
        required=True
    )


######################################################################################################################


class FormSearch(forms.Form):
    find = forms.CharField(
        label='',
        widget=forms.TextInput(
            attrs={
                'width': '300px;',
                'placeholder': 'Введите ИНН или наименование организации',
                'type': 'text', 'class': 'form-control',
                'aria-label': 'Введите ИНН или наименование организации'
            }
        ),
        required=False,
    )


######################################################################################################################


class FormEmployerNew(forms.ModelForm):
    class Meta:
        model = Employer
        fields = [
            'Title',
            'JurAddress',
            'FactAddress',
            'INN',
            'OGRN',
            'VacancyDate',
            'VacancyComment',
            'EventDate',
            'EventComment',
            'Contact',
        ]
        labels = {
            'Title': 'Наименование работодателя:',
            'JurAddress': 'Юридический адрес:',
            'FactAddress': 'Фактический адрес:',
            'INN': 'ИНН:',
            'OGRN': 'ОГРН:',
            'VacancyDate': 'Дата размещения вакансии:',
            'VacancyComment': '',
            'EventDate': 'Дата последнего взаимодействия работодателя и центра занятости:',
            'EventComment': '',
            'Contact': 'Контакт основной:',
        }
        widgets = {
            'Title': forms.TextInput(
                attrs={
                    'type': 'text',
                    'class': 'form-control',
                }
            ),
            'JurAddress': forms.TextInput(
                attrs={
                    'type': 'text',
                    'class': 'form-control',
                }
            ),
            'FactAddress': forms.TextInput(
                attrs={
                    'type': 'text',
                    'class': 'form-control',
                }
            ),
            'INN': forms.TextInput(
                attrs={
                    'type': 'text',
                    'class': 'form-control',
                }
            ),
            'OGRN': forms.TextInput(
                attrs={
                    'type': 'text',
                    'class': 'form-control',
                }
            ),
            'VacancyDate': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'type': 'date',
                }
            ),
            'VacancyComment': forms.TextInput(
                attrs={
                    'type': 'text',
                    'class': 'form-control',
                }
            ),
            'EventDate': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'format': '%d.%m.%Y',
                    'type': 'date',
                },
            ),
            'EventComment': forms.TextInput(
                attrs={
                    'type': 'text',
                    'class': 'form-control',
                }
            ),
            'Contact': forms.TextInput(
                attrs={
                    'type': 'text',
                    'class': 'form-control',
                }
            ),
        }


######################################################################################################################


class FormEmployer(forms.Form):
    title = forms.CharField(
        label='Наименование работодателя',
        widget=forms.TextInput(
            attrs={
                'type': 'text',
                'class': 'form-control',
            }
        ),
        required=True,
    )
    legal_address = forms.CharField(
        label='Юридический адрес',
        widget=forms.TextInput(
            attrs={
                'type': 'text',
                'class': 'form-control',
            }
        ),
        required=True,
    )
    actual_address = forms.CharField(
        label='Фактический адрес',
        widget=forms.TextInput(
            attrs={
                'type': 'text',
                'class': 'form-control',
            }
        ),
        required=True,
    )
    inn = forms.CharField(
        label='ИНН',
        widget=forms.TextInput(
            attrs={
                'type': 'text',
                'class': 'form-control',
            }
        ),
        required=True,
    )
    ogrn = forms.CharField(
        label='ОГРН',
        widget=forms.TextInput(
            attrs={
                'type': 'text',
                'class': 'form-control',
            }
        ),
        required=False,
    )
    vacancy_date = forms.DateField(
        label='Дата размещения вакансии',
        widget=forms.widgets.DateInput(
            attrs={
                'type': 'date',
            }
        ),
        input_formats=('%d.%m.%Y', '%d/%m/%Y', '%d-%m-%Y', ),
        initial=date.today().__format__('%d.%m.%Y'),
        required=False,
    )
    vacancy_comment = forms.CharField(
        label='Комментарий даты размещения вакансии',
        widget=forms.TextInput(
            attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Оставить комментарий',
            }
        ),
        required=False,
    )
    event_date = forms.DateField(
        label='Дата последнего взаимодействия работодателя и центра занятости',
        widget=forms.widgets.DateInput(
            attrs={
                'type': 'date',
            }
        ),
        input_formats=('%d.%m.%Y', '%d/%m/%Y', '%d-%m-%Y', ),
        initial=date.today().__format__('%d.%m.%Y'),
        required=False,
    )
    event_comment = forms.CharField(
        label='Комментарий даты взаимодействия',
        widget=forms.TextInput(
            attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Оставить комментарий',
            }
        ),
        required=False,
    )
    send_date = forms.DateField(
        label='Дата направления информации на проверку в отделы Министерства труда и социального развития Омской '
              'области',
        widget=forms.widgets.DateInput(
            attrs={
                'type': 'date',
            }
        ),
        input_formats=('%d.%m.%Y', '%d/%m/%Y', '%d-%m-%Y', ),
        initial=date.today().__format__('%d.%m.%Y'),
        required=False,
    )
    contact = forms.CharField(
        label='Контакт основной',
        widget=forms.TextInput(
            attrs={
                'type': 'text',
                'class': 'form-control',
            }
        ),
        required=False,
    )


######################################################################################################################


class FormNotify(forms.ModelForm):
    class Meta:
        model = Notify
        fields = [
            'Method',
            'NotifyDate',
            'Comment',
            'Attache',
        ]
        labels = {
            'Method': 'Способ направления информирования',
            'NotifyDate': 'Дата направления информирования',
            'Comment': 'Комментарий',
            'Attache': 'Прикрепленный файл',
        }
        widgets = {
            'Method': forms.Select(
                attrs={
                    'class': 'form-control',
                }
            ),
            'NotifyDate': forms.DateInput(
                attrs={
                    'type': 'date',
                }
            ),
            'Comment': forms.TextInput(
                attrs={
                    'type': 'text',
                    'class': 'form-control',
                    'placeholder': 'Оставить комментарий',
                }
            ),
            'Attache': forms.FileInput(),
        }


######################################################################################################################


class FormInformation(forms.ModelForm):
    class Meta:
        model = Info
        fields = [
            'Name',
            'Comment',
            'Attache',
        ]
        labels = {
            'Name': 'Наименование непредставленной информации',
            'Comment': 'Комментарий',
            'Attache': 'Прикрепленный файл',
        }
        widgets = {
            'Name': forms.Select(
                attrs={
                    'class': 'form-control',
                }
            ),
            'Comment': forms.TextInput(
                attrs={
                    'type': 'text',
                    'class': 'form-control',
                    'placeholder': 'Оставить комментарий',
                }
            ),
            'Attache': forms.FileInput(),
        }


######################################################################################################################


class FormNotice(forms.Form):
    notice = forms.FileField(
        label='',
        widget=forms.FileInput(
            attrs={
                'class': 'form-control-input',
            }
        ),
        required=True,
    )


######################################################################################################################


class FormProtocol(forms.Form):
    employer = forms.ChoiceField(
        choices=EMPLOYER_CHOICES,
        label='',
        initial=0,
        widget=forms.Select(
            attrs={
                'class': 'custom-select mb-0 mr-sm-2 mb-sm-0',
                'id': 'inlineFormCustomSelect',
            }
        ),
        required=True
    )
    protocol = forms.ChoiceField(
        choices=PROTOCOL_CHOICES,
        label='',
        initial=0,
        widget=forms.Select(
            attrs={
                'class': 'custom-select mb-0 mr-sm-2 mb-sm-0',
                'id': 'inlineFormCustomSelect',
            }
        ),
        required=True
    )
    notice = forms.FileField(
        label='',
        widget=forms.FileInput(
            attrs={
                'class': 'form-control-input',
            }
        ),
        required=False,
    )


######################################################################################################################


class FormFilterCzn(forms.Form):
    list_czn = [(0, 'Все ЦЗН')]
    list_czn.extend(list(UserProfile.objects.filter(super_role='czn').values_list('id', 'user__first_name')))

    czn = forms.ChoiceField(
        choices=list_czn,
        label='',
        initial=0,
        widget=forms.Select(
            attrs={
                'class': 'custom-select',
            }
        ),
        required=True
    )


######################################################################################################################


class FormResponse(forms.Form):
    list_response = list(UserProfile.objects.filter(super_role='control').values_list('id', 'user__last_name'))

    response = forms.ChoiceField(
        choices=list_response,
        label='',
        widget=forms.Select(
            attrs={
                'class': 'custom-select',
            }
        ),
        required=True
    )


######################################################################################################################


class FormFilterStatus(forms.Form):
    # status = forms.ChoiceField(
    #     label='',
    #     widget=forms.Select(
    #         attrs={
    #             'class': 'custom-select',
    #         }
    #     ),
    #     choices=list(
    #         map(
    #             lambda x: [x['id'], x['title']],
    #             list(Status.objects.values('id', 'title').filter(is_filtered=True))
    #         )
    #     ),
    #     required=True,
    # )


    # status = forms.ChoiceField(
    #     choices=STATUS_CHOICES,
    #     label='',
    #     initial=20,
    #     widget=forms.Select(
    #         attrs={
    #             'class': 'custom-select',
    #         }
    #     ),
    #     required=True
    # )
    list_status = [(0, 'Все статусы')]
    list_status.extend(list(Status.objects.filter(is_filtered=True).values_list('id', 'title')))
    # list_status.extend(
    #     list(
    #         map(
    #             lambda x: (x['id'], x['title']),
    #             list(Status.objects.values_list('id', 'title').filter(is_filtered=True))
    #         )
    #     )
    # )
    status = forms.ChoiceField(
        choices=list_status,
        label='',
        initial=0,
        widget=forms.Select(
            attrs={
                'class': 'custom-select',
            }
        ),
        required=True,
    )


######################################################################################################################


class FormMonth(forms.Form):
    MONTH_CHOICES = []
    locale.setlocale(locale.LC_ALL, settings.LOCALE)
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
        widget=forms.Select(
            attrs={
                'class': 'custom-select',
            }
        ),
        required=True
    )


######################################################################################################################


class FormReportDates(forms.Form):
    start_date = forms.DateField(
        label='Начальная дата',
        widget=forms.widgets.DateInput(
            attrs={
                'type': 'date',
            }
        ),
        input_formats=('%d.%m.%Y', '%d/%m/%Y', '%d-%m-%Y', ),
        initial=date.today().__format__('2018-08-01'),
        required=True,
    )
    end_date = forms.DateField(
        label='Конечная дата',
        widget=forms.widgets.DateInput(
            attrs={
                'type': 'date',
            }
        ),
        input_formats=('%d.%m.%Y', '%d/%m/%Y', '%d-%m-%Y', ),
        initial=date.today().__format__('%Y-%m-%d'),
        required=True,
    )


######################################################################################################################
