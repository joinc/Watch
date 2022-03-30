# -*- coding: utf-8 -*-

FULL_MENU = (
    (
        ('czn', ),
        'employer_temp_list',
        'Создать карточку из Катарсиса',
        '',
    ),
    (
        ('czn',),
        'employer_create',
        'Создать карточку вручную',
        '',
    ),
    (
        ('control',),
        'employer_temp_list',
        'Создать архивную карточку из Катарсиса',
        '',
    ),
    (
        ('control',),
        'archive',
        'Создать архивную карточку вручную',
        '',
    ),
    (
        ('admin',),
        'response_list',
        'Назначить ответственного',
        '',
    ),
    (
        ('control', 'assist', 'job', 'admin', 'czn', ),
        'report_list',
        'Отчеты',
        'fas fa-chart-bar',
    ),
    (
        ('control', 'assist', 'job', 'admin', 'czn', ),
        'employer_export',
        'Скачать данные',
        'fas fa-download',
    ),
    (
        ('control', 'assist', 'job', 'admin', 'czn', ),
        'message_list',
        'Уведомления',
        'far fa-comment-alt',
    ),
)

ROLE_CHOICES = (
    (
        1,
        'ЦЗН',
    ),
    (
        2,
        'Трудоустройство',
    ),
    (
        3,
        'Правовой',
    ),
    (
        4,
        'Руководство',
    )
)

ROLES_CHOICES = (
    (
        'control',
        'Отдел надзора и контроля в сфере занятости населения',
    ),
    (
        'assist',
        'Отдел содействия занятости инвалидов',
    ),
    (
        'job',
        'Отдел трудоустройства и специальных программ',
    ),
    (
        'admin',
        'Руководство',
    ),
    (
        'czn',
        'Центр занятости',
    ),
)

METHOD_CHOICES = (
    (
        1,
        'Направлено информационное письмо по форме согласно приложению № 2 к настоящему Порядку',
    ),
    (
        2,
        'Размещена информация в СМИ',
    ),
    (
        3,
        'Проведена встреча с работодателями, клубы "Работодатель", "Кадровик"',
    ),
    (
        4,
        'С помощью издания и распространения печатной продукции (брошюр, буклетов и т.п.)',
    ),
    (
        5,
        'Ознакомление работодателей при их личном обращении в центры занятости, по телефону или письменно, '
        'включая электронную почту',
    ),
    (
        6,
        'Размещена информация на информационных стендах и (или) других технических средствах аналогичного назначения '
        'в помещениях центров занятости и иных организаций',
    )
)

EMPLOYER_CHOICES = (
    (
        1,
        'Юридическое лицо',
    ),
    (
        2,
        'Индивидуальный предприниматель',
    )
)

PROTOCOL_CHOICES = (
    (
        1,
        'Получил уведомление, явился на составление протокола',
    ),
    (
        2,
        'Получил уведомление, не явился на составление протокола',
    ),
    (
        3,
        'Не получил уведомление, не явился на составление протокола',
    )
)

RESULT_CHOICES = (
    (
        0,
        'Выберите результат',
    ),
    (
        1,
        'Предупреждение',
    ),
    (
        2,
        'Штраф',
    ),
    (
        3,
        'Отказ',
    )
)

RETURN_CHOICES = (
    (
        1,
        'некорректно введено наименование работодателя',
    ),
    (
        2,
        'некорректно введен юридический адрес',
    ),
    (
        3,
        'некорректно введен фактический адрес',
    ),
    (
        4,
        'некорректно введен ИНН',
    ),
    (
        5,
        'некорректно введен ОГРН',
    ),
    (
        0,
        'другое',
    )
)

INFO_CHOICES = (
    (
        1,
        'Непредоставление (предоставление с нарушением сроков или не в полном объеме) информации о ликвидации '
        'организации (юридического лица)',
    ),
    (
        2,
        'Непредоставление (предоставление с нарушением сроков или не в полном объеме) информации о сокращение '
        'численности или штата работников организации (юридического лица)',
    ),
    (
        3,
        'Непредоставление (предоставление с нарушением сроков или не в полном объеме) информации о прекращение '
        'деятельности индивидуального предпринимателя',
    ),
    (
        4,
        'Непредоставление (предоставление с нарушением сроков или не в полном объеме) информации о сокращении '
        'численности или штата работников индивидуального предпринимателя',
    ),
    (
        5,
        'Непредоставление (предоставление с нарушением сроков или не в полном объеме) информации о введение режима '
        'неполного рабочего дня (смены) и (или) неполной рабочей недели, а также приостановка производства',
    ),
    (
        6,
        'Непредоставление (предоставление с нарушением сроков или не в полном объеме) сведения о применении в '
        'отношении работодателя процедур о несостоятельности (банкротстве)',
    ),
    (
        7,
        'Непредоставление (предоставление с нарушением сроков или не в полном объеме) информации, необходимой для '
        'осуществления деятельности по профессиональной реабилитации и содействию занятости инвалидов',
    ),
    (
        8,
        'Непредоставление (предоставление с нарушением сроков или не в полном объеме) информации о наличии свободных '
        'рабочих мест и вакантных должностей',
    ),
    (
        9,
        'Непредоставление (предоставление с нарушением сроков или не в полном объеме) информация о наличии свободных '
        'рабочих мест и вакантных должностей созданных или выделенных рабочих местах для трудоустройства инвалидов '
        'в соответствии с установленной квотой для приема на работу инвалидов',
    ),
    (
        10,
        'Непредоставление (предоставление с нарушением сроков или не в полном объеме) информации о свободных рабочих '
        'местах или вакантных должностях, содержащая ограничения дискриминационного характера',
    ),
    (
        11,
        'Непредоставление (предоставление с нарушением сроков или не в полном объеме) информации о выделенных '
        '(созданных) рабочих местах для трудоустройства инвалидов в соответствии с установленной квотой для приема '
        'на работу инвалидов и о локальных нормативных актах, содержащих сведения о данных рабочих местах',
    ),
    (
        12,
        'Непредоставление (предоставление с нарушением сроков или не в полном объеме) информации о выполнении квоты '
        'для приема на работу инвалидов',
    ),
    (
        13,
        'Неисполнение работодателем обязанности по созданию или выделению рабочих мест для трудоустройства инвалидов '
        'в соответствии с установленной квотой для приема на работу инвалидов',
    ),
    (
        14,
        'Отказ работодателя в приеме на работу инвалида в пределах установленной квоты',
    ),
)

STATUS_CHOICES = (
    (
        20,
        'Все статусы',
    ),
    (
        0,
        'Черновик',
    ),
    (
        1,
        'Редактируется центром занятости',
    ),
    (
        2,
        'Проверяется отделом трудоустройства и специальных программ',
    ),
    (
        3,
        'Формирование уведомление о вызове на составление протокола',
    ),
    (
        4,
        'Направление уведомление о вызове на составление протокола',
    ),
    (
        5,
        'Составление протокола об административном правонарушении',
    ),
    (
        10,
        'Направление протокола работодателю',
    ),
    (
        6,
        'Формирование заявления Мировому судье о рассмотрении протокола',
    ),
    (
        7,
        'Ожидается результат рассмотрения протокола Мировым судьей',
    ),
    (
        8,
        'Отменено',
    ),
    (
        9,
        'Вынесено постановление',
    ),
    (
        11,
        'Ожидание результат исполнения постановления',
    ),
    (
        12,
        'Закрыто',
    )
)
