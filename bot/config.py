"""
Bot Configuration
"""
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


@dataclass
class BotConfig:
    """Main bot configuration"""
    token: str
    admin_id: int
    
    # Database
    database_url: str
    redis_url: str
    
    # Referral System
    referral_bonus_count: int = 10
    premium_referral_count: int = 50
    
    # Rate Limiting
    max_downloads_per_day: int = 100
    max_file_size_mb: int = 100
    
    # Features
    enable_youtube: bool = True
    enable_tiktok: bool = True
    enable_instagram: bool = True
    enable_twitter: bool = True
    enable_premium: bool = True
    
    # Proxy для YouTube (формат: http://user:pass@ip:port)
    youtube_proxy: Optional[str] = None
    
    # Logging
    log_level: str = "INFO"
    
    # Webhook (опционально)
    webhook_host: Optional[str] = None
    webhook_path: Optional[str] = None
    webapp_host: str = "0.0.0.0"
    webapp_port: int = 8080


def load_config() -> BotConfig:
    """Load configuration from environment variables"""
    return BotConfig(
        token=os.getenv("BOT_TOKEN", ""),
        admin_id=int(os.getenv("ADMIN_ID", "0")),
        database_url=os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./bot.db"),
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        referral_bonus_count=int(os.getenv("REFERRAL_BONUS_COUNT", "10")),
        premium_referral_count=int(os.getenv("PREMIUM_REFERRAL_COUNT", "50")),
        max_downloads_per_day=int(os.getenv("MAX_DOWNLOADS_PER_DAY", "100")),
        max_file_size_mb=int(os.getenv("MAX_FILE_SIZE_MB", "100")),
        enable_youtube=os.getenv("ENABLE_YOUTUBE", "true").lower() == "true",
        enable_tiktok=os.getenv("ENABLE_TIKTOK", "true").lower() == "true",
        enable_instagram=os.getenv("ENABLE_INSTAGRAM", "true").lower() == "true",
        enable_twitter=os.getenv("ENABLE_TWITTER", "true").lower() == "true",
        enable_premium=os.getenv("ENABLE_PREMIUM", "true").lower() == "true",
        youtube_proxy=os.getenv("YOUTUBE_PROXY"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        webhook_host=os.getenv("WEBHOOK_HOST"),
        webhook_path=os.getenv("WEBHOOK_PATH"),
        webapp_host=os.getenv("WEBAPP_HOST", "0.0.0.0"),
        webapp_port=int(os.getenv("WEBAPP_PORT", "8080")),
    )


# Texts and messages
class Messages:
    """Bot messages in Russian"""
    
    START = """
👋 <b>Привет, {name}!</b>

Я многофункциональный бот-помощник! 

🎯 <b>Что я умею:</b>

📥 <b>Скачивание:</b>
• YouTube (видео/музыка)
• TikTok (без водяных знаков)
• Instagram (посты/stories/reels)
• Twitter/X
• Facebook
• VK (ВКонтакте)
• Rutube

🛠 <b>Инструменты:</b>
• Конвертер валют (реальные курсы!)
• Переводчик (выбор языка!)
• QR-коды
• Сокращение ссылок
• Wikipedia
• Калькулятор
• Погода
• Обработка изображений

🎁 <b>Реферальная программа:</b>
Приглашай друзей и получай бонусы!

Используй кнопки ниже или просто отправь мне ссылку! 👇
"""

    REFERRAL_INFO = """
🎁 <b>Реферальная программа</b>

👥 Ваших рефералов: <b>{count}</b>
🏆 Место в рейтинге: <b>#{position}</b>

🔗 <b>Ваша реферальная ссылка:</b>
<code>{link}</code>

<b>Награды:</b>
• {bonus_count} рефералов = Бонусные функции
• {premium_count} рефералов = Premium статус навсегда!

Поделись ссылкой с друзьями и получай награды! 🚀
"""

    DOWNLOADING = "⏳ Скачиваю... Пожалуйста, подожди."
    DOWNLOAD_ERROR = "❌ Ошибка при скачивании. Проверь ссылку и попробуй снова."
    UNSUPPORTED_LINK = "❌ Эта ссылка не поддерживается. Поддерживаемые: YouTube, TikTok, Instagram, Twitter/X, Facebook, VK, Rutube."
    FILE_TOO_LARGE = "❌ Файл слишком большой. Максимальный размер: {size} MB."
    RATE_LIMIT = "⏳ Превышен лимит загрузок на сегодня. Попробуй завтра или приглашай друзей для увеличения лимита!"
    
    STATS = """
📊 <b>Статистика бота</b>

👥 Всего пользователей: <b>{total_users}</b>
📈 Новых за сегодня: <b>{today_users}</b>
📥 Всего скачиваний: <b>{total_downloads}</b>
⚡ Скачиваний сегодня: <b>{today_downloads}</b>
"""

    LEADERBOARD = """
🏆 <b>Топ рефералов</b>

{leaderboard}

Пригласи друзей и попади в топ! 🚀
"""

    HELP = """
❓ <b>Помощь</b>

<b>Скачивание:</b>
Просто отправь ссылку на видео или пост.

<b>Инструменты:</b>
• 🌐 Переводчик - выбор языка перевода
• 📊 QR-код - генератор QR
• 🔗 Сократить ссылку - TinyURL
• 💱 Конвертер валют - реальные курсы
• 🎲 Генератор паролей - безопасные пароли
• 🔍 Wikipedia - быстрый поиск
• 🧮 Калькулятор - вычисления
• 📸 Сжать фото - уменьшение размера
• 🌤 Погода - прогноз для городов

<b>Команды:</b>
/start - Главное меню
/referral - Реферальная программа
/stats - Твоя статистика
/help - Помощь

<b>Скачивание с:</b>
• YouTube (видео/аудио) - работает из любой страны!
• TikTok (без водяных знаков)
• Instagram (посты/reels/stories)
• Twitter/X
• Facebook
• VK (ВКонтакте)
• Rutube

Есть вопросы? Напиши @admin
"""


config = load_config()
messages = Messages()

