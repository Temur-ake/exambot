import asyncio
import logging
import os
import sys
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from dotenv import load_dotenv
from redis_dict import RedisDict

load_dotenv()

TOKEN = os.getenv('TOKEN')
ADMIN_ID = 6067978806,

database = RedisDict('user')

dp = Dispatcher()


class States(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_message = State()


async def send_greeting(message: types.Message):
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    registration_time = datetime.now().strftime("%Y-%m-%d, %H:%M")
    database[str(user_id)] = {"full_name": user_full_name, "registration_time": registration_time}
    await message.answer(f'Salom {user_full_name}')


async def send_message_to_user(user_id, message_text, bot: Bot):
    user_data = database.get(str(user_id))
    if user_data:
        await bot.send_message(user_id, message_text)
        return "Xabar foydalanuvchiga yetkazildi."
    else:
        return "Bunday IDli foydalanuvchi topilmadi."


@dp.message(Command(commands=['start']))
async def command_start(message: types.Message):
    await send_greeting(message)


@dp.message(Command(commands="send"))
async def command_send(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in ADMIN_ID:
        await message.answer("Foydalanuvchi ID-ni kiriting:")
        await message.bot.send_chat_action(message.chat.id, "typing")
        await state.set_state(States.waiting_for_user_id)
    else:
        await message.answer("Sizda ruxsat yo'q!")


@dp.message(States.waiting_for_user_id)
async def process_user_id(message: types.Message, state: FSMContext):
    user_id = message.text
    if user_id.isdigit():
        await state.update_data(user_id=user_id)
        await message.answer("Xabarni kiriting:")
        await state.set_state(States.waiting_for_message)
    else:
        await message.answer('Noto`g`ri ID formati. Foydalanuvchi ID-ni raqam shaklida kiriting.')


@dp.message(States.waiting_for_message)
async def process_message(message: types.Message, state: FSMContext, bot: Bot):
    user_data = await state.get_data()
    user_id = user_data.get("user_id")
    response = await send_message_to_user(user_id, message.text, bot=bot)
    await message.answer(response)
    await state.clear()


@dp.message(Command(commands="stat"))
async def command_stat(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in ADMIN_ID:
        await message.answer("Foydalanuvchi ID-ni kiriting:")
        await state.set_state(States.waiting_for_user_id)
    else:
        await message.answer("Sizda ruxsat yo'q!")


@dp.message(States.waiting_for_user_id)
async def process_user_id_for_stat(message: types.Message, state: FSMContext):
    user_id = message.text
    user_data = database.get(user_id)
    if user_data:
        registration_time = user_data.get("registration_time")
        await message.answer(f"{user_id} li foydalanuvchi {registration_time} kuni ro`yxatdan o`tgan.")
    else:
        await message.answer("Bunday IDli foydalanuvchi topilmadi.")
    await state.finish()


@dp.message()
async def echo_message(message: types.Message):
    await message.answer(message.text)


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
