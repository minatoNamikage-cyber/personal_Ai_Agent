import os
from chat_history import init_db,save_message
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters
)

from chatbot import chat


load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

init_db()


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_input = update.message.text

    user_id = update.effective_user.id
    conversation_id = str(user_id)

    # User message save
    save_message(
        user_id,
        conversation_id,
        "user",
        user_input
    )

    # Eran response
    response = await chat(
        user_input,
        user_id,
        conversation_id)

    result = response["result"]

    # Assistant response save
    save_message(
        user_id,
        conversation_id,
        "assistant",
        result
    )

    # Telegram response
    await update.message.reply_text(result)

def main():

    app = Application.builder().token(TOKEN).build()

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    print("Eran Telegram Bot started...")

    app.run_polling()


if __name__ == "__main__":
    main()