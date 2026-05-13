import asyncio
import logging
from datetime import date
from telegram import Update
from telegram.ext import Application, ChatJoinRequestHandler, ContextTypes

# ===== НАСТРОЙКИ =====
BOT_TOKEN = "8923267714:AAFyUrBkxR_jFvuMOfPB7TIYwNpdsy_gQCU"   # Вставь свой токен
DELAY_SECONDS = 2 * 60          # 2 минуты
DAILY_LIMIT = 400               # Максимум одобрений в день
# =====================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Счётчик одобрений
counter = {
    "date": date.today(),
    "count": 0
}


def check_and_increment():
    """Проверяет лимит. Возвращает True если можно одобрить."""
    today = date.today()
    if counter["date"] != today:
        # Новый день — сбрасываем счётчик
        counter["date"] = today
        counter["count"] = 0

    if counter["count"] >= DAILY_LIMIT:
        return False

    counter["count"] += 1
    return True


async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    request = update.chat_join_request
    user = request.from_user
    chat_id = request.chat.id
    user_id = user.id

    # Фильтр: только аккаунты с юзернеймом
    if not user.username:
        logger.info(f"Отклонён (нет юзернейма): {user.full_name} | id: {user_id}")
        return

    # Проверка дневного лимита
    if not check_and_increment():
        logger.info(f"Лимит {DAILY_LIMIT} на сегодня исчерпан. @{user.username} ждёт ручного одобрения.")
        return

    logger.info(f"Запрос от @{user.username} | Одобрений сегодня: {counter['count']}/{DAILY_LIMIT}")

    # Ждём 2 минуты
    await asyncio.sleep(DELAY_SECONDS)

    try:
        await context.bot.approve_chat_join_request(
            chat_id=chat_id,
            user_id=user_id
        )
        logger.info(f"Одобрен: @{user.username}")
    except Exception as e:
        logger.error(f"Ошибка при одобрении @{user.username}: {e}")


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(ChatJoinRequestHandler(handle_join_request))

    logger.info("Бот запущен. Ожидаю запросы на вступление...")
    app.run_polling(allowed_updates=["chat_join_request"])


if __name__ == "__main__":
    main()
