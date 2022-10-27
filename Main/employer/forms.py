# -*- coding: utf-8 -*-

from django import forms
from Main.models import TypeStatus, Department

######################################################################################################################


class FormSearchEmployer(forms.Form):
    list_czn = [('', 'Выберите центр занятости')]
    list_czn.extend(list(Department.objects.filter(role='czn').values_list('id', 'title')))
    list_status = [('', 'Выбарите статус')]
    list_status.extend(list(TypeStatus.objects.filter(is_filtered=True).values_list('id', 'title')))

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
    czn = forms.ChoiceField(
        choices=list_czn,
        label='',
        initial=0,
        widget=forms.Select(
            attrs={
                'class': 'custom-select',
            }
        ),
        required=False,
    )
    status = forms.ChoiceField(
        choices=list_status,
        label='',
        initial=0,
        widget=forms.Select(
            attrs={
                'class': 'custom-select',
            }
        ),
        required=False,
    )


######################################################################################################################


class FormFilterStatus(forms.Form):
    list_status = [(0, 'Все статусы')]
    list_status.extend(list(TypeStatus.objects.filter(is_filtered=True).values_list('id', 'title')))
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
