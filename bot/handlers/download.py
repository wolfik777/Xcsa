"""
Download handlers
"""
import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import messages, config
from ..keyboards import get_main_menu, get_download_format_keyboard
from ..utils.url_parser import URLParser
from ..services.downloader import Downloader, DownloadError
from ..database.crud import UserCRUD, DownloadCRUD

router = Router()
downloader = Downloader()


class DownloadStates(StatesGroup):
    """Download states"""
    waiting_url = State()
    waiting_format = State()


@router.message(F.text == "📥 Скачать видео/музыку")
async def download_start(message: Message, state: FSMContext):
    """Start download process"""
    await state.set_state(DownloadStates.waiting_url)
    await message.answer(
        "📎 <b>Отправь мне ссылку</b> на видео или пост:\n\n"
        "Поддерживаемые платформы:\n"
        "• YouTube\n"
        "• TikTok\n"
        "• Instagram\n"
        "• Twitter/X\n"
        "• Facebook",
        reply_markup=get_main_menu()
    )


@router.message(DownloadStates.waiting_url)
async def process_url(message: Message, state: FSMContext, session: AsyncSession):
    """Process URL for download"""
    # Check if user wants to cancel
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("❌ Отменено", reply_markup=get_main_menu())
        return
    
    # Check if it's a menu button
    if message.text in ["📥 Скачать видео/музыку", "🛠 Инструменты", "🎁 Реферальная программа",
                        "📊 Моя статистика", "🏆 Топ рефералов", "❓ Помощь"]:
        await state.clear()
        return
    
    url = message.text.strip()
    
    # Check if it's a valid URL
    if not URLParser.is_valid_url(url):
        await message.answer(
            "❌ Это не похоже на ссылку. Попробуй еще раз.",
            reply_markup=get_main_menu()
        )
        return
    
    # Detect platform
    platform, clean_url = URLParser.parse_url(url)
    
    if not platform:
        await message.answer(messages.UNSUPPORTED_LINK, reply_markup=get_main_menu())
        return
    
    # Check if platform is enabled
    platform_enabled = {
        "youtube": config.enable_youtube,
        "tiktok": config.enable_tiktok,
        "instagram": config.enable_instagram,
        "twitter": config.enable_twitter,
        "facebook": True,  # Always enabled
    }
    
    if not platform_enabled.get(platform, False):
        await message.answer(
            f"❌ Скачивание с {platform.title()} временно недоступно.",
            reply_markup=get_main_menu()
        )
        return
    
    # Check rate limit
    user = await UserCRUD.get_by_id(session, message.from_user.id)
    if user and not user.is_premium:
        downloads_today = await DownloadCRUD.get_user_downloads_today(session, message.from_user.id)
        if downloads_today >= config.max_downloads_per_day:
            await message.answer(
                messages.RATE_LIMIT.format(size=config.max_file_size_mb),
                reply_markup=get_main_menu()
            )
            return
    
    # Save URL to state
    await state.update_data(url=clean_url, platform=platform)
    
    # Show format selection for YouTube
    if platform == "youtube":
        await state.set_state(DownloadStates.waiting_format)
        await message.answer(
            "🎯 <b>Выбери формат:</b>",
            reply_markup=get_download_format_keyboard(platform)
        )
    else:
        # Download directly for other platforms
        await start_download(message, state, session, "default")


@router.callback_query(F.data.startswith("format_"))
async def select_format(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Handle format selection"""
    format_type = callback.data.replace("format_", "")
    
    if format_type == "cancel":
        await state.clear()
        await callback.message.delete()
        await callback.message.answer("❌ Отменено", reply_markup=get_main_menu())
        await callback.answer()
        return
    
    await callback.answer()
    await callback.message.delete()
    await start_download(callback.message, state, session, format_type)


async def start_download(message: Message, state: FSMContext, session: AsyncSession, format_type: str):
    """Start downloading file"""
    data = await state.get_data()
    url = data.get("url")
    platform = data.get("platform")
    
    if not url or not platform:
        await message.answer("❌ Ошибка. Попробуй еще раз.", reply_markup=get_main_menu())
        await state.clear()
        return
    
    # Send downloading message
    status_msg = await message.answer(messages.DOWNLOADING)
    
    try:
        # Download file
        result = await downloader.download(
            url=url,
            platform=platform,
            format_type=format_type,
            user_id=message.from_user.id
        )
        
        file_path = result["file_path"]
        file_size = result["file_size"]
        title = result["title"]
        
        # Check file size
        max_size = config.max_file_size_mb * 1024 * 1024
        if file_size > max_size:
            await status_msg.edit_text(
                messages.FILE_TOO_LARGE.format(size=config.max_file_size_mb)
            )
            downloader.cleanup_file(file_path)
            await state.clear()
            return
        
        # Send file
        file = FSInputFile(file_path, filename=f"{title[:50]}.{file_path.split('.')[-1]}")
        
        # Determine file type
        ext = file_path.split(".")[-1].lower()
        if ext in ["mp3", "m4a", "wav", "ogg"]:
            await message.answer_audio(file, caption=f"🎵 {title}")
        elif ext in ["mp4", "avi", "mov", "mkv"]:
            await message.answer_video(file, caption=f"📹 {title}")
        else:
            await message.answer_document(file, caption=f"📎 {title}")
        
        # Delete status message
        await status_msg.delete()
        
        # Save to database
        await DownloadCRUD.create(
            session=session,
            user_id=message.from_user.id,
            platform=platform,
            url=url,
            file_type=ext,
            file_size=file_size,
            success=True
        )
        
        # Update user stats
        await UserCRUD.increment_downloads(session, message.from_user.id)
        
        # Cleanup file
        downloader.cleanup_file(file_path)
        
    except DownloadError as e:
        await status_msg.edit_text(f"{messages.DOWNLOAD_ERROR}\n\n<i>{str(e)}</i>")
        
        # Save error to database
        await DownloadCRUD.create(
            session=session,
            user_id=message.from_user.id,
            platform=platform,
            url=url,
            file_type="unknown",
            success=False,
            error_message=str(e)
        )
    
    except Exception as e:
        await status_msg.edit_text(f"{messages.DOWNLOAD_ERROR}\n\n<i>Неизвестная ошибка</i>")
    
    finally:
        await state.clear()

