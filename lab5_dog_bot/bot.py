import logging
import requests
import os

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from config import TELEGRAM_TOKEN, DOG_API_KEY

# Убираем прокси-переменные окружения, чтобы requests ходил напрямую
for var in ["HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"]:
    os.environ.pop(var, None)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def get_random_dog_image():
    """
    Запрос к The Dog API, возвращает URL случайной картинки собаки.
    В случае ошибки возвращает None.
    """
    url = "https://api.thedogapi.com/v1/images/search"
    headers = {}
    if DOG_API_KEY:
        headers["x-api-key"] = DOG_API_KEY

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data and len(data) > 0:
            return data[0].get("url")
        else:
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при запросе к Dog API: {e}")
        return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! 🐶\n\n"
        "Я бот, который присылает случайные фотографии собак.\n"
        "Используй команду /pic, чтобы получить милую картинку!"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Доступные команды:\n"
        "/start — приветствие и описание бота\n"
        "/help — справка по командам\n"
        "/pic — получить случайную фотографию собаки"
    )


async def pic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ищу собачку... 🐕")

    image_url = get_random_dog_image()

    if image_url:
        await update.message.reply_photo(photo=image_url)
    else:
        await update.message.reply_text(
            "Не удалось получить картинку. 😢\n"
            "Попробуй позже или проверь соединение с интернетом."
        )


def main():
    print("main() стартовал")
    application = (
        Application
        .builder()
        .token(TELEGRAM_TOKEN)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("pic", pic))

    logger.info("Бот запущен...")
    application.run_polling()


if __name__ == "__main__":
    print("__name__ == '__main__', вызываем main()")
    main()