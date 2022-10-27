from django.db import models
from django.contrib.auth.models import User
from .choices import ROLE_CHOICES, STATUS_CHOICES, INFO_CHOICES, METHOD_CHOICES, RESULT_CHOICES, ROLES_CHOICES, \
    FULL_MENU

######################################################################################################################


class Department(models.Model):
    id = models.AutoField(
        primary_key=True,
    )
    title = models.CharField(
        verbose_name='Отдел',
        max_length=124,
        default='',
    )
    role = models.CharField(
        verbose_name='Роль',
        max_length=16,
        choices=ROLES_CHOICES,
        null=True,
        blank=True,
        default=None,
    )
    is_czn = models.BooleanField(
        verbose_name='Признак того, что организация является Центром занятости',
        default=False,
    )
    is_control = models.BooleanField(
        verbose_name='Признак того, что отделя является Отделом надзора и контроля',
        default=False,
    )
    create_date = models.DateTimeField(
        verbose_name='Дата создания отдела',
        auto_now_add=True,
        null=True,
    )

    def __str__(self):
        return f'{self.title}'

    class Meta:
        ordering = 'title',
        verbose_name = 'Отдел'
        verbose_name_plural = 'Отделы'
        managed = True


######################################################################################################################


class TypeStatus(models.Model):
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
        verbose_name='Статус старый',
        choices=STATUS_CHOICES,
        blank=True,
        null=True,
    )
    prev_status = models.ForeignKey(
        'self',
        verbose_name='Статус для возврата',
        null=True,
        blank=True,
        default=None,
        related_name='StatusPrev',
        on_delete=models.SET_NULL,
    )
    next_status = models.ForeignKey(
        'self',
        verbose_name='Следующий статус',
        null=True,
        blank=True,
        default=None,
        related_name='StatusNext',
        on_delete=models.SET_NULL,
    )
    role_access = models.CharField(
        verbose_name='Организация или отдел которые имеют доступ к выполнению данного шага',
        max_length=16,
        choices=ROLES_CHOICES,
        null=True,
        blank=True,
        default=None,
    )
    template_path = models.CharField(
        verbose_name='Путь до шаблона с формой шага карточки',
        max_length=124,
        blank=True,
        default='',
    )
    color = models.CharField(
        verbose_name='Цвет заголовка карточки',
        max_length=32,
        default='',
    )

    def __str__(self):
        return f'{self.title}'

    class Meta:
        ordering = 'order', 'title',
        verbose_name = 'Вид статуса'
        verbose_name_plural = 'Виды статусов'
        managed = True


######################################################################################################################


class TypeViolations(models.Model):
    id = models.AutoField(
        primary_key=True,
    )
    title = models.CharField(
        verbose_name='Название правонарушения',
        max_length=625,
        default='',
    )
    order = models.SmallIntegerField(
        verbose_name='Порядок в списке правонарушений',
        default=0,
    )
    next_status = models.ForeignKey(
        TypeStatus,
        verbose_name='Статус карточки при отправке на проверку',
        null=True,
        related_name='NextStatus',
        on_delete=models.SET_NULL,
    )
    old_name = models.SmallIntegerField(
        verbose_name='Старое название правонарушения',
        choices=INFO_CHOICES,
        default=1,
    )

    def __str__(self):
        return f'{self.title}'

    class Meta:
        ordering = 'order', 'title',
        verbose_name = 'Вид правонарушения'
        verbose_name_plural = 'Виды правонарушений'
        managed = True


######################################################################################################################


class TypeNotify(models.Model):
    id = models.AutoField(
        primary_key=True,
    )
    title = models.CharField(
        verbose_name='Способ направления информирования',
        max_length=625,
        default='',
    )
    order = models.SmallIntegerField(
        verbose_name='Порядок в списке информирования',
        default=0,
    )
    old_name = models.SmallIntegerField(
        verbose_name='Старое название информирования',
        choices=METHOD_CHOICES,
        default=1,
        null=False,
        blank=False,
    )

    def __str__(self):
        return f'{self.title}'

    class Meta:
        ordering = 'order', 'title',
        verbose_name = 'Вид информирования'
        verbose_name_plural = 'Виды информирований'
        managed = True


######################################################################################################################


