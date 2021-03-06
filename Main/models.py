from django.db import models
from django.contrib.auth.models import User
from .choices import ROLE_CHOICES, STATUS_CHOICES, INFO_CHOICES, METHOD_CHOICES, RESULT_CHOICES, ROLES_CHOICES, \
    FULL_MENU
from django.utils.html import format_html

######################################################################################################################


class Status(models.Model):
    id = models.AutoField(
        primary_key=True,
    )
    title = models.CharField(
        verbose_name='Название статуса',
        max_length=64,
        default='',
    )
    order = models.SmallIntegerField(
        verbose_name='Порядок в списке статусов',
        default=0,
    )
    is_filtered = models.BooleanField(
        verbose_name='Используется в фильтрах',
        default=False,
    )
    status = models.SmallIntegerField(
        verbose_name='Старый статус',
        choices=STATUS_CHOICES,
        blank=True,
    )

    def __str__(self):
        return '{0}'.format(self.title)

    class Meta:
        ordering = 'order', 'title',
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы'
        managed = True


######################################################################################################################


class UserProfile(models.Model):
    id = models.AutoField(
        primary_key=True,
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )
    role = models.SmallIntegerField(
        verbose_name='Роль',
        choices=ROLE_CHOICES,
        default=0,
        null=False,
        blank=False,
    )
    super_role = models.CharField(
        verbose_name='Роль new new',
        max_length=16,
        choices=ROLES_CHOICES,
        null=True,
        blank=True,
        default=None,
    )
    blocked = models.BooleanField(
        verbose_name='Учетная запись заблокирована',
        default=False,
    )

    def block(self):
        """
        Отмечает пользователя как заблокированного
        :return:
        """
        self.blocked = True
        self.save()

    def unblock(self):
        """
        Отмечает пользователя как действующего
        :return:
        """
        self.blocked = False
        self.save()

    def is_allowed(self, list_permission):
        """
        Возвращает значение, есть или нет у пользователя права из списка
        :param list_permission:
        :return:
        """
        for permission in list_permission:
            if self.super_role == permission:
                return True
        return False

    def get_menu(self):
        """
        Формирует доступные элементы меню в зависимости от прав
        :return:
        """
        menu = []
        for item in FULL_MENU:
            if self.is_allowed(list_permission=item[0]):
                menu.append(item)
        return menu

    def __str__(self):
        return '{0}'.format(self.user.get_full_name())

    class Meta:
        ordering = 'blocked', 'user',
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'
        managed = True


######################################################################################################################


class Employer(models.Model):
    id = models.AutoField(
        primary_key=True,
    )
    Owner = models.ForeignKey(
        UserProfile,
        verbose_name='Автор карточки',
        null=True,
        related_name='Owner',
        on_delete=models.SET_NULL,
    )
    Title = models.CharField(
        verbose_name='Наименование работодателя',
        max_length=1024,
        default='',
    )
    Number = models.CharField(
        verbose_name='Учётный номер',
        max_length=128,
        default='',
    )
    INN = models.CharField(
        verbose_name='ИНН',
        max_length=20,
        default='',
    )
    OGRN = models.CharField(
        verbose_name='ОГРН',
        max_length=20,
        default='',
        blank=True,
        null=True,
    )
    JurAddress = models.CharField(
        verbose_name='Адрес юридический',
        max_length=256,
        default='',
    )
    FactAddress = models.CharField(
        verbose_name='Адрес фактический',
        max_length=256,
        default='',
    )
    VacancyDate = models.DateField(
        verbose_name='Дата размещения вакансии',
        null=True,
        blank=True,
    )
    VacancyComment = models.CharField(
        verbose_name='Комментарий даты размещения вакансии',
        max_length=512,
        default='',
        blank=True,
    )
    EventDate = models.DateField(
        verbose_name='Дата взаимодействия',
        null=True,
        blank=True,
    )
    EventComment = models.CharField(
        verbose_name='Комментарий даты взаимодействия',
        max_length=512,
        default='',
        blank=True,
    )
    Contact = models.CharField(
        verbose_name='Контакт основной',
        max_length=512,
        default='',
    )
    Status = models.SmallIntegerField(
        verbose_name='Статус',
        choices=STATUS_CHOICES,
        default=0,
    )
    Result = models.SmallIntegerField(
        verbose_name='Результат',
        choices=RESULT_CHOICES,
        null=True,
    )
    SendDate = models.DateField(
        verbose_name='Дата направления в трудоустройство',
        null=True,
    )
    RegKatharsis = models.BooleanField(
        verbose_name='Зарегистрирован в ПК Катарсис',
        default=False,
    )
    Archive = models.BooleanField(
        verbose_name='Архивная карточка',
        default=False,
    )
    Response = models.ForeignKey(
        UserProfile,
        verbose_name='Ответственное лицо',
        null=True,
        default=None,
        related_name='Response',
        on_delete=models.SET_NULL,
    )
    CreateDate = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True,
        null=True,
    )

    def __str__(self):
        return '{0}'.format(self.Title)

    def link(self):
        return format_html('<a href="/emp/{0}/" class="btn btn-info btn-sm" role="button">Перейти</a>', self.id)

    class Meta:
        ordering = 'Status', 'Title',
        verbose_name = 'Карточка работодателя-нарушителя'
        verbose_name_plural = 'Карточки работодателей-нарушителей'
        managed = True


