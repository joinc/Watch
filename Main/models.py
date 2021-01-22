from django.db import models
from django.contrib.auth.models import User
from .choices import ROLE_CHOICES, STATUS_CHOICES, INFO_CHOICES, METHOD_CHOICES, RESULT_CHOICES
from django.utils.html import format_html

######################################################################################################################


class UserProfile(models.Model):
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
    blocked = models.BooleanField(
        verbose_name='Учетная запись заблокирована',
        default=False,
    )

    def block(self):
        self.blocked = True
        self.save()

    def unblock(self):
        self.blocked = False
        self.save()

    def __str__(self):
        return '{0}'.format(self.user.get_full_name())

    class Meta:
        ordering = 'user',
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'
        managed = True


######################################################################################################################


class Employer(models.Model):
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
    )
    VacancyComment = models.CharField(
        verbose_name='Комментарий даты размещения вакансии',
        max_length=512,
        default='',
    )
    EventDate = models.DateField(
        verbose_name='Дата взаимодействия',
        null=True,
    )
    EventComment = models.CharField(
        verbose_name='Комментарий даты взаимодействия',
        max_length=512,
        default='',
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
        verbose_name = 'Работодатель'
        verbose_name_plural = 'Работодатели'
        managed = True


######################################################################################################################


class Info(models.Model):
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
        return '{0} - {1}'.format(self.EmpInfoID, self.Name)

    class Meta:
        ordering = 'CreateDate',
        verbose_name = 'Информация'
        verbose_name_plural = 'Информация'
        managed = True


######################################################################################################################


class TempEmployer(models.Model):
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


class ConfigWatch(models.Model):
    UploadDate = models.DateField(
        verbose_name='Дата загрузки работодателей из Катарсиса',
        null=True,
    )

    def __str__(self):
        return '{0}'.format(self.UploadDate)

    class Meta:
        ordering = 'UploadDate',
        verbose_name = 'Дата загрузки'
        verbose_name_plural = 'Даты загрузки'
        managed = True


######################################################################################################################


class Message(models.Model):
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
        return '{0} - {1}'.format(self.EmpNotifyID, self.Method)

    class Meta:
        ordering = 'NotifyDate',
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        managed = True


######################################################################################################################
