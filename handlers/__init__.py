from aiogram import Router
from . import common, servers, secondbot

def get_handlers_router():
    router = Router()
    router.include_router(common.router)
    router.include_router(servers.router)
    return router

def get_main_router():
    from aiogram import Router
    router = Router()
    router.include_router(common.router)
    router.include_router(servers.router)
    return router

def get_second_router():
    return secondbot.router