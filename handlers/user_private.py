"""ОБРАБАТЫВАЕТ СООБЩЕНИЯ 
    можем осуществлять обращение к боту через message.bot"""
from aiogram import types, Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from sqlalchemy.ext.asyncio import AsyncSession

from filters.chat_types import ChatFilterTypes
from keyboard.inline_kb import get_call_btns, MenuCallBack
from database.orm_makefunc_add import orm_add_user, orm_add_to_cart, orm_get_user_card
from handlers.menu_proccesing import get_menu_content

user_router = Router()
user_router.message.filter(ChatFilterTypes(['private'])) 


@user_router.message(CommandStart())
async def statr_cmd(message:types.Message, session:AsyncSession):
    media, reply_markup = await get_menu_content(session, level=0,menu_name = 'main')
    await message.answer_photo(media.media, caption=media.caption, reply_markup=reply_markup)


async def add_to_cart(callback:types.CallbackQuery, callback_data:dict, session:AsyncSession):
    user = callback.from_user
    await orm_add_user(
        session,
        user_id= user.id,
        first_name= user.first_name,
        last_name=(user.last_name if user.last_name is not None else 'None'),
        phone='None',
    )
    await orm_add_to_cart(session, user_id=user.id, product_id=callback_data.product_id)
    await callback.answer("Товар добавлен в корзину.",show_alert=True)
    

@user_router.callback_query(MenuCallBack.filter())
async def user_menu(callback:types.CallbackQuery, callback_data:MenuCallBack, session:AsyncSession):
    if callback_data.menu_name == 'add_to_cart':
        await add_to_cart(callback, callback_data, session)
        return 
    
    media, kb = await get_menu_content(session=session,
                                       level=callback_data.level,
                                       menu_name=callback_data.menu_name,
                                       category = callback_data.category,
                                       page = callback_data.page,
                                       user_id = callback.from_user.id,
                                       product_id=callback_data.product_id)
    
    await callback.message.edit_media(media=media, reply_markup=kb)
    await callback.answer() 












class MakeOrder(StatesGroup):
    name = State()
    place = State()
    promocode = State()
    phone = State()

    promocodes = {'LUCK4U':10}
    text = {
        "MakeOrder:name": "Введите имя снова:",
        "MakeOrder:place": "Введите место выдачи снова:",
        "MakeOrder:promocode": "Укажите промокод заново",
        "MakeOrder:phone": "Введите номер телефона заново 380 66 111 00 11"
    }



@user_router.callback_query(State(None),F.data == 'make_final_order')
async def make_ordef(callback:types.CallbackQuery, state:FSMContext):
    await callback.answer(text='Сейчас происходят последние шаги',show_alert=True)
    await callback.message.answer('Укажите ваше имя')
    await state.set_state(MakeOrder.name)

@user_router.message(MakeOrder.name, F.text)
async def get_name_for_reg(message:types.Message, state:FSMContext):
    await state.update_data(name=message.text)
    await message.answer('Введите место выдачи')
    await state.set_state(MakeOrder.place)

@user_router.message(MakeOrder.place, F.text)
async def get_place_for_reg(message:types.Message, state:FSMContext):
    await state.update_data(place=message.text)
    await message.answer('Укажите промокод')
    await state.set_state(MakeOrder.promocode)

@user_router.message(MakeOrder.promocode, F.text)
async def get_promocode_for_reg(message:types.Message, state:FSMContext):
    #sale = MakeOrder.promocodes.get(message.text, 0)
    await state.update_data(promocode=10)
    await message.answer('Укажите номер телефона')
    await state.set_state(MakeOrder.phone)

@user_router.message(MakeOrder.phone, F.text)
async def get_phone_for_reg(message:types.Message, state:FSMContext, session:AsyncSession):
    await state.update_data(phone = message.text)
    data = await state.get_data()
    carts = await orm_get_user_card(session=session, user_id=message.from_user.id)
    row = '\n- '.join([obj.product.name for obj in carts])
    try:
        await state.clear()
        await message.answer(f'Ваши данные ушли в обработку, вам перезвонят в течение некоторого времени\nCписок заказаных товаров:\n- {row}')
        n, pl, p = data['name'], data['place'], data['phone']
        await message.bot.send_message('YOUR CHAT.ID',f'Имя покупателя: {n}\nТочка выдачи: {pl}\nНомер телефона покупателя: {p}\n')
    except Exception as e:
        await state.clear()
        await message.answer('ok')