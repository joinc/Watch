# -*- coding: utf-8 -*-

######################################################################################################################


def check_password(username, password, password2):
    """
    Проверка выполнения требований к паролю
    :param username:
    :param password:
    :param password2:
    :return:
    """
    message_list = []
    if password != password2:
        message_list.append('Пароли не совпадают.')
    if len(password) < 8:
        message_list.append('Длина пароля менее 8 символов.')
    if password.isdigit():
        message_list.append('Пароль состоит только из цифр.')
    if password == username:
        message_list.append('Пароль совпадает с логином.')
    return message_list


######################################################################################################################
