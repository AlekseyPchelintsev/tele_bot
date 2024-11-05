# ЛОГИКА ПРОВЕРКИ НА НАЛИЧИЕ ЭМОДЗИ В СООБЩЕНИИ (ПЕРЕНЕСТИ)
import re

'''
async def check_emodji(user_name):
    check = re.search(r'('
                      r'[\U0001F600-\U0001F64F]|'
                      r'[\U0001F300-\U0001F5FF]|'
                      r'[\U0001F680-\U0001F6FF]|'
                      r'[\U0001F700-\U0001F77F]|'
                      r'[\U0001F800-\U0001F8FF]|'
                      r'[\U0001F900-\U0001F9FF]|'
                      r'[\U0001FA00-\U0001FAFF]|'
                      r'[\U00002700-\U000027BF]'
                      r')', user_name)
    return check is None
'''


async def check_emoji(text):
    # Шаблон для проверки эмодзи
    emoji_pattern = (
        r'[\U0001F600-\U0001F64F]|'  # Эмодзи лиц
        r'[\U0001F300-\U0001F5FF]|'  # Эмодзи объектов
        r'[\U0001F680-\U0001F6FF]|'  # Эмодзи транспорта
        r'[\U0001F700-\U0001F77F]|'  # Эмодзи символов
        r'[\U0001F800-\U0001F8FF]|'  # Эмодзи дополнительных символов
        r'[\U0001F900-\U0001F9FF]|'  # Эмодзи новых символов
        r'[\U0001FA00-\U0001FAFF]|'  # Эмодзи дополнительных символов
        r'[\U00002700-\U000027BF]|'  # Эмодзи символов
        r'[\U00002600-\U000026FF]|'  # Другие символы, включая ☀️
        r'[\U0001F004]|'              # Другие символы, включая ☄️
        r'[\U0000FE0F]|'              # Вариант эмодзи
        r'[\U0001F1E6-\U0001F1FF]{2}'  # Флаги (двойные символы)
    )

    # Проверяем наличие эмодзи
    return re.search(emoji_pattern, text) is not None
    # Проверяем наличие специальных символов Markdown

# проверка наличия полной markdown разметки


async def check_all_markdown(text):

    # Шаблон для проверки специальных символов Markdown
    markdown_pattern = r'([*_{}/()$~`>#+\-\\.!?|<%[\]])'

    return re.search(markdown_pattern, text) is not None


# проверка наличия частичной markdown разметки
async def check_partial_markdown(text):

    # Шаблон для проверки специальных символов Markdown
    markdown_pattern = r'([*_{}/$~`>#+\\.|<%[\]])'

    return re.search(markdown_pattern, text) is not None


# проверка наличия частичной markdown разметки для увлечений
async def check_markdown_hobbies(text):

    # Шаблон для проверки специальных символов Markdown
    markdown_pattern = r'([*_{}/()$~`>#+\-\\.!?|<%[\]])'

    return re.search(markdown_pattern, text) is not None

# поверка наличия чистичной markdown разметки для названия города


async def check_markdown_city_name(text):

    # Шаблон для проверки специальных символов Markdown
    markdown_pattern = r'([*_{}()\[\]~`>#+\.!?:%|<[\]])'

    return re.search(markdown_pattern, text) is not None
