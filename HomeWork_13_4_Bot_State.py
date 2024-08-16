import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

API_TOKEN = '--'

# Создаем экземпляр бота
bot = Bot(token=API_TOKEN)

# Создаем диспетчер с хранилищем состояний в памяти
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Определяем группу состояний
class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

# Функция, обрабатывающая команду /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply(
        'Привет! Я бот, помогающий твоему здоровью. Введите "Calories", чтобы начать расчет нормы калорий.')

# Функция для установки возраста
@dp.message_handler(lambda message: message.text.lower() == 'calories', state=None)
async def set_age(message: types.Message):
    await message.reply('Введите свой возраст:')
    await UserState.age.set()

# Функция для установки роста
@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.reply('Введите свой рост (в см):')
    await UserState.growth.set()

# Функция для установки веса
@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    await state.update_data(growth=message.text)
    await message.reply('Введите свой вес (в кг):')
    await UserState.weight.set()

# Функция для расчета и отправки нормы калорий
@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    await state.update_data(weight=message.text)

    data = await state.get_data()

    # Добавлена обработка ошибок для случая, если пользователь введет некорректные данные.
    try:
        age = int(data['age'])
        growth = int(data['growth'])
        weight = int(data['weight'])

        # Расчет по формуле Миффлина-Сан Жеора для мужчин
        calories = int(10 * weight + 6.25 * growth - 5 * age + 5)

        await message.reply(f"Ваша норма калорий: {calories} ккал в день")
    except ValueError:
        await message.reply("Ошибка в введенных данных. Пожалуйста, убедитесь, что вы ввели числовые значения.")

    await state.finish()

# Функция, обрабатывающая все остальные сообщения
@dp.message_handler()
async def all_messages(message: types.Message):
    await message.reply('Введите команду /start, чтобы начать общение или "Calories" для расчета нормы калорий.')


if __name__ == '__main__':
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)