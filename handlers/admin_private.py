from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_makefunc_add import (
    orm_change_banner_image,
    orm_add_product,
    orm_get_all_products,
    orm_get_product,
    orm_update_product,
    orm_delete_product,
    orm_get_info_pages,
    orm_get_categories,
    )

from filters.chat_types import ChatFilterTypes, IsAdmin
from keyboard.reply_kb import build_kb
from keyboard.inline_kb import get_call_btns


admin_router = Router()
admin_router.message.filter(ChatFilterTypes(['private']), IsAdmin())

ADMIN_KB = build_kb(
    "Добавить товар",
    "Ассортимент",
     "Добавить/Изменить баннер",
    placeholder="Выберите действие",
    sizes=(2,))


class AddProduct(StatesGroup):
    name = State()
    description = State()
    category = State()
    price = State()
    prod_img = State()

    product_for_change = None

    text = {
        "AddProduct:name": "Введите название заново:",
        "AddProduct:description": "Введите описание заново:",
        "AddProduct:category": "Выберите категорию  заново ⬆️",
        "AddProduct:price": "Введите стоимость заново:",
        "AddProduct:image": "Этот стейт последний, поэтому...",
    }



@admin_router.message(Command('admin'))
async def start_admining(message:types.Message):
    await message.answer(text="Что хотите сделать?", reply_markup=ADMIN_KB)

@admin_router.message(F.text == 'Ассортимент')
async def nomoves(message:types.Message, session:AsyncSession):
    await message.answer("Ваш список товаров⬇️")
    cates = await orm_get_categories(session)
    btns = {category.name:f'category_{category.id}' for category in cates}
    await message.answer('Выберите категорию',reply_markup=get_call_btns(btns=btns))


@admin_router.callback_query(F.data.startswith('category_'))
async def nomoves(callback:types.CallbackQuery, session:AsyncSession):
    cat_id = callback.data.split('_')[-1]
    products = await orm_get_all_products(session, cat_id)
    for product in products:
        await callback.message.answer_photo(
            product.image,
            caption= f"<strong>{product.name}</strong>\n{product.description}\nСтоимость: {round(product.price, 2)}",
            reply_markup=get_call_btns(btns={
                'Удалить':f'delete_{product.id}',
                'Изменить':f'change_{product.id}',
            })
        )
    await callback.answer()
    await callback.message.answer("ОК, вот список товаров ⏫")

@admin_router.callback_query(StateFilter(None), F.data.startswith('change_'))
async def change_product_callback(callback:types.CallbackQuery, state:FSMContext, session:AsyncSession):
    await callback.answer()
    prod_id = int(callback.data.split('_')[-1])
    p_f_c = await orm_get_product(session, prod_id)
    AddProduct.product_for_change = p_f_c
    await callback.message.answer(
        "Введите название товара", reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddProduct.name)

@admin_router.callback_query(F.data.startswith('delete_'))
async def delete_product_from_bd(callback:types.CallbackQuery, session:AsyncSession):
    del_id = int(callback.data.split('_')[-1])
    await orm_delete_product(session, del_id)
    await callback.answer('Товар удалён')
    await callback.message.delete()



######################### FSM для дабавления/изменения товаров админом ###################

'''Код для машины состояний (FSM)'''



@admin_router.message(StateFilter(None),F.text == "Добавить товар")#проверяем есть ли активные соостояния и если пользователь ввёл добавить товар, то тогда запускается функция
async def add_product(message: types.Message, state:FSMContext):
    await message.answer(
        "Введите название товара")
    await state.set_state(AddProduct.name)#становимся в состояние ожидания ввода названия товара(AddProduct.name)

