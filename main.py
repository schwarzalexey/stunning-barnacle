import asyncio
import logging
import sys
import sqlite3
import random
import string
from os import getenv

from aiogram import Bot, Dispatcher, Router, types, F
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

d = {
    -1: 'Заблокирован',
    1: 'Заявка на рассмотрении',
    2: 'Воркер',
    3: 'Вбивер',
    4: 'Оператор',
    5: 'Наставник',
    6: 'Администратор'   
}

class CreateUser(StatesGroup):
    question1 = State()
    question2 = State()
    question3 = State()
    
class ChangeTag(StatesGroup):
    tag = State()

@router.message(CommandStart())
async def __start(message: Message, state: FSMContext) -> None:
    cursor.execute('SELECT status, tag FROM users WHERE uid = ?', (message.from_user.id,))
    result = cursor.fetchall()
    settings = InlineKeyboardButton(text='⚙️ Настройки', callback_data='settings')
    chats = InlineKeyboardButton(text='💬 Чаты', callback_data='chats')
    listings = InlineKeyboardButton(text='📂 Обьявления', callback_data='listings')
    admin_panel = InlineKeyboardButton(text='🖥 Админ-панель', callback_data='admin_panel')
    if result:
        if result[0][0] == -1:
            await message.answer('<b>❌ Вы заблокированы ❌</b>')
        elif result[0][0] == 0:
            btn = InlineKeyboardButton(text='go', callback_data='proceed')
            menu = InlineKeyboardMarkup(inline_keyboard=[[btn]])
            await message.answer('Добро пожаловать.\nПеред тем, как начать работать с нами, Вам нужно будет ответить на несколько вопросов. Вы готовы?',
                                 reply_markup=menu)
        elif result[0][0] == 1:
            await message.answer('Добро пожаловать. В данный момент, ваша заявка находится в обработке. Пожалуйста, ожидайте.')
        else:
            if result[0][0] == 6:
                menu = InlineKeyboardMarkup(inline_keyboard=[[listings], [settings], [chats], [admin_panel]])
            else:
                menu = InlineKeyboardMarkup(inline_keyboard=[[listings], [settings], [chats]])
            lists = cursor.execute('SELECT id from listings WHERE uid = ?', (message.from_user.id,)).fetchall()
            await message.answer(f'<b>💪🏻 СЛОВО ПАЦАНА GROUP\n\n#️⃣ Тэг: <code>#{result[0][1]}</code>\n📯 Статус: <code>{d[result[0][0]]}</code>\n📂 Объявлений: <code>{len(lists)}</code>\n💰 Сумма профитов: <code>TODO</code>\n📈 Количество профитов: <code>TODO</code>\n👨‍🏫 Наставник: TODO, ?%\n👨🏻 Оператор: TODO, ?%</b>',
                                 reply_markup=menu)
    else:
        cursor.execute('INSERT INTO users (uid, status, username, tag) VALUES (?, ?, ?, ?)', (message.from_user.id,
                                                                                              0,
                                                                                              message.from_user.username if message.from_user.username is not None else '',
                                                                                              ''.join(random.choice(string.ascii_letters) for i in range(8))))
        conn.commit()
        btn = InlineKeyboardButton(text='go', callback_data='proceed')
        menu = InlineKeyboardMarkup(inline_keyboard=[[btn]])
        await message.answer(
            '<b>Добро пожаловать.\nПеред тем, как начать работать с нами, Вам нужно будет ответить на несколько вопросов.\nВы готовы?</b>',
            reply_markup=menu)
        
