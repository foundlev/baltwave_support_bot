import aiogram
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


BOT_TOKEN: str = "<BOT TOKEN>"
# ID операторов.
ADMINS: tuple[int] = tuple()

bot = aiogram.Bot(token=BOT_TOKEN)
dp = aiogram.Dispatcher(bot)


class Storage:
    def __init__(self):
        self.i = {}


db = Storage()


def get_another_admin(admin_id) -> int:
    if ADMINS[0] == admin_id:
        return ADMINS[1]
    return ADMINS[0]


def get_keyboard(form_user_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text="📝 Ответить", callback_data=f"answer_{form_user_id}"))
    return kb


@dp.message_handler(commands=["start"])
async def start_message(message: aiogram.types.Message):
    user_id = message.chat.id

    if user_id in ADMINS:
        text = "Бот работает. Ожидаю вопросов от пользователей."
    else:
        text = ("<b>Здравствуйте, это Техническая Поддержка бота Волна Балтики.</b>\n"
                "Если у вас есть вопросы, опишите их одним сообщением и отправьте Боту. "
                "Если необходимо, прикрепите скриншот или видеозапись экрана.")
    await message.answer(text, parse_mode="html")


@dp.message_handler(content_types=['text', 'audio', 'document', 'animation', 'photo', 'sticker', 'video',
                                   'video_note', 'voice'])
async def text_message(message: aiogram.types.Message):
    user_id = message.chat.id
    username = message.chat.username
    if username:
        username = "@" + username
    else:
        username = "-"

    if user_id in ADMINS:
        other_id = db.i.get(user_id)
        if other_id:
            db.i[user_id] = False
            await message.copy_to(other_id)

            for admin_id in ADMINS:
                text = (f"☑️ Был дан ответ пользователю <code>{other_id}</code>\n\n"
                        f"Текст ответа:")
                await bot.send_message(admin_id, text, parse_mode="html")
                await message.forward(admin_id)

        else:
            await message.answer("❌ Ошибка - вы не выбрали пользователя для ответа")

    else:
        text = ("✉️ <b>Новое сообщение</b>\n"
                f"ID: <code>{user_id}</code>\n"
                f"Username: {username}\n\n"
                f"Сообщение:")
        try:
            for admin_id in ADMINS:
                await bot.send_message(admin_id, text, parse_mode="html", reply_markup=get_keyboard(user_id))
                await message.forward(admin_id)
        except:
            await message.answer("❌ Ошибка - невозможно отправить данное сообщение")
        else:
            await message.answer("☑️ Ваш вопрос отправлен. Постараемся ответить в ближайшее время.")


@dp.callback_query_handler()
async def inline_message(call: aiogram.types.CallbackQuery):
    user_id = call.message.chat.id
    if user_id in ADMINS:
        other_id = int(call.data.replace("answer_", ""))
        db.i[user_id] = other_id
        text = (f"📝 Отправьте текст ответа для пользователя <code>{other_id}</code>.\n"
                f"Можете использовать медиа для более подробного описания.")
        await call.message.answer(text, parse_mode="html")


async def start_msg(_):
    text = "Бот запущен"
    for admin_id in ADMINS:
        await bot.send_message(admin_id, text)


async def stop_msg(_):
    text = "Бот остановлен"
    for admin_id in ADMINS:
        await bot.send_message(admin_id, text)


if __name__ == "__main__":
    aiogram.executor.start_polling(dp, on_startup=start_msg, on_shutdown=stop_msg)
