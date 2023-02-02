from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import (
    Bot, 
    Dispatcher, 
    executor, 
    types
    )
from aiogram.utils.markdown import hspoiler
from aiogram.dispatcher import FSMContext
import logging
import sqlite3
import random



API_TOKEN = '6115546071:AAGJMN-iArl2H0UstzhyXzRo5_Yb5WuOQ28'
ADMINS = [979834772]

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

connection = sqlite3.connect('fc.db')
cursor = connection.cursor()

# Create database

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS words(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_en TEXT NOT NULL,
    word_ru TEXT NOT NULL,
    word_id INTEGER REFERENCES words_info(id)
    );
    """
    )

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS words_info(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    lesson TEXT
    );
    """
    )
# cursor.execute(
#     """
#     INSERT INTO words_info(title, lesson) VALUES ('PAST SIMPLE', '35');
#     """
#     )

# cursor.execute(
#     """
#     INSERT INTO words(word_en, word_ru, word_id) VALUES ('PRESENT SIMPLE', 'Прошлое1 сложное', 1);
#     """
#     )
connection.commit()

# End create database

# Keyboards

# Buttons
btn_main_menu = [
    InlineKeyboardButton('🧠 Начать тренировку 🧠', callback_data='app_choice_card'),
    InlineKeyboardButton('👀 Показать все карточки 👀', callback_data='get_all_cards'),
    InlineKeyboardButton('⚙ Настройки ⚙', callback_data='add_lesson'),
]

btn_state_exit = [
    InlineKeyboardButton('❌ Отмена', callback_data='state_exit'),
]

btn_tarin_go = [
    InlineKeyboardButton('Начнем?', callback_data='app_start_card'),
    InlineKeyboardButton('❌ Отмена', callback_data='state_exit'),
]

btn_tarin_end = [
    InlineKeyboardButton('Готово 🏁', callback_data='app_train_pagination_en'),
]

btn_train_next_en = [
    InlineKeyboardButton('❌ Отмена', callback_data='state_exit'),
    InlineKeyboardButton('Далее 🔜', callback_data='app_train_pagination_en'),
]

btn_train_next_ru = [
    InlineKeyboardButton('❌ Отмена', callback_data='state_exit'),
    InlineKeyboardButton('Далее 🔜', callback_data='app_train_pagination_ru'),
]

btn_select_lang = [
    InlineKeyboardButton('🇺🇸 (ENG) -> (RUS) 🇷🇺', callback_data='entoru'),
    InlineKeyboardButton('🇷🇺 (RUS) -> (ENG)🇺🇸', callback_data='rutoen'),
    InlineKeyboardButton('❌ Отмена', callback_data='state_exit'),
]


# Keyboard
kb_main_menu = InlineKeyboardMarkup(row_width=1).add(*btn_main_menu)
kb_state_exit = InlineKeyboardMarkup(row_width=1).add(*btn_state_exit)
kb_train_pagination_exstart = InlineKeyboardMarkup(row_width=1).add(*btn_tarin_go)
kb_train_pagination_exend = InlineKeyboardMarkup(row_width=1).add(*btn_tarin_end)
kb_train_pagination_en = InlineKeyboardMarkup(row_width=2).add(*btn_train_next_en)
kb_train_pagination_ru = InlineKeyboardMarkup(row_width=2).add(*btn_train_next_ru)
kb_select_lang = InlineKeyboardMarkup(row_width=2).add(*btn_select_lang)

# FSMachine
class FSMChoiceThemeAll(StatesGroup):
    theme = State()

class FSMChoiceThemeSingle(StatesGroup):
    theme = State()

class FSMCardPagination(StatesGroup):
    card = State()

# Body
@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    user_name = message.from_user.username
    await message.answer(
        text=f'Привет, {user_name}, давай начнем', 
        reply_markup=kb_main_menu
        )
    
