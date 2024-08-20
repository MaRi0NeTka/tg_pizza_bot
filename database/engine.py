"""Здесь будет происходить запуск самого движка, то есть ORM системы"""
import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database.models import Base
from database.orm_makefunc_add import orm_create_categories, orm_add_banner_description

from common.text_for_db import categories, description_for_info_pages

engine = create_async_engine(os.getenv('DB_LITE'), echo=True)# echo для того чтобы приходили действия в терминал

session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)#expire_on_commit делаем False чтобы после комита она сразу не закрывалась

async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_maker() as session:
        await orm_create_categories(session, categories)
        await orm_add_banner_description(session, description_for_info_pages)

async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)