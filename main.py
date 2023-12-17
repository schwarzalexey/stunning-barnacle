import asyncio
import logging
import sys
import sqlite3
from os import getenv

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.types.user import User
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.formatting import TextMention

TOKEN = "6724959545:AAGEAZ9dXte-HIVUY_IQKPj406dPJKswm3Y"
conn = sqlite3.connect("db/db.db3")
cursor = conn.cursor()
router = Router()

class CreateUser(StatesGroup):
    question1 = State()
    question2 = State()
    question3 = State()

@router.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    cursor.execute('SELECT status FROM users WHERE uid = ?', (message.from_user.id,))
    result = cursor.fetchall()
    if result:
        if result[0][0] == -1:
            await message.answer('Вы заблокированы в этом боте.')
        elif result[0][0] == 0:
            btn = InlineKeyboardButton(text='go', callback_data='proceed')
            menu = InlineKeyboardMarkup(inline_keyboard=[[btn]])
            await message.answer('Добро пожаловать.\nПеред тем, как начать работать с нами, Вам нужно будет ответить на несколько вопросов.\    Вы готовы?',
                                 reply_markup=menu)
        elif result[0][0] == 1:
            await message.answer('Добро пожаловать. В данный момент, ваша заявка находится в обработке. Пожалуйста, ожидайте.')
        else:
            await message.answer('Добро пожаловать. ')
    else:
        cursor.execute('INSERT INTO users (uid, status) VALUES (?, ?)', (message.from_user.id, 0))
        
        btn = InlineKeyboardButton(text='go', callback_data='proceed')
        menu = InlineKeyboardMarkup(inline_keyboard=[[btn]])
        await message.answer(
            'Добро пожаловать.\nПеред тем, как начать работать с нами, Вам нужно будет ответить на несколько вопросов.\nВы готовы?',
            reply_markup=menu)

@router.callback_query(lambda c: c.data == 'proceed')
async def proceed(callback_query: types.CallbackQuery, state: FSMContext):
    cid = callback_query.message.chat.id
    mid = callback_query.message.message_id
    await bot.edit_message_text('''В каких командах вы работали до этого?''', cid, mid)
    await state.set_state(CreateUser.question1)

@router.message(CreateUser.question1)
async def q_1(message: types.Message, state: FSMContext):
    q_1 = message.text
    await state.update_data(q1=q_1)
    await message.answer('''Сколько у Вас было профитов?''')
    await state.set_state(CreateUser.question2)

@router.message(CreateUser.question2)
async def q_2(message: types.Message, state: FSMContext):
    q_2 = message.text
    await state.update_data(q2=q_2)
    await message.answer('''От кого вы узнали о команде?''')
    await state.set_state(CreateUser.question3)

@router.message(CreateUser.question3)
async def finalauthorization(message: types.Message, state: FSMContext):
    q_3 = message.text
    await state.update_data(q3=q_3)
    user_data = await state.get_data()
    cursor.execute('update users set status=1 where uid=? ', (message.from_user.id,))
    conn.commit()
    approve = InlineKeyboardButton(text='можно', callback_data=f'appr{message.from_user.id}')
    decline = InlineKeyboardButton(text='не можно', callback_data=f'decl{message.from_user.id}')
    menu = InlineKeyboardMarkup(inline_keyboard=[[approve, decline]])
    await message.answer('''Готово! Ваша заявка отправлена на рассмотрение администрации. Пожалуйста, ожидайте.''')
    await bot.send_message(-4017721930,
                           f'''У вас новая заявка:\nПользователь: [{message.from_user.username if message.from_user.username is not None else "id" + str(message.from_user.id)}](tg://user?id={message.from_user.id})\nВ каких командах вы работали до этого?: {user_data['q1']}\nСколько у Вас было профитов?: {user_data['q2']}\nОт кого вы узнали о команде?: {user_data['q3']}\n''',
                           reply_markup=menu,
                           parse_mode=ParseMode.MARKDOWN_V2)
    await state.clear()

@router.callback_query(lambda c: 'appr' in c.data)
async def __approve(callback_query: types.CallbackQuery, state: FSMContext):
    cursor.execute('update users set status=2 where uid=? ', (int(callback_query.data.replace('appr', '')),))
    await bot.send_message(int(callback_query.data.replace('appr', '')), "Заявка подтверждена.")
    await bot.edit_message_text(callback_query.message.text + "\nЗаявка подтверждена.", -4017721930, callback_query.message.message_id)
    
@router.callback_query(lambda c: 'decl' in c.data)
async def __decline(callback_query: types.CallbackQuery, state: FSMContext):
    cursor.execute('update users set status=-1 where uid=? ', (int(callback_query.data.replace('decl', '')),))
    await bot.send_message(int(callback_query.data.replace('decl', '')), "Заявка отклонена.")
    await bot.edit_message_text(callback_query.message.text + "\nЗаявка отклонена.", -4017721930, callback_query.message.message_id)
    
async def main() -> None:
    global bot
    bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())