# 🧠 Начать тренировку 🧠
# 👀 Показать все карточки 👀
@dp.callback_query_handler(lambda c: c.data in ['app_choice_card', 'get_all_cards'])
async def get_callback_cards(callback: types.CallbackQuery):
    query = cursor.execute(f'SELECT * FROM words_info;')
    connection.commit()
    data = ''
    for i in query:
        data += f'{i[0]}: {i[1]} ({i[2]} урок)\n'
    await callback.message.edit_text(text=f'Отправьте ID урока\n\n{data}', reply_markup=kb_state_exit)
    if callback.data == 'app_choice_card':
        await FSMChoiceThemeSingle.theme.set()
    elif callback.data == 'get_all_cards':
        await FSMChoiceThemeAll.theme.set()


# 👀 Показать все карточки 👀
@dp.message_handler(state=FSMChoiceThemeAll.theme)
async def get_cards(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        id = message.text
        query = cursor.execute(f"SELECT * FROM words WHERE word_id = {id};")
        connection.commit()
        data = ''
        for i in query:
            data += f'{i[1]} - {i[2]}\n'
        await message.answer(f'{data}', reply_markup=kb_main_menu)
        await state.finish()
    else:
        await message.answer("Введите положительное число...", reply_markup=kb_state_exit)

# 🧠 Начать тренировку 🧠
@dp.message_handler(state=FSMChoiceThemeSingle.theme)
async def get_card(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        id = message.text
        query = cursor.execute(f"SELECT * FROM words WHERE word_id = {id};")
        await state.finish()
        connection.commit()
        await FSMCardPagination.card.set()
        async with state.proxy() as data:
            data['card_array'] = [i for i in query]
            data['count'] = 0
            data['ex_count'] = 0
            random.shuffle(data['card_array'])
            await message.answer(f"Всего надо пройти {len(data['card_array'])} карточек, удачи!", reply_markup=kb_select_lang)
    else:
        await message.answer("Введите положительное число...", reply_markup=kb_state_exit)

@dp.callback_query_handler(lambda c: c.data in ['entoru', 'rutoen', 'app_train_pagination_ru', 'app_train_pagination_en'], state=FSMCardPagination.card)
async def callback_point(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if len(data['card_array']) != data['count']:
            mess = data['card_array']
            len_mess = len(mess)
            cnt = data['count']
            if callback.data in ['entoru', 'app_train_pagination_en']:
                hidden_text = hspoiler(f'{mess[cnt][2]}')
                await callback.message.answer(
                        text=f'{cnt+1}/{len_mess}: {mess[cnt][1]} - {hidden_text}', 
                        reply_markup=kb_train_pagination_exend if len(data['card_array']) ==  data['count'] + 1 else kb_train_pagination_en
                        )
                await callback.message.delete()
                data['count'] += 1  
            elif callback.data in ['rutoen', 'app_train_pagination_ru']:
                hidden_text = hspoiler(f'{mess[cnt][1]}')
                await callback.message.answer(
                        text=f'{cnt+1}/{len_mess}: {mess[cnt][2]} - {hidden_text}', 
                        reply_markup=kb_train_pagination_exend if len(data['card_array']) ==  data['count'] + 1 else kb_train_pagination_ru
                        )
                await callback.message.delete()
                data['count'] += 1

        else:
            await callback.message.edit_text(text=f"Что будем делать дальше?", reply_markup=kb_main_menu)
            await state.finish()



# Конец состояния
@dp.callback_query_handler(state='*')
async def cancel_state(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await callback.message.edit_text(text='Что будем делать дальше?', reply_markup=kb_main_menu)

# End body

# Final settings
async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "Запустить бота"),
            types.BotCommand("help", "Вывести справку"),
        ]
    )

async def on_startup_notify(dp: Dispatcher):
    for admin in ADMINS:
        try:
            await dp.bot.send_message(admin, "The Bot starting...")

        except Exception as err:
            logging.exception(err)

async def on_startup(dispatcher):
    # Устанавливаем дефолтные команды
    await set_default_commands(dispatcher)

    # Уведомляет про запуск
    await on_startup_notify(dispatcher)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)