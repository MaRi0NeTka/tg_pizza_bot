from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

class MenuCallBack(CallbackData, prefix ='menu'):
    level:int
    menu_name:str
    category:int|None = None
    page:int = 1
    product_id:int | None = None


def get_user_main_btns(*, level:int, sizes: tuple[int] = (2,)):
    kb = InlineKeyboardBuilder()
    btns = {
        "Товары 🍕": "catalog",
        "Корзина 🛒": "cart",
        "О нас ℹ️": "about",
        "Оплата 💰": "payment",
        "Доставка ⛵": "shipping",
    }
    for text, menu_name in btns.items():
        if menu_name == 'catalog':
            kb.add(InlineKeyboardButton(text=text, callback_data=MenuCallBack(level=level+1, menu_name=menu_name).pack()))
        elif menu_name == "cart":
            kb.add(InlineKeyboardButton(text=text, callback_data=MenuCallBack(level=3, menu_name=menu_name).pack()))
        else:
            kb.add(InlineKeyboardButton(text=text, callback_data=MenuCallBack(level=level, menu_name=menu_name).pack()))
    
    return kb.adjust(*sizes).as_markup()


def get_user_categories(*, level:int, categories:list, sizes:tuple[int]=(2,)):
    kb = InlineKeyboardBuilder()
    
    kb.add(InlineKeyboardButton(text='Назад',callback_data=MenuCallBack(level=0,menu_name='main').pack()))
    kb.add(InlineKeyboardButton(text='Корзина',callback_data=MenuCallBack(level=3,menu_name='cart').pack()))

    for categ in categories:
        kb.add(InlineKeyboardButton(text=categ.name,
                                    callback_data=MenuCallBack(level=level+1, menu_name=categ.name, category=categ.id).pack()))
        
    return kb.adjust(*sizes).as_markup()

def get_products_btns(
        *,
        level:int,
        category:int, 
        page:int, 
        pagination_btns:dict,
        product_id:int,
        sizes:tuple[int] = (2,1)
        ):
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text='Назад', callback_data=MenuCallBack(level=level-1, menu_name='catalog').pack()))
    kb.add(InlineKeyboardButton(text="Корзина 🛒", callback_data=MenuCallBack(level=3, menu_name='cart').pack()))
    kb.add(InlineKeyboardButton(text='Купить 💵', callback_data=MenuCallBack(level=level, menu_name='add_to_cart', product_id=product_id).pack()))
    kb.adjust(*sizes)

    row = []
    for text, menu_name in pagination_btns.items():
        if menu_name == 'next':
            btn = InlineKeyboardButton(text=text, callback_data=MenuCallBack(level=level, menu_name=menu_name, category=category, page=page+1).pack())
            row.append(btn)
        elif menu_name == 'previous':
            btn = InlineKeyboardButton(text=text, callback_data=MenuCallBack(level=level, menu_name=menu_name, category=category, page=page-1).pack())
            row.append(btn)
    kb = kb.row(*row).as_markup()
    return kb


def get_cart_btns(
        *,
        level:int,
        page:int,
        pagination_btns:dict|None,
        product_id:int|None,
        sizes:tuple[int] = (3,)
        ):
    kbrd = InlineKeyboardBuilder()
    if page:
        kbrd.add(InlineKeyboardButton(text='Удалить',callback_data=MenuCallBack(level=level, menu_name='delete', product_id=product_id, page=page).pack()))
        kbrd.add(InlineKeyboardButton(text='-1', callback_data=MenuCallBack(level=level, menu_name='decrement', product_id=product_id, page=page).pack()))
        kbrd.add(InlineKeyboardButton(text='+1', callback_data=MenuCallBack(level=level, menu_name='increment', product_id=product_id, page=page).pack()))
        kbrd.adjust(*sizes)
        row = []
        for text, menu_name in pagination_btns.items():
            if menu_name == 'next':
                btn = InlineKeyboardButton(text = text, callback_data=MenuCallBack(level=level,menu_name=menu_name,page=page+1).pack())
                row.append(btn)
            elif menu_name == 'previous':
                btn = InlineKeyboardButton(text = text, callback_data=MenuCallBack(level=level,menu_name=menu_name,page=page-1).pack())
                row.append(btn)

        kbrd.row(*row)
        array_2 = [
            InlineKeyboardButton(text='На главную 🏠', callback_data=MenuCallBack(level=0, menu_name='main').pack()),
            InlineKeyboardButton(text='Заказать', callback_data='make_final_order')
        ]
        return kbrd.row(*array_2).as_markup()
    else:
        kbrd.add(InlineKeyboardButton(text='На главную 🏠', callback_data=MenuCallBack(level=0, menu_name='main').pack()))
        return  kbrd.adjust(*sizes).as_markup()

def get_call_btns(
        *, 
        btns:dict[str, str],
        size: tuple[int] = (2,)):
    kboard = InlineKeyboardBuilder()
    for text, data in btns.items():
        kboard.add(InlineKeyboardButton(text = text, callback_data=data))
    return kboard.adjust(*size).as_markup()