######################################################################################################################


class StatusEmployer(models.Model):
    id = models.AutoField(
        primary_key=True,
    )
    status = models.ForeignKey(
        Status,
        verbose_name='Статус карточки нарушителя',
        null=True,
        related_name='StatusEmployer',
        on_delete=models.SET_NULL,
    )
    employer = models.ForeignKey(
        Employer,
        verbose_name='Карточка нарушителя',
        null=True,
        related_name='EmployerStatus',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return '{0} - {1}'.format(self.employer, self.status)

    class Meta:
        ordering = 'employer',
        verbose_name = 'Статус нарушителя'
        verbose_name_plural = 'Статусы нарушителей'
        managed = True


######################################################################################################################


class StatusRoute(models.Model):
    id = models.AutoField(
        primary_key=True,
    )
    current_status = models.ForeignKey(
        Status,
        verbose_name='Текущий статус',
        null=True,
        related_name='CurrentStatus',
        on_delete=models.SET_NULL,
    )
    next_status = models.ForeignKey(
        Status,
        verbose_name='Следующий статус',
        null=True,
        related_name='NextStatus',
        on_delete=models.SET_NULL,
    )
    turn = models.SmallIntegerField(
        verbose_name='Номер выбора',
        default=0,
    )
    level = models.SmallIntegerField(
        verbose_name='Уровень выбора',
        default=0,
    )

    def __str__(self):
        return '[{0}][{1}] {2} - {3}'.format(self.level, self.turn, self.current_status, self.next_status)

    class Meta:
        ordering = 'level', 'turn',
        verbose_name = 'Маршрут статуса'
        verbose_name_plural = 'Маршруты статусов'
        managed = True


######################################################################################################################


class Info(models.Model):
    id = models.AutoField(
        primary_key=True,
    )
    EmpInfoID = models.ForeignKey(
        Employer,
        verbose_name='Карточка предприятия',
        null=True,
        related_name='EmpInfoID',
        on_delete=models.CASCADE,
    )
    Name = models.SmallIntegerField(
        verbose_name='Наименование информации',
        choices=INFO_CHOICES,
        default=1,
    )
    Comment = models.CharField(
        verbose_name='Комментарий',
        max_length=1024,
        default='',
        blank=True,
    )
    Attache = models.FileField(
        verbose_name='Прикрепленный файл',
        upload_to='attache/%Y/%m/%d',
        null=True,
        blank=True,
    )
    CreateDate = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True,
        null=True,
    )

    def __str__(self):
        return '{0} - {1}'.format(self.EmpInfoID, self.Name)

    class Meta:
        ordering = 'CreateDate',
        verbose_name = 'Информация'
        verbose_name_plural = 'Информация'
        managed = True


