from django.db import models
from django.contrib.auth.models import User
from .choices import ROLE_CHOICES, STATUS_CHOICES, INFO_CHOICES, METHOD_CHOICES, RESULT_CHOICES
from django.utils.html import format_html

######################################################################################################################

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, )
    role = models.SmallIntegerField('Роль', choices=ROLE_CHOICES, default=0, null=False, blank=False, )

    def __str__(self):
        return '{0}'.format(self.user.get_full_name())

    class Meta:
        ordering = 'user',
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'
        managed = True

######################################################################################################################

class Employer(models.Model):
    Owner = models.ForeignKey(UserProfile, verbose_name='Автор карточки', null=True, related_name='Owner', on_delete=models.SET_NULL, )
    Title = models.CharField('Наименование работодателя', max_length=1024, default='', )
    Number = models.CharField('Учётный номер', max_length=128, default='', )
    INN = models.CharField('ИНН', max_length=20, default='', )
    OGRN = models.CharField('ОГРН', max_length=20, default='', )
    JurAddress = models.CharField('Адрес юридический', max_length=256, default='', )
    FactAddress = models.CharField('Адрес фактический', max_length=256, default='', )
    VacancyDate = models.DateField('Дата размещения вакансии', null=True, )
    VacancyComment = models.CharField('Комментарий даты размещения вакансии', max_length=512, default='', )
    EventDate = models.DateField('Дата взаимодействия', null=True, )
    EventComment = models.CharField('Комментарий даты взаимодействия', max_length=512, default='', )
    Contact = models.CharField('Контакт основной', max_length=512, default='', )
    Status = models.SmallIntegerField('Статус', choices=STATUS_CHOICES, default=0, )
    Result = models.SmallIntegerField('Результат', choices=RESULT_CHOICES, null=True, )
    SendDate = models.DateField('Дата направления в трудоустройство', null=True, )
    RegKatharsis = models.BooleanField('Зарегистрирован в ПК Катарсис', default=False, )
    Archive = models.BooleanField('Архивная карточка', default=False, )
    Respons = models.ForeignKey(UserProfile, verbose_name='Ответственное лицо', null=True, default=None, related_name='Respons', on_delete=models.SET_NULL, )
    CreateDate = models.DateTimeField('Дата создания', auto_now_add=True, null=True, )

    def __str__(self):
        return '{0}'.format(self.Title)

    def link(self):
        return format_html('<a href="/emp/{0}/" class="btn btn-info btn-sm" role="button">Перейти</a>', self.id)

    class Meta:
        ordering = 'Title',
        verbose_name = 'Работодатель'
        verbose_name_plural = 'Работодатели'
        managed = True

######################################################################################################################

class Info(models.Model):
    EmpInfoID = models.ForeignKey(Employer, verbose_name='Карточка предприятия', null=True, related_name='EmpInfoID', on_delete=models.CASCADE, )
    Name = models.SmallIntegerField('Наименование информации', choices=INFO_CHOICES, default=1, )
    Comment = models.CharField('Комментарий', max_length=1024, default='', )
    Attache = models.FileField('Прикрепленный файл', upload_to='attache/%Y/%m/%d', null=True, )
    CreateDate = models.DateTimeField('Дата создания', auto_now_add=True, null=True, )

    def __str__(self):
        return '{0} - {1}'.format(self.EmpInfoID, self.Name)

    class Meta:
        ordering = 'CreateDate',
        verbose_name = 'Информация'
        verbose_name_plural = 'Информация'
        managed = True


######################################################################################################################

class TempEmployer(models.Model):
    Number = models.CharField('Учётный номер', max_length=128, default='', )
    Title = models.CharField('Наименование полное', max_length=1024, default='', )
    INN = models.CharField('ИНН', max_length=20, default='', )
    OGRN = models.CharField('ОГРН', max_length=20, default='', )
    JurAddress = models.CharField('Адрес юридический', max_length=256, default='', )
    FactAddress = models.CharField('Адрес фактический', max_length=256, default='', )
    Contact = models.CharField('Контакт основной', max_length=512, default='', )
    EventDate = models.DateField('Дата взаимодействия', null=True, )

    def __str__(self):
        return '{0}'.format(self.Title)

    class Meta:
        ordering = 'Title',
        verbose_name = 'Работодатель из Катарсиса'
        verbose_name_plural = 'Работодатели из Катарсиса'
        managed = True

######################################################################################################################

class Event(models.Model):
    EmpEventID = models.ForeignKey(Employer, verbose_name='Карточка предприятия', null=True, related_name='EmpEventID', on_delete=models.CASCADE, )
    Owner = models.ForeignKey(UserProfile, verbose_name='Создатель информации', null=True, related_name='OwnerInfo', on_delete=models.CASCADE, )
    Comment = models.CharField('Комментарий', max_length=1024, default='', )
    Attache = models.FileField('Прикрепленный файл', upload_to='attache/%Y/%m/%d', null=True, )
    CreateDate = models.DateTimeField('Дата создания', auto_now_add=True, null=True, )

    def __str__(self):
        return '{0}'.format(self.Comment)

    class Meta:
        ordering = '-CreateDate',
        verbose_name = 'Событие'
        verbose_name_plural = 'События'
        managed = True

######################################################################################################################

class ConfigWatch(models.Model):
    UploadDate = models.DateField('Дата загрузки работодателей из Катарсиса', null=True, )

    def __str__(self):
        return '{0}'.format(self.UploadDate)

    class Meta:
        ordering = 'UploadDate',
        verbose_name = 'Дата загрузки'
        verbose_name_plural = 'Даты загрузки'
        managed = True

######################################################################################################################

class Message(models.Model):
    EmpMessageID = models.ForeignKey(Employer, verbose_name='Карточка предприятия', null=True, related_name='EmpMessageID', on_delete=models.CASCADE, )
    Recipient = models.ForeignKey(UserProfile, verbose_name='Получатель', null=True, related_name='Recipient', on_delete=models.CASCADE, )
    Sender = models.ForeignKey(UserProfile, verbose_name='Отправитель', null=True, related_name='Sender', on_delete=models.CASCADE, )
    Text = models.CharField('Текст сообщения', max_length=1024, default='', )
    Reading = models.BooleanField('Прочтено', default=False, )
    CreateDate = models.DateTimeField('Дата сообщения', auto_now_add=True, null=True, )

    def __str__(self):
        return '{0} - {1}'.format(self.Recipient, self.Reading)

    class Meta:
        ordering = 'Reading', '-CreateDate',
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        managed = True


######################################################################################################################

class Notify(models.Model):
    EmpNotifyID = models.ForeignKey(Employer, verbose_name='Карточка предприятия', null=True, related_name='EmpNotifyID', on_delete=models.CASCADE, )
    Owner = models.ForeignKey(UserProfile, verbose_name='Создатель уведомления', null=True, related_name='OwnerNotify', on_delete=models.CASCADE, )
    Method = models.SmallIntegerField('Способ доставки', choices=METHOD_CHOICES, default=1, null=False, blank=False, )
    NotifyDate = models.DateField('Дата уведомления', null=True, )
    Comment = models.CharField('Комментарий', max_length=1024, default='', )
    Attache = models.FileField('Прикрепленный файл', upload_to='attache/%Y/%m/%d', null=True, )
    CreateDate = models.DateTimeField('Дата создания', auto_now_add=True, null=True, )

    def __str__(self):
        return '{0} - {1}'.format(self.EmpNotifyID, self.Method)

    class Meta:
        ordering = 'NotifyDate',
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        managed = True
