# ИМПОРТ
from highload import reg
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import keyboard
import sqlite3, asyncio, os

#БОТ
bot = Bot(token=os.environ.get('TOKEN'), parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())
admin = os.environ.get('ADMIN')
conn = sqlite3.connect('users.db'); cur = conn.cursor()
sskeys = sqlite3.connect('users.db'); sskey = conn.cursor()
codes = ["1"]
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

@dp.message_handler(state=["admin","Allow"], commands="start")
async def startAllow(message: types.Message):
    await message.reply("Привет! Пользуйся ботом спокойно 🥳", reply_markup=keyboard.kb)


@dp.message_handler(state='code')
async def Allow(message: types.Message):
    if message.text in codes:
        cur.execute(f"""INSERT INTO users(userid) 
           VALUES({message.from_user.id});""")
        conn.commit()
        codes.remove(message.text)
        await message.reply("Теперь ты можешь спокойно пользоваться ботом 🥳", reply_markup=keyboard.kb)
        state = dp.current_state(user=message.from_user.id)
        await state.set_state("Allow")
        return
    await message.reply("Нет такого кода😖")


@dp.message_handler(state='wait')
async def wait(message: types.Message):
    pass


@dp.message_handler(state=["admin","Allow"], text=["Получить прокси ⚡"])
async def get(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await state.set_state("wait")
    await message.reply("Получаем прокси, подожди😉")
    adr, passw, ss = await reg()
    with open("keys.txt", "a") as file:
        file.write(f"\n{ss}")
    await message.reply(f"""Прокси получено✅

Ключик: <pre>{ss}</pre> 🛡

Логин: <pre>{adr}</pre> 👤
Пароль: <pre>{passw}</pre> 🔐 
Панель: https://hi-l.eu/auth ⚙
    """)

    await bot.send_message(admin, f"""<b>Пользователь взял ключ!</b>
    
ID: <b>{message.from_user.id}</b>
NAME: <b>{message.from_user.full_name}</b>
USERNAME: @{message.from_user.username}

Ключ: <pre>{ss}</pre>
""")

    if message.from_user.id != admin:
        await state.set_state("Allow")
        return
    await state.set_state("admin")


@dp.message_handler(state='admin', commands="addcode")
async def addcode(message: types.Message):
    argument = message.get_args()
    if argument != "":
        codes.append(argument)
        await message.reply(f"Код <pre>{argument}</pre> добавлен 🔐")
        return

    await message.reply("Ну ты код-то введи")


@dp.message_handler(state='admin', commands="keys")
async def keys(message: types.Message):
    await message.answer_document(open("keys.txt", "rb"))

@dp.message_handler(state='*', commands="start")
async def start(message: types.Message):
    await message.reply("Привет! Бот приватный, по этому введи код, который ты мог получить у админа.")
    state = dp.current_state(user=message.from_user.id)
    await state.set_state("code")


# ЗАПУСК
async def main():
    # Запуск бота
    cur.execute("""CREATE TABLE IF NOT EXISTS users(
       userid INT PRIMARY KEY);
    """)
    conn.commit()

    cur.execute("SELECT * FROM users;")
    users = cur.fetchone()
    if users != None:
        for i in users:
            state = dp.current_state(user=i)
            await state.set_state("Allow")

    #state = dp.current_state(user=admin)
    #await state.set_state("admin")

if __name__ == "__main__":
    ioloop = asyncio.get_event_loop()
    ioloop.run_until_complete(main())
    executor.start_polling(dp, skip_updates=True)