@router.callback_query(lambda c: c.data == 'go_start')
async def __start_callback(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    cursor.execute('SELECT status, tag FROM users WHERE uid = ?', (callback_query.from_user.id,))
    result = cursor.fetchall()
    cid = callback_query.message.chat.id
    mid = callback_query.message.message_id
    settings = InlineKeyboardButton(text='⚙️ Настройки', callback_data='settings')
    chats = InlineKeyboardButton(text='💬 Чаты', callback_data='chats')
    listings = InlineKeyboardButton(text='📂 Обьявления', callback_data='listings')
    admin_panel = InlineKeyboardButton(text='🖥 Админ-панель', callback_data='admin_panel')
    if result:
        if result[0][0] == -1:
            await bot.edit_message_text('<b>❌ Вы заблокированы ❌</b>', cid, mid)
        elif result[0][0] == 0:
            btn = InlineKeyboardButton(text='go', callback_data='proceed')
            menu = InlineKeyboardMarkup(inline_keyboard=[[btn]])
            await bot.edit_message_text('<b>Добро пожаловать.\nПеред тем, как начать работать с нами, Вам нужно будет ответить на несколько вопросов.\nВы готовы?</b>', cid, mid,
                                 reply_markup=menu)
        elif result[0][0] == 1:
            await bot.edit_message_text('<b>Добро пожаловать. В данный момент, ваша заявка находится в обработке. Пожалуйста, ожидайте.</b>', cid, mid)
        else:
            if result[0][0] == 6:
                menu = InlineKeyboardMarkup(inline_keyboard=[[listings], [settings], [chats], [admin_panel]])
            else:
                menu = InlineKeyboardMarkup(inline_keyboard=[[listings], [settings], [chats]])
            lists = cursor.execute('SELECT id from listings WHERE uid = ?', (callback_query.from_user.id,)).fetchall()
            await bot.edit_message_text(f'<b>💪🏻 СЛОВО ПАЦАНА GROUP\n\n#️⃣ Тэг: <code>#{result[0][1]}</code>\n📯 Статус: <code>{d[result[0][0]]}</code>\n📂 Объявлений: <code>{len(lists)}</code>\n💰 Сумма профитов: <code>TODO</code>\n📈 Количество профитов: <code>TODO</code>\n👨‍🏫 Наставник: TODO, ?%\n👨🏻 Оператор: TODO, ?%</b>', cid, mid,
                                 reply_markup=menu)

@router.callback_query(lambda c: 'chats' in c.data)
async def __chatpanel(callback_query: types.CallbackQuery, state: FSMContext):
    chatwork = InlineKeyboardButton(text='Чат воркеров', url='https://t.me/+hxjypzMr3O9jZjQ0')
    chatprofit = InlineKeyboardButton(text='Канал выплат', url='https://t.me/+od_rBY99YwNiNTJk')
    markup = InlineKeyboardMarkup(inline_keyboard=[[chatwork, chatprofit]] + [[InlineKeyboardButton(text='⬅️Назад', callback_data='go_start')]])
    await bot.edit_message_text("<b>💬 Чаты</b>", callback_query.from_user.id, callback_query.message.message_id, reply_markup=markup)

@router.callback_query(lambda c: c.data == 'listings')
async def __listings(callback_query: types.CallbackQuery, state: FSMContext):
    cid = callback_query.message.chat.id
    mid = callback_query.message.message_id
    buttons = []
    listings = cursor.execute("select phishing_id, name, service from listings where uid=?", (callback_query.from_user.id,)).fetchall()
    for lst in listings:
        buttons.append([InlineKeyboardButton(text=(cursor.execute('select flag from services where service=?', (lst[2],)).fetchone()[0] + " | " + str(lst[1]) + " | " + str(lst[0])), callback_data=f'listing{lst[0]}')])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons + [[InlineKeyboardButton(text='⬅️Назад', callback_data='go_start')]])
    await bot.edit_message_text('''Ваши обьявления''', cid, mid, reply_markup=markup)
    await state.set_state(CreateUser.question1)

@router.callback_query(lambda c: c.data == 'proceed')
async def __proceed(callback_query: types.CallbackQuery, state: FSMContext):
    cid = callback_query.message.chat.id
    mid = callback_query.message.message_id
    await bot.edit_message_text('''В каких командах вы работали до этого?''', cid, mid)
    await state.set_state(CreateUser.question1)

@router.message(CreateUser.question1)
async def __q_1(message: types.Message, state: FSMContext):
    q_1 = message.text
    await state.update_data(q1=q_1)
    await message.answer('''Сколько у Вас было профитов?''')
    await state.set_state(CreateUser.question2)

@router.message(CreateUser.question2)
async def __q_2(message: types.Message, state: FSMContext):
    q_2 = message.text
    await state.update_data(q2=q_2)
    await message.answer('''От кого вы узнали о команде?''')
    await state.set_state(CreateUser.question3)

