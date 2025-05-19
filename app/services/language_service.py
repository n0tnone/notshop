import json
import logging
import os
from app import config



printx = logging.getLogger(__name__)

translations = {}


def load_translations():
    """Загружает все доступные переводы из файлов JSON."""
    for lang_code in os.listdir(config.LOCALES_DIR):
        if lang_code.endswith(".json"):
            lang = lang_code[:-5]
            file_path = os.path.join(config.LOCALES_DIR, lang_code)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    translations[lang] = json.load(f)
                printx.info(f"Переводы для языка '{lang}' успешно загружены.")
            except Exception as e:
                printx.info(f"Ошибка загрузки переводов для '{lang}': {e}")


def get_text(key: str, lang: str = "ru", **kwargs) -> str:
    """
    Получает текст по ключу для указанного языка и форматирует его.
    :param key: Ключ текста (например, "welcome" или "buttons.profile").
    :param lang: Код языка пользователя (например, "ru", "en").
    :param kwargs: Именованные аргументы для подстановки в текст.
    :return: Переведенный и отформатированный текст или ключ, если перевод не найден.
    """

    keys = key.split('.')
    text_template = translations.get(lang, translations.get(config.BASE_LOCAL))

    try:
        for k in keys:
            if isinstance(text_template, dict):
                text_template = text_template[k]
            else:
                printx.info(
                    f"Ключ '{key}' не найден для языка '{lang}' на уровне '{k}'")
                return key

        if not isinstance(text_template, str):
            printx.info(
                f"Значение для ключа '{key}' не является строкой для языка '{lang}'")
            return key

    except KeyError:
        printx.info(f"Ключ '{key}' не найден для языка '{lang}'")
        default_lang_translations = translations.get("ru", {})
        text_template_default = default_lang_translations
        try:
            for k_default in keys:
                if isinstance(text_template_default, dict):
                    text_template_default = text_template_default[k_default]
                else:
                    return key
            if isinstance(text_template_default, str):
                return text_template_default.format_map(kwargs) if kwargs else text_template_default
        except KeyError:
            return key
        return key

    return text_template.format_map(kwargs) if kwargs else text_template
