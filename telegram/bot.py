
import os
import logging
import httpx
import time
from typing import Set
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
BACKEND_URL = os.environ.get('BACKEND_URL')
ALLOWED_USERS = os.environ.get('ALLOWED_USERS', '').split(',')

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required")
if not BACKEND_URL:
    raise ValueError("BACKEND_URL environment variable is required")

class TelegramBot:
    def __init__(self):
        self.application = Application.builder().token(BOT_TOKEN).build()
        self.allowed_users: Set[str] = {user.strip().lower() for user in ALLOWED_USERS if user.strip()}
        self.setup_handlers()
    
    def is_user_allowed(self, user) -> bool:
        if not user.username:
            return False
        return user.username.lower() in self.allowed_users
    
    def setup_handlers(self):
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self.is_user_allowed(update.effective_user):
            await update.message.reply_text("❌ У вас нет доступа к этому боту.")
            return
        await update.message.reply_text("👋 Отправьте сообщение для обработки.")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        
        if not self.is_user_allowed(user):
            await update.message.reply_text("❌ У вас нет доступа к этому боту.")
            return
        
        text = update.message.text
        
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                
                response = await client.get(BACKEND_URL, params={"text": text})
                response.raise_for_status()
                bot_response = response.json()
                
                await update.message.reply_text(bot_response)
                
        except Exception as e:
            logger.error(f"Exception occurred: {e}", exc_info=True)
            logger.error(f"  Type: {type(e).__name__}")
            logger.error(f"  Message: {str(e)}")
            logger.error(f"  Args: {e.args}")
            await update.message.reply_text("❌ Ошибка при обработке запроса.")
    
    def run(self):
        logger.info("Starting Telegram bot...")
        self.application.run_polling(drop_pending_updates=True)

def main():
    bot = TelegramBot()
    bot.run()

if __name__ == "__main__":
    main()