@router.message(CreateUser.question3)
async def __finalauthorization(message: types.Message, state: FSMContext):
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
    cursor.execute('UPDATE users SET status=2 WHERE uid=? ', (int(callback_query.data.replace('appr', '')),))
    conn.commit()
    await bot.send_message(int(callback_query.data.replace('appr', '')), "Заявка подтверждена. Напишите /start")
    await bot.edit_message_text(callback_query.message.text + "\nЗаявка подтверждена.", -4017721930, callback_query.message.message_id)
    
@router.callback_query(lambda c: 'decl' in c.data)
async def __decline(callback_query: types.CallbackQuery, state: FSMContext):
    cursor.execute('update users set status=-1 where uid=? ', (int(callback_query.data.replace('decl', '')),))
    conn.commit()
    await bot.send_message(int(callback_query.data.replace('decl', '')), "Заявка отклонена.")
    await bot.edit_message_text(callback_query.message.text + "\nЗаявка отклонена.", -4017721930, callback_query.message.message_id)
    
@router.callback_query(lambda c: 'admin_panel' in c.data)
async def __adminpanel(callback_query: types.CallbackQuery, state: FSMContext):
    cursor.execute('SELECT status FROM users WHERE uid = ?', (callback_query.from_user.id,))
    result = cursor.fetchall()
    if result[0][0] == 6:
        users = InlineKeyboardButton(text='Пользователи', callback_data='usrscheck0')
        markup = InlineKeyboardMarkup(inline_keyboard=[[users]] + [[InlineKeyboardButton(text='⬅️Назад', callback_data='go_start')]])
        await bot.edit_message_text("<b>🖥 Админ-панель</b>", callback_query.from_user.id, callback_query.message.message_id, reply_markup=markup)
    
@router.callback_query(lambda c: 'settings' in c.data)
async def __settpanel(callback_query: types.CallbackQuery, state: FSMContext):
    tag = InlineKeyboardButton(text='Изменить тэг', callback_data='tagchng')
    markup = InlineKeyboardMarkup(inline_keyboard=[[tag]] + [[InlineKeyboardButton(text='⬅️Назад', callback_data='go_start')]])
    await bot.edit_message_text("⚙️ Настройки", callback_query.from_user.id, callback_query.message.message_id, reply_markup=markup)

@router.callback_query(lambda c: 'tagchng' in c.data)
async def __settpanel(callback_query: types.CallbackQuery, state: FSMContext):
    tag = cursor.execute("select tag from users where uid=?", (callback_query.from_user.id,)).fetchone()[0]
    await bot.edit_message_text(f"Ваш текущий тэг: <code>#{tag}</code>\n\nВведите новый тэг:", callback_query.from_user.id, callback_query.message.message_id)
    await state.set_state(ChangeTag.tag)
    
@router.message(ChangeTag.tag, F.text.not_in(list(map(lambda x: x[0], cursor.execute("select tag from users").fetchall()))))
async def __tagsuccess(message: types.Message, state: FSMContext):
    cursor.execute("update users set tag=? where uid=?", (message.text, message.from_user.id))
    conn.commit()
    markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='⬅️Назад', callback_data='go_start')]])
    await bot.send_message(message.from_user.id, "Новый тэг успешно установлен.", reply_markup=markup)
    await state.clear()

@router.message(ChangeTag.tag)
async def __tagfailure(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id, "Такой тэг уже используется другим пользователем. Пожалуйста, введите другой тэг:")

