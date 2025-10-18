"""
Referral system handlers
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import messages, config
from ..keyboards import get_main_menu, get_share_button
from ..database.crud import UserCRUD

router = Router()


@router.message(Command("referral"))
@router.message(F.text == "🎁 Реферальная программа")
async def referral_info(message: Message, session: AsyncSession):
    """Show referral information"""
    user = await UserCRUD.get_by_id(session, message.from_user.id)
    
    if not user:
        await message.answer("❌ Пользователь не найден. Используй /start")
        return
    
    # Get bot username
    bot = message.bot
    bot_me = await bot.get_me()
    bot_username = bot_me.username
    
    # Create referral link
    referral_link = f"https://t.me/{bot_username}?start={user.referral_code}"
    
    # Get user position in leaderboard
    position = await UserCRUD.get_user_position(session, message.from_user.id)
    
    # Get list of referrals (last 5)
    referrals = await UserCRUD.get_referrals(session, message.from_user.id, limit=5)
    
    referrals_text = ""
    if referrals:
        referrals_text = "\n\n<b>📋 Последние рефералы:</b>\n"
        for i, ref in enumerate(referrals, 1):
            name = ref.first_name
            if ref.username:
                name = f"@{ref.username}"
            referrals_text += f"{i}. {name}\n"
    
    # Format message
    text = messages.REFERRAL_INFO.format(
        count=user.referral_count,
        position=position,
        link=referral_link,
        bonus_count=config.referral_bonus_count,
        premium_count=config.premium_referral_count
    ) + referrals_text
    
    await message.answer(
        text,
        reply_markup=get_share_button(referral_link)
    )


@router.message(Command("leaderboard"))
@router.message(F.text == "🏆 Топ рефералов")
async def leaderboard(message: Message, session: AsyncSession):
    """Show referral leaderboard"""
    top_users = await UserCRUD.get_leaderboard(session, limit=10)
    
    if not top_users:
        await message.answer(
            "🏆 <b>Топ рефералов</b>\n\nПока никого нет. Стань первым! 🚀",
            reply_markup=get_main_menu()
        )
        return
    
    # Get current user position
    user = await UserCRUD.get_by_id(session, message.from_user.id)
    user_position = await UserCRUD.get_user_position(session, message.from_user.id) if user else 0
    
    # Format leaderboard
    leaderboard_text = ""
    for i, top_user in enumerate(top_users, 1):
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"{i}.")
        name = top_user.first_name
        if top_user.username:
            name = f"@{top_user.username}"
        
        # Highlight current user
        if user and top_user.id == user.id:
            leaderboard_text += f"<b>➤ {medal} {name} - {top_user.referral_count} рефералов (ТЫ)</b>\n"
        else:
            leaderboard_text += f"{medal} {name} - <b>{top_user.referral_count}</b> рефералов\n"
    
    # Add user position if not in top 10
    user_stats_text = ""
    if user and (user_position > 10 or user.referral_count == 0):
        user_stats_text = f"\n\n<b>📊 Твоя позиция:</b> #{user_position}\n<b>👥 Твои рефералы:</b> {user.referral_count}"
    
    text = messages.LEADERBOARD.format(leaderboard=leaderboard_text) + user_stats_text
    
    await message.answer(text, reply_markup=get_main_menu())


@router.message(Command("my_referrals"))
async def my_referrals(message: Message, session: AsyncSession):
    """Show all user's referrals"""
    user = await UserCRUD.get_by_id(session, message.from_user.id)
    
    if not user:
        await message.answer("❌ Пользователь не найден. Используй /start")
        return
    
    if user.referral_count == 0:
        await message.answer(
            "👥 <b>Твои рефералы</b>\n\n"
            "У тебя пока нет рефералов.\n\n"
            "Используй команду /referral чтобы получить реферальную ссылку!",
            reply_markup=get_main_menu()
        )
        return
    
    # Get all referrals
    referrals = await UserCRUD.get_referrals(session, message.from_user.id, limit=50)
    
    referrals_text = f"👥 <b>Твои рефералы</b> (Всего: {user.referral_count})\n\n"
    
    for i, ref in enumerate(referrals, 1):
        name = ref.first_name
        if ref.username:
            name = f"@{ref.username}"
        
        # Show registration date
        reg_date = ref.created_at.strftime("%d.%m.%Y")
        referrals_text += f"{i}. {name} - <i>{reg_date}</i>\n"
    
    if len(referrals) < user.referral_count:
        referrals_text += f"\n<i>... и еще {user.referral_count - len(referrals)}</i>"
    
    await message.answer(referrals_text, reply_markup=get_main_menu())

