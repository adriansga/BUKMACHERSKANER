import logging
import asyncio
from telegram import Bot
from config import settings

class Notifier:
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        self.bot = Bot(token=self.bot_token) if self.bot_token and "YOUR_TOKEN" not in self.bot_token else None

    async def send_alert(self, opp):
        """Wysyła alert o znalezieniu Value Bet."""
        if not self.bot:
            logging.info(f"Powiadomienie (Sim): {opp['game']} | {opp['outcome']} @ {opp['odds']} | EV: {opp['ev']}%")
            return

        message = (
            f"🚨 *VALUE BET FOUND!*\n\n"
            f"⚽ *Mecz:* {opp['game']}\n"
            f"📈 *Typ:* {opp['outcome']} @ {opp['odds']}\n"
            f"🏢 *Buk:* {opp['bookmaker']}\n"
            f"📊 *EV:* {opp['ev']}%\n"
            f"💰 *Kelly Stake:* {opp['kelly']}%"
        )
        
        try:
            await self.bot.send_message(chat_id=self.chat_id, text=message, parse_mode='Markdown')
        except Exception as e:
            logging.error(f"Błąd wysyłki Telegram: {str(e)}")