@router.callback_query(lambda c: 'usrscheck' in c.data )
async def __adminpanel(callback_query: types.CallbackQuery, state: FSMContext):
    cursor.execute('SELECT status FROM users WHERE uid = ?', (callback_query.from_user.id,))
    result = cursor.fetchall()
    if result[0][0] == 6:
        users = cursor.execute('SELECT uid, status, username FROM users').fetchall()
        buttons = [list() for i in range(len(users))]
        i = 0
        for user in users:
            if user[1] != 0:
                if user[2] != '':
                    buttons[i // 3].append(InlineKeyboardButton(text=user[2], callback_data=f'user{user[0]}'))
                else:
                    buttons[i // 3].append(InlineKeyboardButton(text=str(user[0]), callback_data=f'user{user[0]}'))
                i += 1
        pages = []
        n_page = int(callback_query.data.replace("usrscheck", ''))
        for i in range(0, len(buttons), 10):
            pages.append(buttons[i: i + 10])
        arrows = [[InlineKeyboardButton(text=f'1 / 1', callback_data="ghjaczskdf")]] if len(pages) == 1 else [[InlineKeyboardButton(text=f'1 / {len(pages)}', callback_data="ghjaczskdf"), InlineKeyboardButton(text='->', callback_data="usrscheck1")]] if n_page == 0 else [[InlineKeyboardButton(text='<-', callback_data=f"usrscheck{len(pages) - 2}"), InlineKeyboardButton(text=f'{len(pages)} / {len(pages)}', callback_data="uazsxecdghijk")]] if n_page == len(pages) - 1 else [[InlineKeyboardButton(text='<-', callback_data=f"usrscheck{n_page - 1}"), InlineKeyboardButton(text=f'{n_page + 1} / {len(pages)}', callback_data="ghjaczskdf"), InlineKeyboardButton(text='->', callback_data=f"usrscheck{n_page + 1}")]]
        markup = InlineKeyboardMarkup(inline_keyboard=pages[n_page]+arrows+[[InlineKeyboardButton(text='⬅️Назад', callback_data='admin_panel')]])
        await bot.edit_message_text("Пользователи", callback_query.from_user.id, callback_query.message.message_id, reply_markup=markup)

@router.callback_query(lambda c: 'user' in c.data)
async def __userinfo(callback_query: types.CallbackQuery, state: FSMContext):
    cursor.execute('SELECT status FROM users WHERE uid = ?', (callback_query.from_user.id,))
    result = cursor.fetchall()
    if result[0][0] == 6:
        id = int(callback_query.data.replace("user", ''))
        buttons = [[InlineKeyboardButton(text='Обновить статус', callback_data=f'update{id}')],
                   [InlineKeyboardButton(text='Заблокировать пользователя', callback_data=f'block{id}')],
                   [InlineKeyboardButton(text='⬅️Назад', callback_data='usrscheck0')]]
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        dt = cursor.execute('SELECT id, status, tag FROM users WHERE uid = ?', (id,)).fetchone()

        await bot.edit_message_text(f'''Пользователь №{dt[0]}\n\nID: {id}\nСтатус пользователя: {d[dt[1]]}\nТег пользователя: <code>#{dt[2]}</code>''', callback_query.from_user.id, callback_query.message.message_id, reply_markup=markup)

@router.callback_query(lambda c: 'block' in c.data)
async def __blockuser(callback_query: types.CallbackQuery, state: FSMContext):
    cursor.execute('SELECT status FROM users WHERE uid = ?', (callback_query.from_user.id,))
    result = cursor.fetchall()
    if result[0][0] == 6:
        id = int(callback_query.data.replace("block", ''))
        buttons = [[InlineKeyboardButton(text='⬅️Назад', callback_data=f'user{id}')]]
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        cursor.execute('update users set status=-1 where uid=? ', (id,))
        conn.commit()
        await bot.send_message(id, "<b>❌ Вы заблокированы ❌</b>")
        await bot.edit_message_text(f'''Пользователь заблокирован''', callback_query.from_user.id, callback_query.message.message_id, reply_markup=markup)    
        
@router.callback_query(lambda c: 'update' in c.data)
async def __updateuser(callback_query: types.CallbackQuery, state: FSMContext):
    cursor.execute('SELECT status FROM users WHERE uid = ?', (callback_query.from_user.id,))
    result = cursor.fetchall()
    if result[0][0] == 6:
        id = int(callback_query.data.replace("update", ''))
        buttons = [[InlineKeyboardButton(text='Воркер', callback_data=f'__work{id}')],
                   [InlineKeyboardButton(text='Вбивер', callback_data=f'__vbv{id}')],
                   [InlineKeyboardButton(text='Оператор', callback_data=f'__opr{id}')],
                   [InlineKeyboardButton(text='Наставник', callback_data=f'__nast{id}')],
                   [InlineKeyboardButton(text='Администратор', callback_data=f'__adm{id}')],
                   [InlineKeyboardButton(text='⬅️Назад', callback_data=f'user{id}')]]
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        await bot.edit_message_text(f'''Выберите статус для пользователя ID: {id}''', callback_query.from_user.id, callback_query.message.message_id, reply_markup=markup)

@router.callback_query(lambda c: '__work' in c.data)
async def __workuser(callback_query: types.CallbackQuery, state: FSMContext):
    cursor.execute('SELECT status FROM users WHERE uid = ?', (callback_query.from_user.id,))
    result = cursor.fetchall()
    if result[0][0] == 6:
        id = int(callback_query.data.replace("__work", ''))
        buttons = [[InlineKeyboardButton(text='⬅️Назад', callback_data=f'user{id}')]]
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        cursor.execute('update users set status=2 where uid=? ', (id,))
        conn.commit()
        await bot.send_message(id, f"Ваш статус изменен на: {d[2]}")
        await bot.edit_message_text(f'''Статус успешно изменен''', callback_query.from_user.id, callback_query.message.message_id, reply_markup=markup)  
        
@router.callback_query(lambda c: '__vbv' in c.data)
async def __vbvuser(callback_query: types.CallbackQuery, state: FSMContext):
    cursor.execute('SELECT status FROM users WHERE uid = ?', (callback_query.from_user.id,))
    result = cursor.fetchall()
    if result[0][0] == 6:
        id = int(callback_query.data.replace("__vbv", ''))
        buttons = [[InlineKeyboardButton(text='⬅️Назад', callback_data=f'user{id}')]]
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        cursor.execute('update users set status=3 where uid=? ', (id,))
        conn.commit()
        await bot.send_message(id, f"Ваш статус изменен на: {d[3]}")
        await bot.edit_message_text(f'''Статус успешно изменен''', callback_query.from_user.id, callback_query.message.message_id, reply_markup=markup)  
        
@router.callback_query(lambda c: '__opr' in c.data)
async def __opruser(callback_query: types.CallbackQuery, state: FSMContext):
    cursor.execute('SELECT status FROM users WHERE uid = ?', (callback_query.from_user.id,))
    result = cursor.fetchall()
    if result[0][0] == 6:
        id = int(callback_query.data.replace("__opr", ''))
        buttons = [[InlineKeyboardButton(text='⬅️Назад', callback_data=f'user{id}')]]
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        cursor.execute('update users set status=4 where uid=? ', (id,))
        conn.commit()
        await bot.send_message(id, f"Ваш статус изменен на: {d[4]}")
        await bot.edit_message_text(f'''Статус успешно изменен''', callback_query.from_user.id, callback_query.message.message_id, reply_markup=markup)  
        
@router.callback_query(lambda c: '__nast' in c.data)
async def __nastuser(callback_query: types.CallbackQuery, state: FSMContext):
    cursor.execute('SELECT status FROM users WHERE uid = ?', (callback_query.from_user.id,))
    result = cursor.fetchall()
    if result[0][0] == 6:
        id = int(callback_query.data.replace("__nast", ''))
        buttons = [[InlineKeyboardButton(text='⬅️Назад', callback_data=f'user{id}')]]
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        cursor.execute('update users set status=5 where uid=? ', (id,))
        conn.commit()
        await bot.send_message(id, f"Ваш статус изменен на: {d[5]}")
        await bot.edit_message_text(f'''Статус успешно изменен''', callback_query.from_user.id, callback_query.message.message_id, reply_markup=markup)  

@router.callback_query(lambda c: '__adm' in c.data)
async def __admuser(callback_query: types.CallbackQuery, state: FSMContext):
    cursor.execute('SELECT status FROM users WHERE uid = ?', (callback_query.from_user.id,))
    result = cursor.fetchall()
    if result[0][0] == 6:
        id = int(callback_query.data.replace("__adm", ''))
        buttons = [[InlineKeyboardButton(text='⬅️Назад', callback_data=f'user{id}')]]
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        cursor.execute('update users set status=6 where uid=? ', (id,))
        conn.commit()
        await bot.send_message(id, f"Ваш статус изменен на: {d[6]}")
        await bot.edit_message_text(f'''Статус успешно изменен''', callback_query.from_user.id, callback_query.message.message_id, reply_markup=markup)  

async def main() -> None:
    global bot
    bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
    
#TODO 