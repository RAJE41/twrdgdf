# ИМПОРТ
from highload import reg
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import keyboard
import sqlite3, asyncio, os

#БОТ
bot = Bot(token=os.environ.get('TOKEN'), parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())

admin = int(os.environ.get('ADMIN'))
allowed = [int(i) for i in os.environ.get('ids').split(",")]

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


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


@dp.message_handler(state='admin', commands="keys")
async def keys(message: types.Message):
    await message.answer_document(open("keys.txt", "rb"))

@dp.message_handler(state=['Allow', 'admin'], commands="start")
async def start(message: types.Message):
    await message.reply("Привет! Можешь брать прокси в этом боте бесплатно 😎", reply_markup=keyboard.kb)


# ЗАПУСК
async def main():
    # Запуск бота
    if allowed != []:
        for i in allowed:
            state = dp.current_state(user=i)
            await state.set_state("Allow")

    state = dp.current_state(user=admin)
    await state.set_state("admin")

if __name__ == "__main__":
    ioloop = asyncio.get_event_loop()
    ioloop.run_until_complete(main())
    executor.start_polling(dp, skip_updates=True)
