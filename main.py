import asyncio
import logging
import sys
import sqlite3
from os import getenv

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.markdown import hbold

TOKEN = "6724959545:AAGEAZ9dXte-HIVUY_IQKPj406dPJKswm3Y"
conn = sqlite3.connect("db/db.db3")
cursor = conn.cursor()
dp = Dispatcher()



@dp.message(CommandStart())
async def start(message: Message) -> None:
    cursor.execute('SELECT status FROM users WHERE uid = ?', (message.from_user.id,))
    result = cursor.fetchall()
    if result:
        if result[0][0] == -1:
            await message.answer('Вы заблокированы в этом боте.')
        elif result[0][0] == 0:
            btn = InlineKeyboardButton(text='go', callback_data='proceed')
            menu = InlineKeyboardMarkup(inline_keyboard=[[btn]])
            await message.answer('Добро пожаловать.\nПеред тем, как начать работать с нами, Вам нужно будет ответить на несколько вопросов.\nВы готовы?',
                                 reply_markup=menu)
        else:
            await message.answer('Добро пожаловать.')
    else:
        cursor.execute('INSERT INTO users (uid, status) VALUES (?, ?)', (message.from_user.id, 0))
        btn = InlineKeyboardButton(text='go', callback_data='proceed')
        menu = InlineKeyboardMarkup(inline_keyboard=[[btn]])
        await message.answer(
            'Добро пожаловать.\nПеред тем, как начать работать с нами, Вам нужно будет ответить на несколько вопросов.\nВы готовы?',
            reply_markup=menu)


@dp.message()
async def echo_handler(message: types.Message) -> None:
    try:
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        await message.answer("Nice try!")


async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())