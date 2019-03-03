
ROLE_CHOICES = (
    (1, 'ЦЗН'),
    (2, 'Трудоустройство'),
    (3, 'Правовой'),
    (4, 'Руководство')
)

METHOD_CHOICES = (
    (1, 'Направлено информационное письмо по форме согласно приложению № 2 к настоящему Порядку'),
    (2, 'Размещена информация в СМИ'),
    (3, 'Проведена встреча с работодателями, клубы "Работодатель", "Кадровик"'),
    (4, 'С помощью издания и распространения печатной продукции (брошюр, буклетов и т.п.)'),
    (5, 'Ознакомление работодателей при их личном обращении в центры занятости, по телефону или письменно, включая электронную почту'),
    (6, 'Размещена информация на информационных стендах и (или) других технических средствах аналогичного назначения в помещениях центров занятости и иных организаций')
)

EMPLOYER_CHOICES = (
    (1, 'Юридическое лицо'),
    (2, 'Индивидуальный предприниматель')
)

PROTOCOL_CHOICES = (
    (1, 'Получил уведомление, явился на составление протокола'),
    (2, 'Получил уведомление, не явился на составление протокола'),
    (3, 'Не получил уведомление, не явился на составление протокола')
)

RESULT_CHOICES = (
    (0, 'Выберите результат'),
    (1, 'Предупреждение'),
    (2, 'Штраф'),
    (3, 'Отказ')
)

RETURN_CHOICES = (
    (1, 'некорректно введено наименование работодателя'),
    (2, 'некорректно введен юридический адрес'),
    (3, 'некорректно введен фактический адрес'),
    (4, 'некорректно введен ИНН'),
    (5, 'некорректно введен ОГРН'),
    (0, 'другое')
)

INFO_CHOICES = (
    (1, 'Ликвидация организации (юридического лица)'),
    (2, 'Сокращение численности или штата работников организации (юридического лица)'),
    (3, 'Прекращение деятельности индивидуального предпринимателя'),
    (4, 'Сокращение численности или штата работников индивидуального предпринимателя'),
    (5, 'Введение режима неполного рабочего дня (смены) и (или) неполной рабочей недели, а также приостановка производства'),
    (6, 'Сведения о применении в отношении работодателя процедур о несостоятельности (банкротстве)'),
    (7, 'Информация, необходимая для осуществления деятельности по профессиональной реабилитации и содействию занятости инвалидов'),
    (8, 'Информация о наличии свободных рабочих мест и вакантных должностей'),
    (9, 'Информация о наличии свободных рабочих мест и вакантных должностей созданных или выделенных рабочих '
        'местах для трудоустройства инвалидов в соответствии с установленной квотой для приема на работу инвалидов'),
    (10, 'Информация о свободных рабочих местах или вакантных должностях, содержащая ограничения дискриминационного характера'),
)

STATUS_CHOICES = (
    (20, 'Все статусы'),
    (0, 'Черновик'),
    (1, 'Редактируется центром занятости'),
    (2, 'Проверяется отделом трудоустройства и специальных программ'),
    (3, 'Формирование уведомление о вызове на составление протокола'),
    (4, 'Направление уведомление о вызове на составление протокола'),
    (5, 'Составление протокола об административном правонарушении'),
    (10, 'Направление протокола работодателю'),
    (6, 'Формирование заявления Мировому судье о рассмотрении протокола'),
    (7, 'Ожидается результат рассмотрения протокола Мировым судьей'),
    (8, 'Отменено'),
    (9, 'Вынесено постановление'),
    (11, 'Ожидание результат исполнения постановления'),
    (12, 'Закрыто')
)