######################################################################################################################


class TempEmployer(models.Model):
    id = models.AutoField(
        primary_key=True,
    )
    Number = models.CharField(
        verbose_name='Учётный номер',
        max_length=128,
        default='',
    )
    Title = models.CharField(
        verbose_name='Наименование полное',
        max_length=1024,
        default='',
    )
    INN = models.CharField(
        verbose_name='ИНН',
        max_length=20,
        default='',
    )
    OGRN = models.CharField(
        verbose_name='ОГРН',
        max_length=20,
        default='',
    )
    JurAddress = models.CharField(
        verbose_name='Адрес юридический',
        max_length=256,
        default='',
    )
    FactAddress = models.CharField(
        verbose_name='Адрес фактический',
        max_length=256,
        default='',
    )
    Contact = models.CharField(
        verbose_name='Контакт основной',
        max_length=512,
        default='',
    )
    EventDate = models.DateField(
        verbose_name='Дата взаимодействия',
        null=True,
        blank=True,
    )

    def __str__(self):
        return '{0}'.format(self.Title)

    class Meta:
        ordering = 'Title',
        verbose_name = 'Работодатель из Катарсиса'
        verbose_name_plural = 'Работодатели из Катарсиса'
        managed = True


######################################################################################################################


class Event(models.Model):
    id = models.AutoField(
        primary_key=True,
    )
    EmpEventID = models.ForeignKey(
        Employer,
        verbose_name='Карточка предприятия',
        null=True,
        related_name='EmpEventID',
        on_delete=models.CASCADE,
    )
    Owner = models.ForeignKey(
        UserProfile,
        verbose_name='Создатель информации',
        null=True,
        related_name='OwnerInfo',
        on_delete=models.CASCADE,
    )
    Comment = models.CharField(
        verbose_name='Комментарий',
        max_length=1024,
        default='',
    )
    Attache = models.FileField(
        verbose_name='Прикрепленный файл',
        upload_to='attache/%Y/%m/%d',
        null=True,
    )
    CreateDate = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True,
        null=True,
    )

    def __str__(self):
        return '{0}'.format(self.Comment)

    class Meta:
        ordering = '-CreateDate',
        verbose_name = 'Событие'
        verbose_name_plural = 'События'
        managed = True


######################################################################################################################


class UpdateEmployer(models.Model):
    id = models.AutoField(
        primary_key=True,
    )
    upload_date = models.DateField(
        verbose_name='Дата загрузки работодателей из Катарсиса',
        null=True,
    )
    count_employer = models.CharField(
        verbose_name='Количество загруженных организаций из Катарсиса',
        max_length=16,
        default='',
    )
    time_spent = models.CharField(
        verbose_name='Длительность загрузки работодателей из Катарсиса в секундах',
        max_length=8,
        default='',
    )

    def __str__(self):
        return '{0}'.format(self.upload_date)

    class Meta:
        ordering = '-upload_date',
        verbose_name = 'Дата загрузки'
        verbose_name_plural = 'Даты загрузки'
        managed = True


######################################################################################################################


class Message(models.Model):
    id = models.AutoField(
        primary_key=True,
    )
    EmpMessageID = models.ForeignKey(
        Employer,
        verbose_name='Карточка предприятия',
        null=True,
        related_name='EmpMessageID',
        on_delete=models.CASCADE,
    )
    Recipient = models.ForeignKey(
        UserProfile,
        verbose_name='Получатель',
        null=True,
        related_name='Recipient',
        on_delete=models.CASCADE,
    )
    Sender = models.ForeignKey(
        UserProfile,
        verbose_name='Отправитель',
        null=True,
        related_name='Sender',
        on_delete=models.CASCADE,
    )
    Text = models.CharField(
        verbose_name='Текст сообщения',
        max_length=1024,
        default='',
    )
    Reading = models.BooleanField(
        verbose_name='Прочтено',
        default=False,
    )
    CreateDate = models.DateTimeField(
        verbose_name='Дата сообщения',
        auto_now_add=True,
        null=True,
    )

    def __str__(self):
        return '{0} - {1}'.format(self.Recipient, self.Reading)

    class Meta:
        ordering = 'Reading', '-CreateDate',
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        managed = True


