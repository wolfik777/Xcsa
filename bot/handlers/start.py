"""
Start command and main menu handlers
"""
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import messages
from ..keyboards import get_main_menu, get_tools_menu
from ..database.crud import UserCRUD, StatsCRUD

router = Router()


@router.message(CommandStart(deep_link=True))
async def start_with_referral(message: Message, session: AsyncSession):
    """Handle /start command with referral code"""
    # Extract referral code from deep link
    args = message.text.split(maxsplit=1)
    referral_code = args[1] if len(args) > 1 else None
    
    # Get or create user
    user, is_new = await UserCRUD.get_or_create(
        session=session,
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        referrer_code=referral_code if is_new else None
    )
    
    # Send welcome message
    text = messages.START.format(name=message.from_user.first_name)
    
    if is_new and referral_code:
        text += "\n\n🎉 <b>Вы присоединились по реферальной ссылке!</b>\nВаш друг получил бонус!"
    
    await message.answer(text, reply_markup=get_main_menu())


@router.message(CommandStart())
async def start_command(message: Message, session: AsyncSession):
    """Handle /start command"""
    # Get or create user
    await UserCRUD.get_or_create(
        session=session,
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    
    # Send welcome message
    text = messages.START.format(name=message.from_user.first_name)
    await message.answer(text, reply_markup=get_main_menu())


@router.message(Command("help"))
@router.message(F.text == "❓ Помощь")
async def help_command(message: Message):
    """Handle help command"""
    await message.answer(messages.HELP, reply_markup=get_main_menu())


@router.message(F.text == "🛠 Инструменты")
async def tools_menu(message: Message):
    """Show tools menu"""
    await message.answer(
        "🛠 <b>Выберите инструмент:</b>",
        reply_markup=get_tools_menu()
    )


@router.message(Command("stats"))
@router.message(F.text == "📊 Моя статистика")
async def user_stats(message: Message, session: AsyncSession):
    """Show user statistics"""
    user = await UserCRUD.get_by_id(session, message.from_user.id)
    
    if not user:
        await message.answer("❌ Пользователь не найден. Используй /start")
        return
    
    text = f"""
📊 <b>Твоя статистика</b>

📥 Всего скачиваний: <b>{user.downloads_count}</b>
📥 Скачиваний сегодня: <b>{user.downloads_today}</b>
👥 Приглашенных друзей: <b>{user.referral_count}</b>

{"⭐ Premium статус активен!" if user.is_premium else ""}
"""
    
    await message.answer(text, reply_markup=get_main_menu())


@router.message(Command("admin_stats"))
async def admin_stats(message: Message, session: AsyncSession):
    """Show admin statistics (admin only)"""
    from ..config import config
    
    if message.from_user.id != config.admin_id:
        return
    
    total_users = await StatsCRUD.get_total_users(session)
    today_users = await StatsCRUD.get_today_users(session)
    total_downloads = await StatsCRUD.get_total_downloads(session)
    today_downloads = await StatsCRUD.get_today_downloads(session)
    
    text = messages.STATS.format(
        total_users=total_users,
        today_users=today_users,
        total_downloads=total_downloads,
        today_downloads=today_downloads
    )
    
    await message.answer(text)


@router.callback_query(F.data == "back_main")
async def back_to_main(callback: CallbackQuery):
    """Return to main menu"""
    await callback.message.edit_text(
        "👋 Главное меню",
        reply_markup=get_main_menu()
    )
    await callback.answer()

