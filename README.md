# tele_bot

frameworks:
</br>aiogram 3
</br>psycopg2

</br>Бот

</br>Реализованные механики:

</br>- При регистрации:

</br> - Отсутствие имени пользователя в профиле:
</br> - Уведомление с описанием как его добавить. Продолжить регистрацию нельзя.

</br> - Проверка на наличие user_id (при удалении анкеты не всегда подтягивает - решаю):
</br> - Вывожу уведомление и повторный переход в регистрацию (повторный переход обычно решает проблему).

</br> - При регистрации заведены проверки на форматы сообщений (если имя - нельзя отправить картинку или эмодзи + вывожу уведомление пользователю). Дата рождения завязана на datetime и проверке формата данных. При загрузке фото профиля - нельзя отправить ничего кроме изображения (так же вывожу уведомление).

</br>(user_1 - я, user_2 - другой пользователь)

</br> - Система реакций:
</br> - при лайке анкеты user_2:
</br> - Для user_2 отправляется уведомление (с кнопками «принять запрос» или «отложить»).
</br> - Анкета user_2 убирается из всех поисков user_1 и переносится в его «исходящие реакции».
</br> - Анкета user_1 попадает в «входящие реакции» user_2, но остается в поиске у user_2.

</br> - Если user_1 передумал и отозвал реакцию из меню «исходящие реакции»:
</br> - Если user_2 отправляет ответную реакцию на уведомление от user_1 - user_1 отправляется такое же уведомление о входящей реакции, а user_2 выводится сообщение, что «user_1 отменил свою реакцию, но мы ему отправили вашу реакцию».
</br> - Если в уведомлении user_2 откладывает анкету - он получает сообщение, что «реакция от user_1 была ранее отменена самим user_1». В таком случае ответная реакция от user_2 для user_1 не отправляется.
</br> - Оба пользователя снова выводятся друг другу в поиске.

</br>- В случае взаимных реакций:
</br> - user_1 и user_2 - обоим пользователям отправляются уведомления с кнопкой «открыть беседу» и «вернуться в меню»
</br> - Пользователи попадают друг к другу в раздел «мои контакты»

</br>- Удаление пользователя из контактов (по сути бессмысленно если user_1 ранее открывал беседу с user_2):
</br> - Если user_1 удаляет анкету user_2 из «мои контакты» - данные анкет удаляются у обоих пользователей из раздела «мои контакты».
</br> - user_2 попадает в список «удаленные пользователи» у user_1. При этом user_1 не попадает в раздел «удаленные пользователи» у user_2. Друг другу в поиске пользователи не выводятся.
</br> - Если user_1 возвращает user_2 в поиск, удаляя его анкету из раздела «удаленные пользователи» - все возвращается на начальный этап, как если бы они не были знакомы ранее (могут найти друг друга в поиске и снов а отправить друг другу реакции).
</br> - user_2 не может ничего с этим сделать, пока user_1 не уберет user_2 из раздела «заблокированные пользователи» (происходит по праву первого)

</br>- Поиск пользователей (перерабатываю т.к. система - ху е та):
</br> - При выборе любого из вариантов поиска, спрашивает предпочтение по полу.
</br> - Раздел поиска «Все пользователи» - выводит всех зарегистрированных пользователей с учетом выбора пола
</br> - Поиск «в вашем городе» - выводит всех пользователей из вашего города, указанного в анкете с учетом выбора пола
</br> - Поиск «по хобби» - пока что ищет по точному совпадению запроса (полностью перерабатываю этот раздел)

</br>- Редактирование профиля:
</br> - Редактируются все пункты, которые указывались при регистрации.
</br> - При удалении фото профиля загружается дефолтное изображение «об отсутствии фото»
</br> - Удаление хобби происходит через генерацию клавиатуры с кнопкой для каждого хобби, при нажатии на которую происходит удаление хобби и обновление страницы с учетом внесенных изменений.

</br>- Удаление анкеты:
</br> - При удалении анкеты удаляются каскадом все записи из всех таблиц, связанные по user_tg (реакций, взаимные реакций, хобби).
</br> - Не удаляются данные из таблицы «удаленные пользователи» и при повторной регистрации, туда подтягиваются данные о ранее заблокированных пользователях, которых можно от туда убрать при желании.

</br>Все завязал на inline клавиатурах (работают через колбэки, а не через команды по типу /start /help и выводятся в окне сообщений, а не вместо телефонной клававиатуры) и редактировании сообщений, а не отправке новых, чтобы минимизировать загрязнение чата. Но в некоторых местах (при отправке уведомлений о реакциях) избежать дополнительных сообщений не удалось.

</br>Добавить в анкету поле «О себе» где пользователь сможет описать развернуто и в свободной форме свою характеристику. Поиск по «хобби» оставить как есть сейчас, но сделать возможность поиска по нескольким увлечениям сразу. Так же сделать поиск условных «единомышленников», который будет выводить всех пользователей, с которыми совпадает хотя бы одно из увлечений, указанных у «меня» в анкете и возможностью указать город в котором хочет найти «единомышленников» (или искать во всех городах, на случай если человеку не принципиально географическое расположение).
