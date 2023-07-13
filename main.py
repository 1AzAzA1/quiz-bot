from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData

from config import TOKEN
from cats import get_cat_info
from questions import questions
import random

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=MemoryStorage())


# приветствие
@dp.message_handler(commands=['start'], state='*')
async def start_messeng(message: types.Message, state: FSMContext):
    await message.answer("Добро пожаловать в Квиз бот! Напиши /quiz чтобы начать.")


# музон под рожу
@dp.message_handler(commands=['muzon_pod_roju'], state='*')
async def cmd_image(message: types.Message):
    with open('muson.mp4', 'rb') as video:
        await message.answer_video(video)


# котики
@dp.message_handler(commands=['cat'], state="*")
async def cat(message: types.Message):
    cat_url = await get_cat_info()
    await message.answer_photo(photo=cat_url)


# задаётся кол-во вопросов
@dp.message_handler(commands=['quiz'], state="*")
async def count_questions(message: types.Message, state: FSMContext):
    await message.answer(f"Напиши, квиз из скольки вопросов ты хочешь.(max {len(questions)})")
    await state.set_state("checking")


# проверяется -- число ли это
@dp.message_handler(state="checking")
async def checking_for_number(message: types.Message, state: FSMContext):
    try:
        quiz_size = int(message.text)
        user_questions = []
        question_bank = questions.copy()

        for i in range(quiz_size):
            if not question_bank:
                break
            random_question = random.choice(question_bank)
            question_bank.remove(random_question)
            user_questions.append(random_question)

        await state.update_data(questions=user_questions, counter=0, corrects=0)
        await state.set_state("answering")
        await show_question(message, state)

    except ValueError:
        await message.answer("Это не число")


quiz_callback = CallbackData("quiz", "number")


async def show_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    questions = data["questions"]
    counter = data["counter"]  # то, на каком именно вопросе пользователь находится
    current_question = questions[counter]
    keyboard = types.InlineKeyboardMarkup()
    variants = current_question.get("variants")
    if variants is not None:
        for i, variant in enumerate(current_question["variants"]):
            button = types.InlineKeyboardButton(text=variant, callback_data=quiz_callback.new(number=i))
            keyboard.add(button)
        await message.answer(text=current_question["question"], reply_markup=keyboard)
    else:
        await message.answer(text=current_question["question"])


@dp.callback_query_handler(quiz_callback.filter(), state="answering")
async def answer_question(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await bot.answer_callback_query(call.id)
    data = await state.get_data()
    counter = data["counter"]  # то, на каком именно вопросе пользователь находится
    current_questions = data["questions"]

    current_question = current_questions[counter]
    correct_answer = current_question["answer"]
    corrects = data["corrects"]

    chosen_variant_id = int(callback_data.get("number"))
    chosen_variant = current_question["variants"][chosen_variant_id]
    await bot.send_message(call.from_user.id, f'Вы нажали кнопку "{chosen_variant}"')

    if chosen_variant == correct_answer:
        await call.message.answer("Правильный ответ!")
        corrects += 1
        await state.update_data(corrects=corrects)
    else:
        await call.message.answer(f"Неправильный ответ... Правильным был {correct_answer}")

    counter += 1

    if counter >= len(current_questions):
        await call.message.answer(f"Ты молодец, ты ответил на {corrects} вопросов из {len(current_questions)}")
        await state.finish()
        return

    await state.update_data(counter=counter)
    await show_question(call.message, state)


@dp.message_handler(state="answering")
async def answer_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    counter = data["counter"]  # то, на каком именно вопросе пользователь находится
    current_questions = data["questions"]

    current_question = current_questions[counter]
    correct_answer = current_question["answer"]
    corrects = data["corrects"]
    chosen_variant = message.text
    await bot.send_message(message.from_user.id, f'Вы ввели "{chosen_variant}"')

    if chosen_variant.lower() == correct_answer.lower():
        await message.answer("Правильный ответ!")
        corrects += 1
        await state.update_data(corrects=corrects)
    else:
        await message.answer(f"Неправильный ответ... Правильным был {correct_answer}")

    counter += 1

    if counter >= len(current_questions):
        await message.answer(f"Ты молодец, ты ответил на {corrects} вопросов из {len(current_questions)}")
        await state.finish()
        return

    await state.update_data(counter=counter)
    await show_question(message, state)


executor.start_polling(dp, skip_updates=True)

#    data = await state.get_data()
#    counter = data["counter"]
#    text = f"Кнопка нажата {counter} раз"


# эхо бот
# @dp.message_handler()
# async def eho_message(message: types.Message):
#    await message.answer(message.text)