@admin_router.message(StateFilter('*'),Command('отмена'))# StateFilter('*') -> эта проверкак на то, что пользователь находиться в любом состоянии
@admin_router.message(StateFilter('*'),F.text.casefold() == 'отмена')
async def cancel_handler(message: types.Message, state:FSMContext) -> None:
    data = await state.get_data()# получаем все данные которые передал пользователь
    if data is None:# если не было получено никаких данных то игнорируем всё
        return
    if AddProduct.product_for_change:
        AddProduct.product_for_change = None
    await state.clear()#сбрасывает все состояния
    await message.answer('Все действия отменены', reply_markup=ADMIN_KB)

@admin_router.message(StateFilter("*"), Command("назад"))
@admin_router.message(StateFilter("*"), F.text.casefold() == "назад")
async def cancel_handler(message: types.Message, state:FSMContext) -> None:
    current_state = await state.get_state()
    if current_state == AddProduct.name:
        await message.answer('Вы не можете вернуться, введите название товара')
        return
    previous = None #переменная для прошлого состояния
    for step in AddProduct.__all_states__:#проходимся по всем состояниям которые присутствуют в классе
        if step == current_state:# если состояние равняется текущему, то мы устанавливаем прошлое состояние как текущее в строчке ниже
            await state.set_state(previous)# устанавливаем состояние, а после установки определенного состояния мы отправляемся в корректный хэндлер
            await message.answer(f"Вы вернулись к прошлому шагу\n{AddProduct.text[previous.state]}")#
            return 
        previous = step# передаём previous значение step

@admin_router.message(AddProduct.name, or_f(F.text, F.text.lower()=="пропустить"))#прописываем проверку на это состояние(которо указанов в хэндлере)
async def add_name(message: types.Message, state:FSMContext):
    if message.text.lower() == "пропустить" and AddProduct.product_for_change:
        await state.update_data(name = AddProduct.product_for_change.name)
    elif message.text == "Добавить товар":
        await message.answer("Вы ввели недопустимое значение. Введите название товара:")
        await state.set_state(AddProduct.name)
        return 
    else:
        await state.update_data(name=message.text)#записываем полученное название товара
    await message.answer("Введите описание товара")
    await state.set_state(AddProduct.description)#становимся в состояние ожидания ввода описания

"""Для некорректного ввода названия товара"""
@admin_router.message(AddProduct.name)
async def add_name(message: types.Message, state:FSMContext):
    await message.answer("Вы ввели недопустимое значение. Введите название товара:")

# Ловим данные для состояние description и потом меняем состояние на category
@admin_router.message(AddProduct.description, or_f(F.text, F.text.lower()=="пропустить"))
async def add_description(message: types.Message, state:FSMContext, session:AsyncSession):
    if message.text.lower()=="пропустить" and AddProduct.product_for_change:
        await state.update_data(description = AddProduct.product_for_change.description)
    elif message.text == "Добавить товар":
        await message.answer("Вы ввели недопустимое значение. Введите описание:")
        await state.set_state(AddProduct.name)
        return 
    else:
        await state.update_data(description=message.text)
    
    categories = await orm_get_categories(session)
    btns = {cat.name: str(cat.id) for cat in categories}
    await message.answer("Выберите категорию", reply_markup=get_call_btns(btns=btns))
    await state.set_state(AddProduct.category)

"""Для некорректного ввода описание"""
@admin_router.message(AddProduct.description)
async def add_description(message: types.Message, state:FSMContext):
    await message.answer("Вы ввели недопустимое значение. Введите описание:")

@admin_router.callback_query(AddProduct.category)
async def category_choice(callback:types.CallbackQuery, state:FSMContext, session:AsyncSession):
    if int(callback.data) in [int(cat.id) for cat in await orm_get_categories(session)]:
        await callback.answer()
        await state.update_data(category = callback.data)
        await callback.message.answer('Теперь введите цену товара.')
        await state.set_state(AddProduct.price)
    else:
        await callback.message.answer('Выберите катеорию из кнопок.')
        await callback.answer()

#Ловим любые некорректные действия, кроме нажатия на кнопку выбора категории
@admin_router.message(AddProduct.category)
async def category_choice2(message: types.Message, state: FSMContext):
    await message.answer("'Выберите катеорию из кнопок.'") 


