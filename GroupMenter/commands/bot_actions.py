"""
Здесь работа с конкретным ботом
"""
from aiogram import types
from aiogram.utils.exceptions import TelegramAPIError, Unauthorized
from GroupMenter.models.models import Bot
from server.server import unregister_token


async def delete_bot(bot: Bot, call: types.CallbackQuery):
    """
    Пользователь решил удалить бота
    """
    try:
        await unregister_token(bot.decrypted_token())
    except Unauthorized:
        # Вероятно пользователь сбросил токен или удалил бот, это уже не наши проблемы
        pass
    await bot.delete()
    await call.answer("Бот удалён")
    try:
        await call.message.delete()
    except TelegramAPIError:
        pass


async def reset_bot_text(bot: Bot, call: types.CallbackQuery):
    """
    Пользователь решил сбросить текст бота к default
    :param bot:
    :param call:
    :return:
    """
    bot.start_text = bot._meta.fields_map['start_text'].default
    await bot.save()
    await call.answer("Текст сброшен")


async def reset_bot_second_text(bot: Bot, call: types.CallbackQuery):
    """
    Пользователь решил сбросить second text бота
    :param bot:
    :param call:
    :return:
    """
    bot.second_text = bot._meta.fields_map['second_text'].default
    await bot.save()
    await call.answer("Текст сброшен")


async def select_chat(bot: Bot, call: types.CallbackQuery, chat: str):
    """
    Пользователь выбрал чат, в который хочет получать сообщения от бота
    :param bot:
    :param call:
    :param chat:
    :return:
    """
    if chat == "personal":
        bot.group_chat = None
        await bot.save()
        await call.answer("Выбран личный чат")
        return

    chat_obj = await bot.group_chats.filter(id=chat).first()
    if not chat_obj:
        await call.answer("Нельзя привязать бота к этому чату")
        return
    bot.group_chat = chat_obj
    await bot.save()
    await call.answer(f"Выбран чат {chat_obj.name}")
