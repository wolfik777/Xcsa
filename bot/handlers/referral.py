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
    
    # Format message
    text = messages.REFERRAL_INFO.format(
        count=user.referral_count,
        position=position,
        link=referral_link,
        bonus_count=config.referral_bonus_count,
        premium_count=config.premium_referral_count
    )
    
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
    
    # Format leaderboard
    leaderboard_text = ""
    for i, user in enumerate(top_users, 1):
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"{i}.")
        name = user.first_name
        if user.username:
            name = f"@{user.username}"
        
        leaderboard_text += f"{medal} {name} - <b>{user.referral_count}</b> рефералов\n"
    
    text = messages.LEADERBOARD.format(leaderboard=leaderboard_text)
    
    await message.answer(text, reply_markup=get_main_menu())

