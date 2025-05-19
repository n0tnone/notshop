import math
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Callable, List, Tuple, Optional, Dict, Any, Union

class PageCallbackData(CallbackData, prefix="page_nav"):
    action: str
    page_num: int 

class ButtonData:
    """Структура для хранения данных кнопки перед созданием объекта InlineKeyboardButton."""

    def __init__(self, text: str, callback_data: Optional[str] = None, url: Optional[str] = None, **kwargs):
        self.text = text
        self.callback_data = callback_data
        self.url = url
        self.kwargs = kwargs

    def to_aiogram_button(self) -> InlineKeyboardButton:
        params = {"text": self.text}
        if self.callback_data:
            params["callback_data"] = self.callback_data
        elif self.url:
            params["url"] = self.url
        params.update(self.kwargs)
        return InlineKeyboardButton(**params)
    
class KeyboardBuilder:
    def __init__(self, _: Callable):
        self._buttons: List[ButtonData] = []
        self._ = _

    def add_button(
        self,
        text: str,
        callback_data: Optional[str] = None,
        url: Optional[str] = None,
        **kwargs 
    ) -> 'KeyboardBuilder':
        self._buttons.append(ButtonData(text, callback_data, url, **kwargs))
        return self

    def add_buttons(self, buttons_data: List[Union[ButtonData, Dict[str, Any]]]) -> 'KeyboardBuilder':
        for btn_data in buttons_data:
            if isinstance(btn_data, ButtonData):
                self._buttons.append(btn_data)
            elif isinstance(btn_data, dict):
                if 'text' not in btn_data:
                    raise ValueError("Словарь для кнопки должен содержать ключ 'text'.")
                self._buttons.append(ButtonData(**btn_data))
            else:
                raise TypeError("Элементы списка buttons_data должны быть ButtonData или dict.")
        return self

    def _generate_pagination_buttons(
        self, 
        current_page_for_controls: int, 
        total_pages_for_controls: int, 
        page_callback_factory: Any,
        action_name_for_factory: str
    ) -> List[InlineKeyboardButton]:
        pagination_row: List[InlineKeyboardButton] = []
        if current_page_for_controls > 1:
            prev_page_cb_data = page_callback_factory(
                action=action_name_for_factory, 
                page_num=current_page_for_controls - 1
            ).pack()
            pagination_row.append(InlineKeyboardButton(text=self._("buttons.pagination.prev"), callback_data=prev_page_cb_data))
        
        ignore_cb_data = "ignore_pagination_state"
        try:
            ignore_cb_data = page_callback_factory(action="ignore_state", page_num=current_page_for_controls).pack()
        except TypeError:
            pass

        pagination_row.append(InlineKeyboardButton(
            text=self._("buttons.pagination.current_page", current_page=current_page_for_controls, total_pages=total_pages_for_controls),
            callback_data=ignore_cb_data
        ))

        if current_page_for_controls < total_pages_for_controls:
            next_page_cb_data = page_callback_factory(
                action=action_name_for_factory,
                page_num=current_page_for_controls + 1
            ).pack()
            pagination_row.append(InlineKeyboardButton(text=self._("buttons.pagination.next"), callback_data=next_page_cb_data))
        return pagination_row

    def build(
        self,
        layout: Optional[Tuple[int, ...]] = None,
        default_row_width: int = 1,
        items_per_page: Optional[int] = None,
        current_page: int = 1,
        page_callback_data_provider: Optional[Dict[str, Any]] = None
    ) -> InlineKeyboardMarkup:
        """
        Собирает и возвращает InlineKeyboardMarkup.

        :param layout: Кортеж для расположения кнопок текущей страницы.
        :param default_row_width: Ширина ряда по умолчанию для кнопок текущей страницы.
        :param items_per_page: Количество основных кнопок (из self._buttons) на одной странице.
                               Если None, все кнопки из self._buttons отображаются.
        :param current_page: Номер текущей отображаемой страницы контента (начинается с 1).
        :param page_callback_data_provider: Словарь с { "factory": PageCallbackData, "action": "имя_действия" }.
                                            Если указан и страниц больше одной, пагинация будет добавлена.
        :return: Готовая инлайн-клавиатура.
        """
        markup_rows: List[List[InlineKeyboardButton]] = []
        
        buttons_to_display_data: List[ButtonData]
        actual_total_pages_for_controls = 1
        actual_current_page_for_controls = 1

        if items_per_page and items_per_page > 0 and self._buttons:
            total_content_buttons = len(self._buttons)
            actual_total_pages_for_controls = math.ceil(total_content_buttons / items_per_page)
            actual_current_page_for_controls = max(1, min(current_page, actual_total_pages_for_controls))
            start_index = (actual_current_page_for_controls - 1) * items_per_page
            end_index = start_index + items_per_page
            buttons_to_display_data = self._buttons[start_index:end_index]
        else:
            buttons_to_display_data = list(self._buttons)
            page_callback_data_provider = None

        aiogram_buttons_for_page = [btn_data.to_aiogram_button() for btn_data in buttons_to_display_data]
        
        current_button_idx_for_page = 0
        num_total_buttons_for_page = len(aiogram_buttons_for_page)

        if layout:
            for num_buttons_in_row in layout:
                if current_button_idx_for_page >= num_total_buttons_for_page: break
                row = aiogram_buttons_for_page[current_button_idx_for_page : current_button_idx_for_page + num_buttons_in_row]
                if row: markup_rows.append(row)
                current_button_idx_for_page += num_buttons_in_row
        elif default_row_width > 0:
            for i in range(0, num_total_buttons_for_page, default_row_width):
                markup_rows.append(aiogram_buttons_for_page[i : i + default_row_width])
        elif aiogram_buttons_for_page: 
            for button in aiogram_buttons_for_page:
                markup_rows.append([button])
        
        if page_callback_data_provider and actual_total_pages_for_controls > 1:
            factory = page_callback_data_provider.get('factory')
            action_name = page_callback_data_provider.get('action')

            if not factory or not action_name:
                raise ValueError("page_callback_data_provider должен содержать ключи 'factory' и 'action'.")

            pagination_row_buttons = self._generate_pagination_buttons(
                actual_current_page_for_controls,
                actual_total_pages_for_controls,
                factory,
                action_name
            )
            if pagination_row_buttons:
                markup_rows.append(pagination_row_buttons)

        self._buttons = [] 
        return InlineKeyboardMarkup(inline_keyboard=markup_rows)