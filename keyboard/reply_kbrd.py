from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton, ReplyKeyboardRemove



def build_kb(
        *btns,
        placeholder:str = None,
        contact:int = None,
        location:int = None,
        sizes:tuple[int] = (2,)):
    """Parameters request_contact and request_location
       must be as indexes of btns args
       for buttons you need.
       Example:
    get_keyboard(
            "Меню",
            "О магазине",
            "Варианты оплаты",
            "Варианты доставки",
            "Отправить номер телефона"
            placeholder="Что вас интересует?",
            request_contact=4,
            sizes=(2, 2, 1)
        )
       """
    kbrd = ReplyKeyboardBuilder()
    for indx, text in enumerate(btns, start=0):
        if contact and contact == indx:
            kbrd.add(KeyboardButton(text=text,request_contact=contact))
        
        elif location and location == indx:
            kbrd.add(KeyboardButton(text=text, request_location=location))

        else:
            kbrd.add(KeyboardButton(text=text))

    return kbrd.adjust(*sizes).as_markup(
        resize_keyboard=True,
        input_field_placeholder=placeholder
        )
    

'''Удаление клавиатуры'''
del_kb = ReplyKeyboardRemove()
