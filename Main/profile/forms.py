# -*- coding: utf-8 -*-

from django import forms
from Main.models import User, UserProfile

######################################################################################################################


class FormProfile(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name',
            'username',
            'email',
        ]
        widgets = {
            'first_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Введите имя пользователя',
                }
            ),
            'username': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Введите логин пользователя',
                }
            ),
            'email': forms.TextInput(
                attrs={
                    'type': 'email',
                    'class': 'form-control',
                    'autocomplete': 'off',
                    'placeholder': 'Введите электронный адрес',
                }
            ),
        }
        labels = {
            'first_name': 'Имя пользователя',
            'username': 'Логин пользователя',
            'email': 'Адрес электронной почты',
        }
        help_texts = {
            'username': 'Обязательное поле. Только английские буквы.',
        }


######################################################################################################################


class FormDepartment(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'department',
        ]
        widgets = {
            'department': forms.Select(
                attrs={
                    'class': 'custom-select',
                }
            ),
        }
        labels = {
            'department': 'Выберите организацию или отдел:',
        }


######################################################################################################################


class FormPassword(forms.Form):
    password = forms.CharField(
        label='Новый пароль',
        widget=forms.TextInput(
            attrs={
                'type': 'password',
                'class': 'form-control',
                'autocomplete': 'off',
            }
        ),
        help_text='Пароль не должен совпадать с логином и состоять только из цифр. '
                  'Пароль должен содержать как минимум 8 символов.',
        required=True,
    )
    password2 = forms.CharField(
        label='Подтверждение нового пароля',
        widget=forms.TextInput(
            attrs={
                'type': 'password',
                'class': 'form-control',
                'autocomplete': 'off',
            }
        ),
        help_text='Для подтверждения введите, пожалуйста, пароль ещё раз.',
        required=True,
    )


######################################################################################################################