class TypeResult(models.Model):
    id = models.AutoField(
        primary_key=True,
    )
    title = models.CharField(
        verbose_name='Название результата',
        max_length=625,
        default='',
    )
    order = models.SmallIntegerField(
        verbose_name='Порядок в списке результатов',
        default=0,
    )
    next_status = models.ForeignKey(
        TypeStatus,
        verbose_name='Статус карточки при выборе результата',
        null=True,
        related_name='NextStatusResult',
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return f'{self.title}'

    class Meta:
        ordering = 'order',
        verbose_name = 'Вид результата'
        verbose_name_plural = 'Виды результатов'
        managed = True


######################################################################################################################


class TypeProtocol(models.Model):
    id = models.AutoField(
        primary_key=True,
    )
    title = models.CharField(
        verbose_name='Название направления протокола',
        max_length=625,
        default='',
    )
    order = models.SmallIntegerField(
        verbose_name='Порядок в списке результатов',
        default=0,
    )
    next_status = models.ForeignKey(
        TypeStatus,
        verbose_name='Статус карточки при выборе результата',
        null=True,
        related_name='NextStatusProtocol',
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return f'{self.title}'

    class Meta:
        ordering = 'order',
        verbose_name = 'Вид протокола'
        verbose_name_plural = 'Виды протоколов'
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
    department = models.ForeignKey(
        Department,
        verbose_name='Организация или отдел',
        null=True,
        related_name='Department',
        on_delete=models.SET_NULL,
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
        if self.department.role in list_permission:
            return True
        else:
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
        return f'{self.user.get_full_name()}'

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
    owner_department = models.ForeignKey(
        Department,
        verbose_name='Владелец',
        null=True,
        related_name='owner_department',
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
    status_new = models.ForeignKey(
        TypeStatus,
        verbose_name='Статус новый',
        null=True,
        related_name='Status',
        on_delete=models.SET_NULL,
    )
    Result = models.SmallIntegerField(
        verbose_name='Результат',
        choices=RESULT_CHOICES,
        null=True,
        blank=True,
    )
    SendDate = models.DateField(
        verbose_name='Дата направления в трудоустройство',
        null=True,
        blank=True,
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
        blank=True,
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
        return f'{self.Title}'

    def get_list_status(self) -> list:
        """
        Список статусов карточки нарушителя
        :return:
        """
        list_status = list(
            TypeStatus.objects.filter(
                id__in=list(
                    StatusEmployer.objects.filter(employer=self).values_list('type_status', flat=True)
                )
            )
        )
        return list_status

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
    employer = models.ForeignKey(
        Employer,
        verbose_name='Карточка работодателя-нарушителя',
        null=True,
        related_name='Employer',
        on_delete=models.CASCADE,
    )
    type_status = models.ForeignKey(
        TypeStatus,
        verbose_name='Статус карточки работодателя-нарушителя',
        null=True,
        related_name='TypeStatus',
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return f'{self.employer} - {self.type_status}'

    class Meta:
        ordering = 'type_status', 'employer',
        verbose_name = 'Статус карточки'
        verbose_name_plural = 'Статусы карточек'
        managed = True


######################################################################################################################


# class StatusRoute(models.Model):
#     id = models.AutoField(
#         primary_key=True,
#     )
#     current_status = models.ForeignKey(
#         TypeStatus,
#         verbose_name='Текущий статус',
#         null=True,
#         blank=True,
#         default=None,
#         related_name='StatusCurrent',
#         on_delete=models.SET_NULL,
#     )
#
#     def __str__(self):
#         return f'[{self.prev_status}] - {self.current_status} - [{self.next_status}]'
#
#     class Meta:
#         ordering = 'current_status',
#         verbose_name = 'Маршрут статуса'
#         verbose_name_plural = 'Маршруты статусов'
#         managed = True


######################################################################################################################


class Info(models.Model):
    id = models.AutoField(
        primary_key=True,
    )
    type_violations = models.ForeignKey(
        TypeViolations,
        verbose_name='Наименование правонарушения',
        null=True,
        related_name='TypeViolations',
        on_delete=models.SET_NULL,
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
        return f'{self.EmpInfoID} - {self.Name}'

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
        return f'{self.Title}'

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
        return f'{self.Comment}'

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
    create_date = models.DateTimeField(
        verbose_name='Дата создания записи',
        auto_now_add=True,
        null=True,
    )

    def __str__(self):
        return f'{self.create_date}'

    class Meta:
        ordering = '-create_date',
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
        return f'{self.Recipient} - {self.Reading}'

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
    type_notify = models.ForeignKey(
        TypeNotify,
        verbose_name='Наименование информирования',
        null=True,
        related_name='TypeNotify',
        on_delete=models.SET_NULL,
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
        return f'{self.EmpNotifyID} - {self.Method}'

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
        return f'{self.title}'

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
    color = models.CharField(
        verbose_name='Основной цвет',
        max_length=124,
        default='',
    )

    def __str__(self):
        return f'{self.title}'

    class Meta:
        ordering = 'order', 'title',
        verbose_name = 'Виджет'
        verbose_name_plural = 'Виджеты'
        managed = True


######################################################################################################################


# class ActionSteps(models.Model):
#     id = models.AutoField(
#         primary_key=True,
#     )
#     type_status = models.ForeignKey(
#         TypeStatus,
#         verbose_name='Тип статуса',
#         null=True,
#         blank=True,
#         default=None,
#         related_name='StepStatus',
#         on_delete=models.CASCADE,
#     )
#     department = models.ForeignKey(
#         Department,
#         verbose_name='Организация или отдел которые имеют доступ к выполнению данного шага',
#         null=True,
#         blank=True,
#         default=None,
#         related_name='DepartmentAccess',
#         on_delete=models.CASCADE,
#     )
#     template_path = models.CharField(
#         verbose_name='Путь до шаблона с формой шага карточки',
#         max_length=124,
#         default='',
#     )
#
#     def __str__(self):
#         return f'{self.template_path} - {self.type_status} [{self.department}]'
#
#     class Meta:
#         ordering = 'template_path', 'type_status',
#         verbose_name = 'Шаг действия'
#         verbose_name_plural ='Шаги действий'
#         managed = True


######################################################################################################################


class WidgetStatus(models.Model):
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
        TypeStatus,
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
        return f'{self.widget} - {self.status}'

    class Meta:
        ordering = 'widget', 'status',
        verbose_name = 'Фильтр статуса'
        verbose_name_plural = 'Фильтры стасусов'
        managed = True


######################################################################################################################