######################################################################################################################


class Notify(models.Model):
    id = models.AutoField(
        primary_key=True,
    )
    EmpNotifyID = models.ForeignKey(
        Employer,
        verbose_name='Карточка предприятия',
        null=True,
        related_name='EmpNotifyID',
        on_delete=models.CASCADE,
    )
    Owner = models.ForeignKey(
        UserProfile,
        verbose_name='Создатель уведомления',
        null=True,
        related_name='OwnerNotify',
        on_delete=models.CASCADE,
    )
    Method = models.SmallIntegerField(
        verbose_name='Способ доставки',
        choices=METHOD_CHOICES,
        default=1,
        null=False,
        blank=False,
    )
    NotifyDate = models.DateField(
        verbose_name='Дата уведомления',
        null=True,
    )
    Comment = models.CharField(
        verbose_name='Комментарий',
        max_length=1024,
        default='',
        blank=True,
    )
    Attache = models.FileField(
        verbose_name='Прикрепленный файл',
        upload_to='attache/%Y/%m/%d',
        null=True,
        blank=True,
    )
    CreateDate = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True,
        null=True,
    )

    def __str__(self):
        return '{0} - {1}'.format(self.EmpNotifyID, self.Method)

    class Meta:
        ordering = 'NotifyDate',
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        managed = True


######################################################################################################################


class Configure(models.Model):
    id = models.AutoField(
        primary_key=True,
    )
    title = models.CharField(
        verbose_name='Название настройки',
        max_length=128,
        default='',
        blank=True,
    )
    description = models.CharField(
        verbose_name='Описание настройки',
        max_length=1024,
        default='',
        blank=True,
    )
    url = models.CharField(
        verbose_name='Ссылка настройки',
        max_length=128,
        default='',
        blank=True,
    )

    def __str__(self):
        return '{0}'.format(self.title)

    class Meta:
        ordering = 'title',
        verbose_name = 'Настройка'
        verbose_name_plural = 'Настройки'
        managed = True


######################################################################################################################


class Widget(models.Model):
    id = models.AutoField(
        primary_key=True,
    )
    title = models.CharField(
        verbose_name='Название виджета',
        max_length=64,
        default='',
    )
    order = models.SmallIntegerField(
        verbose_name='Порядок в списке виджетов',
        default=0,
    )
    color_primary = models.CharField(
        verbose_name='Основной цвет',
        max_length=124,
        default='',
    )
    color_secondary = models.CharField(
        verbose_name='Альтернативный цвет',
        max_length=124,
        default='',
    )
    url = models.CharField(
        verbose_name='Ссылка виджета',
        max_length=128,
        default='',
        blank=True,
    )

    def __str__(self):
        return '{0}'.format(self.title)

    class Meta:
        ordering = 'order', 'title',
        verbose_name = 'Виджет'
        verbose_name_plural = 'Виджеты'
        managed = True


######################################################################################################################


class WidgetFilter(models.Model):
    id = models.AutoField(
        primary_key=True,
    )
    widget = models.ForeignKey(
        Widget,
        verbose_name='Виджет фильтра',
        null=True,
        related_name='WidgetFilter',
        on_delete=models.CASCADE,
    )
    status = models.ForeignKey(
        Status,
        verbose_name='Статус фильтра',
        null=True,
        related_name='StatusWidget',
        on_delete=models.CASCADE,
    )
    checked = models.BooleanField(
        verbose_name='Статус включен в фильтр',
        default=False,
    )

    def __str__(self):
        return '{0} - {1}'.format(self.widget, self.status)

    class Meta:
        ordering = 'widget', 'status',
        verbose_name = 'Фильтр статуса'
        verbose_name_plural = 'Фильтры стасусов'
        managed = True


######################################################################################################################