@admin_router.message(AddProduct.price, or_f(F.text, F.text.lower()=="пропустить"))
async def add_price(message: types.Message, state:FSMContext):
    if message.text.lower()=="пропустить"and AddProduct.product_for_change:
        await state.update_data(price=AddProduct.product_for_change.price)
    else:
        try:
            float(message.text)
        except ValueError:
            await message.answer("Введите корректное значение цены")
            return
        
        await state.update_data(price=message.text)

    await message.answer("Загрузите изображение товара:")
    await state.set_state(AddProduct.prod_img)

"""Для некорректного ввода цены"""
@admin_router.message(AddProduct.price)
async def add_price(message: types.Message, state:FSMContext):
    await message.answer("Вы ввели недопустимое значение. Введите цену")


@admin_router.message(AddProduct.prod_img, or_f(F.photo, F.text.lower()=="пропустить"))
async def add_image(message: types.Message, state:FSMContext, session:AsyncSession):
    if message.text and message.text.lower()=="пропустить" and AddProduct.product_for_change:
        await state.update_data(prod_img=AddProduct.product_for_change.image)
    elif message.photo:
        await state.update_data(prod_img=message.photo[-1].file_id)
    else:
        await message.answer("Отправьте фото пищи")
        return
    data = await state.get_data()#получаем все данные которые получили за время работы машины состояний
    try:   
        if AddProduct.product_for_change:
            await orm_update_product(session, AddProduct.product_for_change.id, data)
            await message.answer("Товар изменен", reply_markup=ADMIN_KB)
        else:     
            await orm_add_product(session, data)
            await message.answer("Товар добавлен", reply_markup=ADMIN_KB)
        await state.clear() #очищаем машину состояний
    except Exception as e:
        print(e)
        await message.answer(f"Ошибка:{str(e)}\n", reply_markup=ADMIN_KB)
        await state.clear()

    AddProduct.product_for_change = None

"""Для некорректного ввода фото"""
@admin_router.message(AddProduct.prod_img)
async def add_price(message: types.Message, state:FSMContext):
    await message.answer("Вы ввели недопустимое значение. Загрузите изображение товара")




################# Микро FSM для загрузки/изменения баннеров ############################

class AddBanner(StatesGroup):
    banner = State()

@admin_router.message(F.text == 'Добавить/Изменить баннер', StateFilter(None))
async def add_image_banner(message:types.Message, state:FSMContext, session:AsyncSession):
    pages_names = [page.name for page in await orm_get_info_pages(session)]
    await message.answer(f"Отправьте фото баннера.\nВ описании укажите для какой страницы:\
                         \n{', '.join(pages_names)}")
    await state.set_state(AddBanner.banner)


@admin_router.message(AddBanner.banner, F.photo)
async def add_banner(message:types.Message, state:FSMContext, session:AsyncSession):
    image_for_banner = message.photo[-1].file_id
    for_page = message.caption.strip()#получаем описаные под фото
    pages_names = [page.name for page in await orm_get_info_pages(session)]
    if for_page not in pages_names:
        await message.answer(f"Введите нормальное название страницы, например:\
                         \n{', '.join(pages_names)}")
        return 
    await orm_change_banner_image(session, for_page, image_for_banner)
    await message.answer("Баннер добавлен/изменен.")
    await state.clear()

# ловим некоррекный ввод
@admin_router.message(AddBanner.banner)
async def not_valid_banner(message:types.Message, state:FSMContext):
    await message.answer("Отправьте фото баннера или отмена", reply_markup=get_call_btns(btns={'Отмена':'Отмена'}))

@admin_router.callback_query(AddBanner.banner, F.data == 'Отмена')
async def break_add_banner(callback:types.CallbackQuery, state:FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.answer('Ok', reply_markup=ADMIN_KB)
#########################################################################################