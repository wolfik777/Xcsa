"""
Admin panel handlers
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import config, messages
from ..database.crud import UserCRUD, StatsCRUD, DownloadCRUD
from ..keyboards import get_main_menu

router = Router()


def get_admin_menu() -> InlineKeyboardMarkup:
    """Admin panel menu"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats"),
        InlineKeyboardButton(text="👥 Пользователи", callback_data="admin_users")
    )
    builder.row(
        InlineKeyboardButton(text="📥 Скачивания", callback_data="admin_downloads"),
        InlineKeyboardButton(text="🎁 Рефералы", callback_data="admin_referrals")
    )
    builder.row(
        InlineKeyboardButton(text="💬 Рассылка", callback_data="admin_broadcast"),
        InlineKeyboardButton(text="🔧 Настройки", callback_data="admin_settings")
    )
    builder.row(
        InlineKeyboardButton(text="❌ Закрыть", callback_data="admin_close")
    )
    
    return builder.as_markup()


@router.message(Command("admin"))
async def admin_panel(message: Message, session: AsyncSession):
    """Admin panel"""
    # Check if user is admin
    if message.from_user.id != config.admin_id:
        await message.answer("❌ У вас нет доступа к админ-панели!")
        return
    
    await message.answer(
        "🔐 <b>Админ-панель</b>\n\n"
        "Выберите действие:",
        reply_markup=get_admin_menu()
    )


@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery, session: AsyncSession):
    """Show statistics"""
    if callback.from_user.id != config.admin_id:
        await callback.answer("❌ Доступ запрещён", show_alert=True)
        return
    
    # Get statistics
    total_users = await StatsCRUD.get_total_users(session)
    today_users = await StatsCRUD.get_today_users(session)
    total_downloads = await StatsCRUD.get_total_downloads(session)
    today_downloads = await StatsCRUD.get_today_downloads(session)
    
    # Get top referrers
    top_referrers = await UserCRUD.get_leaderboard(session, limit=5)
    
    text = f"""
📊 <b>Статистика бота</b>

👥 <b>Пользователи:</b>
  • Всего: {total_users}
  • Сегодня: +{today_users}

📥 <b>Скачивания:</b>
  • Всего: {total_downloads}
  • Сегодня: {today_downloads}

🎁 <b>Топ-5 рефереров:</b>
"""
    
    for i, user in enumerate(top_referrers, 1):
        name = user.first_name
        if user.username:
            name = f"@{user.username}"
        text += f"{i}. {name} - {user.referral_count} реф.\n"
    
    await callback.message.edit_text(text, reply_markup=get_admin_menu())
    await callback.answer()


@router.callback_query(F.data == "admin_users")
async def admin_users(callback: CallbackQuery, session: AsyncSession):
    """Show users info"""
    if callback.from_user.id != config.admin_id:
        await callback.answer("❌ Доступ запрещён", show_alert=True)
        return
    
    total_users = await StatsCRUD.get_total_users(session)
    today_users = await StatsCRUD.get_today_users(session)
    
    # Count premium users
    from sqlalchemy import select, func
    from ..database.models import User
    
    result = await session.execute(
        select(func.count()).select_from(User).where(User.is_premium == True)
    )
    premium_count = result.scalar()
    
    text = f"""
👥 <b>Пользователи</b>

📈 Всего пользователей: <b>{total_users}</b>
🆕 Новых сегодня: <b>{today_users}</b>
⭐ Premium пользователей: <b>{premium_count}</b>

💡 <i>Для просмотра списка используйте /admin_list</i>
"""
    
    await callback.message.edit_text(text, reply_markup=get_admin_menu())
    await callback.answer()


