from math import ceil

from sqlalchemy.orm import joinedload
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Product, Category, User, Cart, Banner


        ############################ Категории ######################################


async def orm_get_categories(session:AsyncSession):
    query = select(Category)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_create_categories(session:AsyncSession, categories:list):
    query = select(Category)
    res = await session.execute(query)
    if res.first():
        return 
    session.add_all([Category(name=cat) for cat in categories])
    await session.commit()



        ############ Админка: добавить/изменить/удалить товар ########################
"""ДОБАВЛЕНИЕ ТОВАРА В ТАБЛИЦУ"""
async def orm_add_product(session:AsyncSession, data:dict):
    obj = Product(name = data['name'],
        description = data['description'],
        price = float(data['price']),
        image = data['prod_img'],
        category_id = int(data['category']))
    session.add(obj)       #формируем параметры продукта
    await session.commit()

"""ПОЛУЧЕНИЕ ВСЕХ ПРОДУКТОВ ИЗ ТАБЛИЦЫ"""
async def orm_get_all_products(session:AsyncSession, category_id):
    query = select(Product).where(Product.category_id == int(category_id)) # формируем запрос, что все данные будут потребованы из нашей таблицы
    result = await session.execute(query) # отправляем запрос и получаем все данные с таблицы
    return result.scalars().all() #форматируем данные, чтобы они имели допустимый вид

"""ПОЛУЧЕНИЕ ОПРЕДЕЛЕННОГО ТОВАРА ИЗ ТАБЛИЦЫ"""
async def orm_get_product(session:AsyncSession, product_id:int):
    query = select(Product).where(Product.id == product_id) #указываем что нам нужны все данные товар с данным id и  
    result = await session.execute(query)
    return result.scalar()

"""ФОРМАТИРОВАНИЕ ТОВАРА"""
async def orm_update_product(session:AsyncSession, prod_id:int, data:dict):
    query = update(Product).where(Product.id == prod_id).values(    # указываем что будем обновлять товар по id и менять данные на новые
        name = data['name'],
        description = data['description'],
        price = float(data['price']),
        image = data['prod_img'],
        category_id = int(data['category'])
    )
    await session.execute(query) #отправляем запрос на изменение данных
    await session.commit() #сохраняем изменения

"""УДАЛЕНИЕ ТОВАРА"""
async def orm_delete_product(session:AsyncSession, prod_id:int):
    query = delete(Product).where(Product.id == prod_id) # указываем что будем удалять товар с определенным id
    await session.execute(query)#отправляем запрос
    await session.commit()#сохраняем изменения


        ##################### Добавляем юзера в БД #####################################


async def orm_add_user(session:AsyncSession,
                       user_id:int,
                       first_name:str|None = None,
                       last_name:str|None = None,
                       phone:str|None = None
                       ):
    query = select(User).where(User.user_id == user_id)
    result = await session.execute(query)
    if result.first() is None:
        obj = User(user_id=user_id, first_name=first_name, last_name=last_name, phone=phone) 
        session.add(obj)
        await session.commit()


        ######################## Работа с корзинами #######################################


async def orm_add_to_cart(session:AsyncSession, user_id:int, product_id:int):
    query = select(Cart).where(Cart.product_id == product_id, Cart.user_id == user_id).options(joinedload(Cart.product))
    cart = await session.execute(query)
    cart = cart.scalar()
    if cart:
        cart.quantity += 1
        await session.commit()
        return cart
    else:
        obj = Cart(user_id=user_id, product_id=product_id, quantity=1)
        session.add(obj)
        await session.commit()


async def orm_get_user_card(session:AsyncSession, user_id):
    query = select(Cart).where(Cart.user_id == user_id).options(joinedload(Cart.product))
    result = await session.execute(query)
    return result.scalars().all()


async def orm_delete_from_cart(session:AsyncSession, user_id, product_id):
    query = delete(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id)
    await session.execute(query)
    await session.commit()


async def orm_reduce_product_in_cart(session:AsyncSession, user_id:int, product_id:int):
    query = select(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id)
    result = await session.execute(query)
    cart = result.scalar()

    if not cart: 
        return 
    
    if cart.quantity>1:
        cart.quantity -= 1
        await session.commit()
        return True
    else:
        await orm_delete_from_cart(session, user_id, product_id)
        await session.commit()
        return False
    

        ############### Работа с баннерами (информационными страницами) ###############


async def orm_add_banner_description(session:AsyncSession, data:dict):
    #Добавляем новый или изменяем существующий по именам
    #пунктов меню: main, about, cart, shipping, payment, catalog
    query = select(Banner)
    result = await session.execute(query)

    if result.first():
        return 
    obj = [Banner(name = n, description = d) for n, d in data.items()]
    session.add_all(obj)
    await session.commit()


async def orm_change_banner_image(session: AsyncSession, name: str, image: str):
    query = update(Banner).where(Banner.name == name).values(image=image)
    await session.execute(query)
    await session.commit()


async def orm_get_banner(session: AsyncSession, page: str):
    query = select(Banner).where(Banner.name == page)
    result = await session.execute(query)
    return result.scalar()


async def orm_get_info_pages(session: AsyncSession):
    query = select(Banner)
    result = await session.execute(query)
    return result.scalars().all()
