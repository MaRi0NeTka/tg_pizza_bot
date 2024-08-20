from sqlalchemy.ext.asyncio import AsyncSession

from aiogram.types import InputMediaPhoto

from utils.paginator import Paginator
from database.orm_makefunc_add import orm_get_banner, orm_get_user_card, orm_get_categories, orm_get_all_products, orm_add_to_cart, orm_delete_from_cart, orm_reduce_product_in_cart
from keyboard.inline_kb import get_user_main_btns, get_user_categories, get_products_btns, get_cart_btns




async def main_menu(session:AsyncSession,
                    level,
                    menu_name):
    banner= await orm_get_banner(session, menu_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)

    kbrd = get_user_main_btns(level=level)
    return image, kbrd

async def catalog(session:AsyncSession, level:int, menu_name:str):
    categ = await orm_get_categories(session)
    banner= await orm_get_banner(session, menu_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)
    kbrd = get_user_categories(level=level, categories=categ)
    return image, kbrd

def btns_for_pagin(paginator:Paginator):
    btns= dict()
    if paginator.has_previous():
        btns["◀ Пред."] = "previous"
    if paginator.has_next():
        btns["След. ▶"] = 'next'
    return btns


async def products(session, level, category, page):
    products = await orm_get_all_products(session, category_id=category)
    paginator = Paginator(products, page=page)
    product = paginator.get_page()[0]
    image = InputMediaPhoto(
        media=product.image,
        caption=f"<strong>{product.name}\
                </strong>\n{product.description}\nСтоимость: {round(product.price, 2)}\n\
                <strong>Товар {paginator.page} из {paginator.pages}</strong>",
    )
    pag_buttons = btns_for_pagin(paginator)
    kbrd = get_products_btns(
        level=level,
        category=category,
        page=page,
        pagination_btns=pag_buttons,
        product_id=product.id
    )
    return image, kbrd

async def user_buy_cart(session, level, menu_name, page, user_id, product_id):
    if menu_name == 'delete':
        await orm_delete_from_cart(session=session, user_id=user_id, product_id=product_id)
        if page>1:
            page -=1
    elif menu_name == 'increment':
        await orm_add_to_cart(session=session, user_id=user_id, product_id=product_id)
    elif menu_name == 'decrement':
        is_cart = await orm_reduce_product_in_cart(session=session, user_id=user_id,product_id=product_id)
        if page > 1 and not is_cart:
            page-=1
    
    carts = await orm_get_user_card(session, user_id)
    if not carts:
        image = await orm_get_banner(session, 'cart')
        image = InputMediaPhoto(media=image.image, caption=image.description)
        kb = get_cart_btns(
            level=level,
            page=None,
            pagination_btns=None,
            product_id=None
        )
        return image, kb
    else:
        paginator = Paginator(carts, page=page)
        pagin_btns = btns_for_pagin(paginator)
        cart = paginator.get_page()[0]
        cart_price = round(cart.quantity * cart.product.price, 2)
        total_sum = round(sum(cart.quantity * cart.product.price for cart in carts),2)
        image = InputMediaPhoto(
            media=cart.product.image,
            caption=f"<strong>{cart.product.name}</strong>\n{round(cart.product.price,2)}$ x {cart.quantity} = {cart_price}$\
                    \nТовар {paginator.page} из {paginator.pages} в корзине.\nОбщая стоимость товаров в корзине {total_sum}",
        )

        kb = get_cart_btns(
            level = level,
            page = page,
            pagination_btns=pagin_btns,
            product_id=cart.product.id
        )
        return image, kb


async def get_menu_content(
        session:AsyncSession,
        level:int,
        menu_name:str,
        category:int|None = None,
        page:int|None = None,
        user_id:int|None = None,
        product_id:int|None = None
):
    if level == 0:
        return await main_menu(session,level,menu_name)
    elif level == 1:
        return await catalog(session, level,menu_name)
    elif level == 2:
        return await products(session, level, category, page)
    elif level == 3:
        return await user_buy_cart(session, level, menu_name, page, user_id, product_id)