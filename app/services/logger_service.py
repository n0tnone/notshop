import logging
import logging.handlers
import os
import re
import sys
from datetime import datetime


SESSION_UPDATE_COUNTER = 0

try:
    import colorama
    colorama.init(autoreset=True)
    Fore = colorama.Fore
    Style = colorama.Style
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False

    class Fore:
        pass

    class Style:
        pass
    setattr(Fore, "RESET", "")
    setattr(Fore, "CYAN", "")
    setattr(Fore, "BLUE", "")
    setattr(Fore, "GREEN", "")
    setattr(Fore, "YELLOW", "")
    setattr(Fore, "RED", "")
    setattr(Fore, "MAGENTA", "")
    setattr(Style, "RESET_ALL", "")
    setattr(Style, "BRIGHT", "")


class AiogramEventFilter(logging.Filter):
    """
    Фильтр для обогащения лог-записей от aiogram.event.
    Добавляет счетчик обновлений за сессию и парсит аргументы.
    """

    def filter(self, record):
        global SESSION_UPDATE_COUNTER

        expected_msg_template = "Update id=%s is %s. Duration %d ms by bot id=%d"
        if record.name == 'aiogram.event' and record.msg == expected_msg_template:

            SESSION_UPDATE_COUNTER += 1
            record.session_update_count = SESSION_UPDATE_COUNTER

            if hasattr(record, 'args') and isinstance(record.args, tuple):
                if len(record.args) >= 1:
                    record.parsed_update_id = record.args[0]

                if len(record.args) >= 3:
                    record.parsed_duration_ms = record.args[2]

            record.original_aiogram_msg_template = record.msg
        return True


class ColorizingFormatter(logging.Formatter):
    """
    Кастомный форматер для логирования с цветами в консоли.
    Числа в сообщении будут подсвечены.
    Специально обрабатывает сообщения от aiogram.event.
    """
    LEVEL_COLORS = {
        logging.DEBUG: Fore.BLUE,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA,
    } if HAS_COLORAMA else {}

    def format(self, record):

        original_levelname = record.levelname
        text_message_with_args_if_not_overridden = record.getMessage()

        _original_msg_for_record = record.msg
        _original_args_for_record = record.args
        _formatter_modified_msg_or_args = False

        if HAS_COLORAMA:
            color = self.LEVEL_COLORS.get(record.levelno, Fore.RESET)
            record.levelname = f"{color}{Style.BRIGHT}{original_levelname}{Style.RESET_ALL}"

        _processed_as_aiogram_event = False

        expected_msg_template_for_formatter = "Update id=%s is %s. Duration %d ms by bot id=%d"
        if record.name == 'aiogram.event' and \
           hasattr(record, 'session_update_count') and \
           getattr(record, 'original_aiogram_msg_template', None) == expected_msg_template_for_formatter:

            update_id_str = f"ID {record.parsed_update_id}" if hasattr(
                record, 'parsed_update_id') else "ID (неизвестно)"

            duration_val = getattr(record, 'parsed_duration_ms', None)
            duration_str = f"{int(duration_val)} мс" if duration_val is not None else "(неизвестно)"

            new_msg_template = (
                f"Обработано обновление {Style.BRIGHT}"
                f"[{Fore.CYAN}{update_id_str}{Style.RESET_ALL}]. "
                f"Длительность: {Fore.GREEN}{duration_str}{Style.RESET_ALL}."
            )
            
            record.msg = new_msg_template
            record.args = tuple()
            _formatter_modified_msg_or_args = True
            _processed_as_aiogram_event = True

        elif HAS_COLORAMA and not _processed_as_aiogram_event:
            
            
            
            
            colored_text_message = re.sub(
                r'(\b\d+\.?\d*\b)', f'{Fore.CYAN}\\1{Style.RESET_ALL}', text_message_with_args_if_not_overridden)
            
            record.msg = colored_text_message
            record.args = tuple()
            _formatter_modified_msg_or_args = True
        
        formatted_log = super().format(record)
        
        
        
        

        record.levelname = original_levelname

        if _formatter_modified_msg_or_args:
            record.msg = _original_msg_for_record
            record.args = _original_args_for_record
        
        return formatted_log


