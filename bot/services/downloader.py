"""
Universal downloader service for different platforms
"""
import os
import asyncio
from typing import Optional, Dict, Any
from pathlib import Path
import yt_dlp


class DownloadError(Exception):
    """Download error exception"""
    pass


class Downloader:
    """Universal downloader for social media platforms"""
    
    def __init__(self, download_dir: str = "./downloads"):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
    
    async def download(
        self,
        url: str,
        platform: str,
        format_type: str = "best",
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Download media from URL
        
        Args:
            url: Media URL
            platform: Platform name (youtube, tiktok, etc.)
            format_type: Format type (audio, video_hd, video_sd, etc.)
            user_id: User ID for organizing downloads
            
        Returns:
            Dict with file_path, file_size, title, etc.
        """
        try:
            if platform == "youtube":
                return await self._download_youtube(url, format_type, user_id)
            elif platform == "tiktok":
                return await self._download_tiktok(url, user_id)
            elif platform == "instagram":
                return await self._download_instagram(url, user_id)
            elif platform == "twitter":
                return await self._download_twitter(url, user_id)
            elif platform == "facebook":
                return await self._download_facebook(url, user_id)
            else:
                raise DownloadError(f"Unsupported platform: {platform}")
        except Exception as e:
            raise DownloadError(f"Download failed: {str(e)}")
    
    async def _download_youtube(
        self,
        url: str,
        format_type: str,
        user_id: Optional[int]
    ) -> Dict[str, Any]:
        """Download from YouTube"""
        output_template = str(self.download_dir / f"{user_id or 'temp'}_%(id)s.%(ext)s")
        
        # Configure yt-dlp options
        ydl_opts = {
            "outtmpl": output_template,
            "quiet": True,
            "no_warnings": True,
        }
        
        # Set format based on type
        if format_type == "audio":
            ydl_opts.update({
                "format": "bestaudio/best",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
            })
        elif format_type == "video_4k":
            ydl_opts["format"] = "bestvideo[height<=2160]+bestaudio/best"
        elif format_type == "video_hd":
            ydl_opts["format"] = "bestvideo[height<=1080]+bestaudio/best"
        elif format_type == "video_sd":
            ydl_opts["format"] = "bestvideo[height<=480]+bestaudio/best"
        else:
            ydl_opts["format"] = "best"
        
        # Download
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, self._download_with_ytdlp, url, ydl_opts)
        
        return info
    
    async def _download_tiktok(self, url: str, user_id: Optional[int]) -> Dict[str, Any]:
        """Download from TikTok"""
        output_template = str(self.download_dir / f"{user_id or 'temp'}_tiktok_%(id)s.%(ext)s")
        
        ydl_opts = {
            "outtmpl": output_template,
            "quiet": True,
            "no_warnings": True,
        }
        
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, self._download_with_ytdlp, url, ydl_opts)
        
        return info
    
    async def _download_instagram(self, url: str, user_id: Optional[int]) -> Dict[str, Any]:
        """Download from Instagram"""
        output_template = str(self.download_dir / f"{user_id or 'temp'}_ig_%(id)s.%(ext)s")
        
        ydl_opts = {
            "outtmpl": output_template,
            "quiet": True,
            "no_warnings": True,
        }
        
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, self._download_with_ytdlp, url, ydl_opts)
        
        return info
    
    async def _download_twitter(self, url: str, user_id: Optional[int]) -> Dict[str, Any]:
        """Download from Twitter/X"""
        output_template = str(self.download_dir / f"{user_id or 'temp'}_twitter_%(id)s.%(ext)s")
        
        ydl_opts = {
            "outtmpl": output_template,
            "quiet": True,
            "no_warnings": True,
        }
        
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, self._download_with_ytdlp, url, ydl_opts)
        
        return info
    
    async def _download_facebook(self, url: str, user_id: Optional[int]) -> Dict[str, Any]:
        """Download from Facebook"""
        output_template = str(self.download_dir / f"{user_id or 'temp'}_fb_%(id)s.%(ext)s")
        
        ydl_opts = {
            "outtmpl": output_template,
            "quiet": True,
            "no_warnings": True,
        }
        
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, self._download_with_ytdlp, url, ydl_opts)
        
        return info
    
    def _download_with_ytdlp(self, url: str, ydl_opts: dict) -> Dict[str, Any]:
        """Download using yt-dlp (sync function for executor)"""
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # Get downloaded file path
            if "requested_downloads" in info:
                file_path = info["requested_downloads"][0]["filepath"]
            else:
                file_path = ydl.prepare_filename(info)
            
            # Get file size
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            
            return {
                "file_path": file_path,
                "file_size": file_size,
                "title": info.get("title", "Unknown"),
                "duration": info.get("duration"),
                "thumbnail": info.get("thumbnail"),
                "uploader": info.get("uploader"),
            }
    
    @staticmethod
    def cleanup_file(file_path: str):
        """Remove downloaded file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            pass

