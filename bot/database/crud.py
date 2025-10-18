"""
Database CRUD operations
"""
import secrets
from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User, Download, BotStats


class UserCRUD:
    """User CRUD operations"""
    
    @staticmethod
    async def get_or_create(
        session: AsyncSession,
        user_id: int,
        username: Optional[str],
        first_name: str,
        last_name: Optional[str],
        referrer_code: Optional[str] = None
    ) -> tuple[User, bool]:
        """Get existing user or create new one"""
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if user:
            # Update user info
            user.username = username
            user.first_name = first_name
            user.last_name = last_name
            await session.commit()
            return user, False
        
        # Create new user
        referrer = None
        if referrer_code:
            result = await session.execute(
                select(User).where(User.referral_code == referrer_code)
            )
            referrer = result.scalar_one_or_none()
        
        user = User(
            id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            referral_code=secrets.token_urlsafe(8),
            referrer_id=referrer.id if referrer else None
        )
        
        session.add(user)
        await session.commit()
        
        # Increment referrer's count
        if referrer:
            referrer.referral_count += 1
            await session.commit()
        
        return user, True
    
    @staticmethod
    async def get_by_id(session: AsyncSession, user_id: int) -> Optional[User]:
        """Get user by ID"""
        result = await session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def increment_downloads(session: AsyncSession, user_id: int):
        """Increment user's download count"""
        user = await UserCRUD.get_by_id(session, user_id)
        if not user:
            return
        
        today = date.today()
        if user.last_download_date and user.last_download_date.date() == today:
            user.downloads_today += 1
        else:
            user.downloads_today = 1
            user.last_download_date = datetime.now()
        
        user.downloads_count += 1
        await session.commit()
    
    @staticmethod
    async def get_leaderboard(session: AsyncSession, limit: int = 10) -> List[User]:
        """Get top users by referral count"""
        result = await session.execute(
            select(User)
            .where(User.referral_count > 0)
            .order_by(desc(User.referral_count))
            .limit(limit)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_user_position(session: AsyncSession, user_id: int) -> int:
        """Get user's position in leaderboard"""
        user = await UserCRUD.get_by_id(session, user_id)
        if not user:
            return 0
        
        result = await session.execute(
            select(func.count())
            .select_from(User)
            .where(User.referral_count > user.referral_count)
        )
        return result.scalar() + 1
    
    @staticmethod
    async def get_referrals(session: AsyncSession, user_id: int, limit: int = 10) -> List[User]:
        """Get list of users referred by this user"""
        result = await session.execute(
            select(User)
            .where(User.referrer_id == user_id)
            .order_by(desc(User.created_at))
            .limit(limit)
        )
        return list(result.scalars().all())


class DownloadCRUD:
    """Download CRUD operations"""
    
    @staticmethod
    async def create(
        session: AsyncSession,
        user_id: int,
        platform: str,
        url: str,
        file_type: str,
        file_size: Optional[int] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> Download:
        """Create download record"""
        download = Download(
            user_id=user_id,
            platform=platform,
            url=url,
            file_type=file_type,
            file_size=file_size,
            success=success,
            error_message=error_message
        )
        
        session.add(download)
        await session.commit()
        return download
    
    @staticmethod
    async def get_user_downloads_today(session: AsyncSession, user_id: int) -> int:
        """Get number of downloads by user today"""
        today = datetime.now().date()
        result = await session.execute(
            select(func.count())
            .select_from(Download)
            .where(
                Download.user_id == user_id,
                func.date(Download.created_at) == today,
                Download.success == True
            )
        )
        return result.scalar()


class StatsCRUD:
    """Statistics CRUD operations"""
    
    @staticmethod
    async def get_total_users(session: AsyncSession) -> int:
        """Get total number of users"""
        result = await session.execute(select(func.count()).select_from(User))
        return result.scalar()
    
    @staticmethod
    async def get_today_users(session: AsyncSession) -> int:
        """Get number of new users today"""
        today = datetime.now().date()
        result = await session.execute(
            select(func.count())
            .select_from(User)
            .where(func.date(User.created_at) == today)
        )
        return result.scalar()
    
    @staticmethod
    async def get_total_downloads(session: AsyncSession) -> int:
        """Get total number of downloads"""
        result = await session.execute(
            select(func.count())
            .select_from(Download)
            .where(Download.success == True)
        )
        return result.scalar()
    
    @staticmethod
    async def get_today_downloads(session: AsyncSession) -> int:
        """Get number of downloads today"""
        today = datetime.now().date()
        result = await session.execute(
            select(func.count())
            .select_from(Download)
            .where(
                func.date(Download.created_at) == today,
                Download.success == True
            )
        )
        return result.scalar()