def setup_logging(
    log_dir="logs",
    console_level=logging.INFO,
    file_level=logging.DEBUG,
    aiogram_level=logging.INFO,
    log_file_name="app.log",
    symlink_name="latest.log"
):
    """
    Настраивает систему логирования.

    :param log_dir: Директория для сохранения лог-файлов.
    :param console_level: Уровень логирования для вывода в консоль.
    :param file_level: Уровень логирования для записи в файл.
    :param aiogram_level: Уровень логирования для библиотеки aiogram.
    :param log_file_name: Базовое имя файла для логов.
    :param symlink_name: Имя символической ссылки на последний лог.
    """
    if not HAS_COLORAMA:
        print("Предупреждение: библиотека colorama не найдена. Логи в консоли не будут окрашены.", file=sys.stderr)

    try:
        os.makedirs(log_dir, exist_ok=True)
    except OSError as e:
        print(f"Ошибка создания директории логов {log_dir}: {e}", file=sys.stderr)
        return

    console_format_str = "%(asctime)s - %(levelname)s - [%(name)s] - %(message)s"
    if not HAS_COLORAMA:
        console_formatter = logging.Formatter(
            console_format_str, datefmt="%Y-%m-%d %H:%M:%S")
    else:
        console_formatter = ColorizingFormatter(
            console_format_str, datefmt="%Y-%m-%d %H:%M:%S")

    file_format_str = "%(asctime)s - %(levelname)s - [%(name)s:%(module)s:%(funcName)s:%(lineno)d] - %(message)s"
    file_formatter = logging.Formatter(
        file_format_str, datefmt="%Y-%m-%d %H:%M:%S")

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    current_log_file_path = os.path.join(log_dir, log_file_name)

    file_handler = logging.handlers.TimedRotatingFileHandler(
        current_log_file_path, when="midnight", interval=1, backupCount=7, encoding="utf-8"
    )
    file_handler.setLevel(file_level)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    aiogram_logger = logging.getLogger("aiogram")
    aiogram_logger.setLevel(aiogram_level)

    aiogram_event_specific_logger = logging.getLogger("aiogram.event")
    aiogram_event_specific_logger.addFilter(AiogramEventFilter())

    logging.info("Система логирования инициализирована.")
    logging.debug(
        f"Уровень логов консоли: {logging.getLevelName(console_level)}, Уровень логов файла: {logging.getLevelName(file_level)}")
    logging.info(f"Текущий файл логов: {os.path.abspath(current_log_file_path)}")

    symlink_target_path = os.path.join(log_dir, symlink_name)

    if os.path.exists(symlink_target_path) or os.path.islink(symlink_target_path):
        try:
            os.remove(symlink_target_path)
        except OSError as e:
            logging.warning(
                f"Не удалось удалить старую символическую ссылку/файл {symlink_target_path}: {e}")

    try:

        os.symlink(log_file_name, symlink_target_path)
        logging.info(
            f"Символическая ссылка создана: {symlink_target_path} -> {log_file_name}")
    except (OSError, AttributeError) as e:
        fallback_path_file = os.path.join(log_dir, "latest_log_path.txt")
        logging.warning(
            f"Не удалось создать символическую ссылку '{symlink_target_path}' (ОС: {os.name}, Ошибка: {e}). "
            f"Это может потребовать Режим разработчика или права администратора в Windows. "
            f"Создается файл с путем к текущему логу: '{fallback_path_file}'."
        )
        try:
            with open(fallback_path_file, "w", encoding="utf-8") as f:
                f.write(os.path.abspath(current_log_file_path))
            logging.info(
                f"Создан файл '{fallback_path_file}', указывающий на {os.path.abspath(current_log_file_path)}")
        except Exception as e_txt:
            logging.error(f"Не удалось создать файл '{fallback_path_file}': {e_txt}")