@router.callback_query(F.data == "admin_downloads")
async def admin_downloads(callback: CallbackQuery, session: AsyncSession):
    """Show downloads info"""
    if callback.from_user.id != config.admin_id:
        await callback.answer("❌ Доступ запрещён", show_alert=True)
        return
    
    total_downloads = await StatsCRUD.get_total_downloads(session)
    today_downloads = await StatsCRUD.get_today_downloads(session)
    
    # Get downloads by platform
    from sqlalchemy import select, func
    from ..database.models import Download
    
    result = await session.execute(
        select(Download.platform, func.count(Download.id))
        .where(Download.success == True)
        .group_by(Download.platform)
        .order_by(func.count(Download.id).desc())
    )
    platforms = result.all()
    
    text = f"""
📥 <b>Скачивания</b>

📊 Всего скачиваний: <b>{total_downloads}</b>
📅 Сегодня: <b>{today_downloads}</b>

🎯 <b>По платформам:</b>
"""
    
    for platform, count in platforms:
        text += f"  • {platform.capitalize()}: {count}\n"
    
    await callback.message.edit_text(text, reply_markup=get_admin_menu())
    await callback.answer()


@router.callback_query(F.data == "admin_referrals")
async def admin_referrals(callback: CallbackQuery, session: AsyncSession):
    """Show referrals info"""
    if callback.from_user.id != config.admin_id:
        await callback.answer("❌ Доступ запрещён", show_alert=True)
        return
    
    # Get total referrals
    from sqlalchemy import select, func
    from ..database.models import User
    
    result = await session.execute(
        select(func.sum(User.referral_count)).select_from(User)
    )
    total_referrals = result.scalar() or 0
    
    # Get users with referrals
    result = await session.execute(
        select(func.count()).select_from(User).where(User.referral_count > 0)
    )
    users_with_refs = result.scalar()
    
    # Get top referrer
    top_referrers = await UserCRUD.get_leaderboard(session, limit=1)
    top_name = "Нет"
    top_count = 0
    if top_referrers:
        top_user = top_referrers[0]
        top_name = f"@{top_user.username}" if top_user.username else top_user.first_name
        top_count = top_user.referral_count
    
    text = f"""
🎁 <b>Реферальная система</b>

📊 Всего рефералов: <b>{total_referrals}</b>
👥 Пользователей с рефералами: <b>{users_with_refs}</b>

🏆 <b>Топ реферер:</b>
  {top_name} - {top_count} реф.

💡 <i>Полный топ: /leaderboard</i>
"""
    
    await callback.message.edit_text(text, reply_markup=get_admin_menu())
    await callback.answer()


@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast(callback: CallbackQuery):
    """Broadcast message"""
    if callback.from_user.id != config.admin_id:
        await callback.answer("❌ Доступ запрещён", show_alert=True)
        return
    
    text = (
        "💬 <b>Рассылка</b>\n\n"
        "Функция рассылки будет доступна в следующей версии.\n\n"
        "Для ручной рассылки используйте:\n"
        "/broadcast - текст сообщения"
    )
    
    await callback.message.edit_text(text, reply_markup=get_admin_menu())
    await callback.answer()


@router.callback_query(F.data == "admin_settings")
async def admin_settings(callback: CallbackQuery):
    """Bot settings"""
    if callback.from_user.id != config.admin_id:
        await callback.answer("❌ Доступ запрещён", show_alert=True)
        return
    
    text = f"""
🔧 <b>Настройки бота</b>

📝 <b>Текущие настройки:</b>
  • Лимит скачиваний: {config.max_downloads_per_day} в день
  • Бонус за реферала: {config.referral_bonus_count}
  • Premium за рефералов: {config.premium_referral_count}
  • Макс размер файла: {config.max_file_size_mb} МБ

💡 <i>Для изменения настроек редактируйте bot/config.py</i>
"""
    
    await callback.message.edit_text(text, reply_markup=get_admin_menu())
    await callback.answer()


@router.callback_query(F.data == "admin_close")
async def admin_close(callback: CallbackQuery):
    """Close admin panel"""
    if callback.from_user.id != config.admin_id:
        await callback.answer("❌ Доступ запрещён", show_alert=True)
        return
    
    await callback.message.delete()
    await callback.message.answer("✅ Админ-панель закрыта", reply_markup=get_main_menu())
    await callback.answer()

