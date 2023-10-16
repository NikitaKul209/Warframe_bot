from aiogram import types, F, Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import api_requests
import api_requests as requests

router = Router()


class OrderFissures(StatesGroup):
    choosing_mode = State()
    choosing_game_mode = State()

available_mode =["Стальной путь","Обычный режим"]
available_game_mode = ["Рейлджек","Обычный режим"]

def make_row_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    """
    Создаёт реплай-клавиатуру с кнопками в один ряд
    :param items: список текстов для кнопок
    :return: объект реплай-клавиатуры
    """
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)

@router.message(Command("start"))
async def start_handler(msg: Message):

    main_menu_buttons = ["Разрывы бездны",
                         "Циклы мира",
                         "Текущая награда стального пути",
                         "Товары Баро Китира",
                         "Найти предмет",
                         "Текущие ивенты",
                         "Арбитраж",
                         "Задания ночной волны",
                         "Новости"]

    builder = ReplyKeyboardBuilder()
    for i in range(len(main_menu_buttons)):
        builder.add(types.KeyboardButton(text=main_menu_buttons[i]))
    builder.adjust(2)
    await msg.answer(
         "Привет,я бот-помощник для игры Warframe",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )

@router.message(F.text ==  "Товары Баро Китира")
async def get_voidTrader(message: Message):
    answer = requests.get_voidTrader()
    for i in range(len(answer)):
        await message.answer(answer[i])

@router.message(F.text ==  "Текущая награда стального пути")
async def get_steel_path_reward(message: Message):
    answer = requests.get_steel_path_reward()
    await message.answer(answer)

@router.message(F.text ==  "Текущие ивенты")
async def get_events(message: Message):
    answer = api_requests.get_events()
    await message.answer(answer)

@router.message(F.text ==  "Арбитраж")
async def get_arbitration(message: Message):
    answer = api_requests.get_arbitration()
    await message.answer(answer)




@router.message(F.text ==  "Разрывы бездны")
async def get_fissures(message: Message, state: FSMContext):
    await message.answer("Выберите режим:",reply_markup=make_row_keyboard(["Cтальной путь","Обычный режим"]))
    await state.set_state(OrderFissures.choosing_mode)

@router.message(OrderFissures.choosing_mode,F.text.in_(available_mode))
async def choose_mode(message: Message, state: FSMContext):
    await state.update_data(chosen_mode=message.text)
    await message.answer(text="Выберите режим:",reply_markup=make_row_keyboard(available_game_mode))
    await state.set_state(OrderFissures.choosing_game_mode)

@router.message(OrderFissures.choosing_game_mode,F.text.in_(available_game_mode))
async def choose_game_mode(message: Message, state: FSMContext):
    user_data = await state.get_data()
    answer = api_requests.get_fissures(user_data["chosen_mode"],message.text)
    await message.answer(answer)
    await state.set_state(OrderFissures.choosing_mode)

