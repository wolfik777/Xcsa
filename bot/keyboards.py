"""
Keyboard layouts
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def get_main_menu() -> ReplyKeyboardMarkup:
    """Main menu keyboard"""
    builder = ReplyKeyboardBuilder()
    
    builder.row(
        KeyboardButton(text="📥 Скачать видео/музыку"),
        KeyboardButton(text="🛠 Инструменты")
    )
    builder.row(
        KeyboardButton(text="🎁 Реферальная программа"),
        KeyboardButton(text="📊 Моя статистика")
    )
    builder.row(
        KeyboardButton(text="🏆 Топ рефералов"),
        KeyboardButton(text="❓ Помощь")
    )
    
    return builder.as_markup(resize_keyboard=True)


def get_tools_menu() -> InlineKeyboardMarkup:
    """Tools menu keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🌐 Переводчик", callback_data="tool_translator"),
        InlineKeyboardButton(text="📊 QR-код", callback_data="tool_qr")
    )
    builder.row(
        InlineKeyboardButton(text="🔗 Сократить ссылку", callback_data="tool_shorturl"),
        InlineKeyboardButton(text="📝 Конвертер", callback_data="tool_converter")
    )
    builder.row(
        InlineKeyboardButton(text="🎨 Обработать фото", callback_data="tool_image"),
        InlineKeyboardButton(text="💱 Конвертер валют", callback_data="tool_currency")
    )
    builder.row(
        InlineKeyboardButton(text="🌤 Погода", callback_data="tool_weather")
    )
    builder.row(
        InlineKeyboardButton(text="« Назад", callback_data="back_main")
    )
    
    return builder.as_markup()


def get_download_format_keyboard(platform: str) -> InlineKeyboardMarkup:
    """Download format selection keyboard"""
    builder = InlineKeyboardBuilder()
    
    if platform == "youtube":
        builder.row(
            InlineKeyboardButton(text="🎵 Аудио MP3", callback_data="format_audio"),
            InlineKeyboardButton(text="📹 Видео HD", callback_data="format_video_hd")
        )
        builder.row(
            InlineKeyboardButton(text="📹 Видео SD", callback_data="format_video_sd"),
            InlineKeyboardButton(text="📹 Видео 4K", callback_data="format_video_4k")
        )
    else:
        builder.row(
            InlineKeyboardButton(text="📥 Скачать", callback_data="format_default")
        )
    
    builder.row(
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")
    )
    
    return builder.as_markup()


def get_share_button(referral_link: str) -> InlineKeyboardMarkup:
    """Share referral link button"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="📤 Поделиться ссылкой",
            url=f"https://t.me/share/url?url={referral_link}&text=Попробуй этого крутого бота!"
        )
    )
    
    return builder.as_markup()


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Cancel keyboard"""
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="❌ Отмена"))
    return builder.as_markup(resize_keyboard=True)

