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
from aiogram.dispatcher import FSMContext

TOKEN = "6724959545:AAGEAZ9dXte-HIVUY_IQKPj406dPJKswm3Y"
conn = sqlite3.connect("db/db.db3")
cursor = conn.cursor()
dp = Dispatcher()

class CreateUser(StatesGroup):
    question1 = State()
    question2 = State()
    question3 = State()

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

@dp.callback_query_handler(lambda c: c.data == 'proceed')
async def proceed(callback_query: types.CallbackQuery):
    cid = callback_query.message.chat.id
    mid = callback_query.message.message_id
    await bot.edit_message_text('''В каких командах вы работали до этого?''', cid, mid)
    await CreateUser.question1.set()

@dp.message_handler(state=CreateUser.question1)
async def q_1(message: types.Message, state: FSMContext):
    q_1 = message.text
    cursor.execute("UPDATE forms SET q1=? WHERE uid=?", (q_1, message.from_user.id))
    await message.answer('''Сколько у Вас было профитов?''')
    await CreateUser.question2.set()

@dp.message_handler(state=CreateUser.question2)
async def q_2(message: types.Message, state: FSMContext):
    q_2 = message.text
    cursor.execute("UPDATE forms SET q2=? WHERE uid=?", (q_2, message.from_user.id))
    await message.answer('''От кого вы узнали о команде?''')
    await CreateUser.question3.set()

@dp.message_handler(state=CreateUser.question3)
async def finalauthorization(message: types.Message, state: FSMContext):
    q_3 = message.text
    cursor.execute("UPDATE forms SET q3=? WHERE uid=?", (q_3, message.from_user.id))
    await state.finish()
    
@dp.message_handler(state=CreateUser.question1)
async def entrgolds(message: types.Message, state: FSMContext):
    num = message.text
    
    await state.finish()

@dp.message()
async def echo_handler(message: types.Message) -> None:
    try:
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        await message.answer("Nice try!")


async def main() -> None:
    global bot
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())