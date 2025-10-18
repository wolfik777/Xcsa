"""
Universal downloader service for different platforms
"""
import os
import asyncio
import aiohttp
import random
from typing import Optional, Dict, Any, List
from pathlib import Path
import yt_dlp
from bot.config import config
from pytube import YouTube
import re
from bot.services.youtube_api import YouTubeAPIDownloader


class DownloadError(Exception):
    """Download error exception"""
    pass


class Downloader:
    """Universal downloader for social media platforms"""
    
    def __init__(self, download_dir: str = "./downloads"):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        self.proxy_cache: List[str] = []
        self.yt_api = YouTubeAPIDownloader()
    
    async def get_working_proxy(self) -> Optional[str]:
        """Получить рабочий прокси из GeoNode API"""
        try:
            # Если есть закэшированные прокси, используем их
            if self.proxy_cache:
                return random.choice(self.proxy_cache)
            
            async with aiohttp.ClientSession() as session:
                # Получаем список прокси из GeoNode API
                url = "https://proxylist.geonode.com/api/proxy-list?limit=50&page=1&sort_by=lastChecked&sort_type=desc&protocols=http,socks4,socks5&speed=fast"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        proxies = data.get('data', [])
                        
                        # Фильтруем быстрые прокси с хорошим uptime
                        good_proxies = []
                        for p in proxies:
                            if p.get('upTime', 0) > 50:  # Uptime > 50%
                                ip = p.get('ip')
                                port = p.get('port')
                                protocols = p.get('protocols', [])
                                
                                # Формируем URL прокси
                                if 'http' in protocols:
                                    proxy_url = f"http://{ip}:{port}"
                                elif 'socks5' in protocols:
                                    proxy_url = f"socks5://{ip}:{port}"
                                elif 'socks4' in protocols:
                                    proxy_url = f"socks4://{ip}:{port}"
                                else:
                                    continue
                                
                                good_proxies.append(proxy_url)
                        
                        # Кэшируем прокси
                        if good_proxies:
                            self.proxy_cache = good_proxies[:20]  # Берём топ 20
                            return random.choice(self.proxy_cache)
            
            return None
        except Exception:
            # Ошибка получения прокси - игнорируем
            return None
    
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
                # Пробуем в порядке приоритета:
                # 1. Pytube (быстрый, без прокси) - первый вариант
                # 2. yt-dlp с прокси (медленный, но обходит блокировки) - резерв
                
                # 1. Пробуем pytube (без прокси, быстро)
                try:
                    print("[INFO] Trying pytube download (no proxy)...")
                    return await self._download_youtube_pytube(url, format_type, user_id)
                except Exception as pytube_error:
                    print(f"[WARNING] Pytube failed: {str(pytube_error)[:100]}")
                
                # 2. Fallback на yt-dlp с прокси
                print("[INFO] Falling back to yt-dlp with proxy...")
                return await self._download_youtube(url, format_type, user_id)
            elif platform == "tiktok":
                return await self._download_tiktok(url, user_id)
            elif platform == "instagram":
                return await self._download_instagram(url, user_id)
            elif platform == "twitter":
                return await self._download_twitter(url, user_id)
            elif platform == "facebook":
                return await self._download_facebook(url, user_id)
            elif platform == "vk":
                return await self._download_vk(url, user_id)
            elif platform == "rutube":
                return await self._download_rutube(url, user_id)
            else:
                raise DownloadError(f"Unsupported platform: {platform}")
        except Exception as e:
            raise DownloadError(f"Download failed: {str(e)}")
    
    async def _download_youtube_api(
        self,
        url: str,
        format_type: str,
        user_id: Optional[int]
    ) -> Dict[str, Any]:
        """Download from YouTube using free API (100 requests/day)"""
        try:
            # Определяем тип скачивания
            if format_type == "audio":
                # Скачиваем аудио
                result = await self.yt_api.download_audio(url)
                if not result:
                    raise DownloadError("API failed to get audio download link")
                
                # Скачиваем файл
                download_url = result['download_url']
                filename = f"{user_id or 'temp'}_youtube_audio.mp3"
                output_path = self.download_dir / filename
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(download_url, timeout=aiohttp.ClientTimeout(total=60)) as resp:
                        if resp.status == 200:
                            content = await resp.read()
                            with open(output_path, 'wb') as f:
                                f.write(content)
                        else:
                            raise DownloadError(f"Failed to download: HTTP {resp.status}")
                
                file_size = output_path.stat().st_size / (1024 * 1024)
                
                return {
                    "file_path": str(output_path),
                    "title": result.get('title', 'audio'),
                    "platform": "youtube",
                    "format": "mp3",
                    "size_mb": round(file_size, 2)
                }
            else:
                # Скачиваем видео
                quality_map = {
                    "video_4k": "1080",
                    "video_hd": "720",
                    "video_sd": "360"
                }
                quality = quality_map.get(format_type, "720")
                
                result = await self.yt_api.download_video(url, quality)
                if not result:
                    raise DownloadError("API failed to get video download link")
                
                # Скачиваем файл
                download_url = result['download_url']
                filename = f"{user_id or 'temp'}_youtube_video.mp4"
                output_path = self.download_dir / filename
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(download_url, timeout=aiohttp.ClientTimeout(total=120)) as resp:
                        if resp.status == 200:
                            content = await resp.read()
                            with open(output_path, 'wb') as f:
                                f.write(content)
                        else:
                            raise DownloadError(f"Failed to download: HTTP {resp.status}")
                
                file_size = output_path.stat().st_size / (1024 * 1024)
                
                return {
                    "file_path": str(output_path),
                    "title": result.get('title', 'video'),
                    "platform": "youtube",
                    "format": "mp4",
                    "size_mb": round(file_size, 2)
                }
        except Exception as e:
            print(f"[ERROR] YouTube API download failed: {str(e)}")
            raise
    
    async def _download_youtube_pytube(
        self,
        url: str,
        format_type: str,
        user_id: Optional[int]
    ) -> Dict[str, Any]:
        """Download from YouTube using pytube (faster, less blocked)"""
        try:
            print("[INFO] Trying pytube download (no proxy needed)...")
            
            # Создаем YouTube объект
            yt = YouTube(url)
            
            # Получаем название видео
            title = yt.title
            video_id = yt.video_id
            
            # Выбираем стрим в зависимости от формата
            if format_type == "audio":
                # Только аудио
                stream = yt.streams.filter(only_audio=True).first()
                ext = "mp3"
            elif format_type == "video_4k":
                # 4K видео (2160p)
                stream = yt.streams.filter(res="2160p", file_extension='mp4').first()
                if not stream:
                    stream = yt.streams.filter(res="1440p", file_extension='mp4').first()
                ext = "mp4"
            elif format_type == "video_hd":
                # HD видео (720p)
                stream = yt.streams.filter(res="720p", file_extension='mp4').first()
                if not stream:
                    stream = yt.streams.filter(res="480p", file_extension='mp4').first()
                ext = "mp4"
            else:
                # SD видео (360p) или лучшее доступное
                stream = yt.streams.filter(res="360p", file_extension='mp4').first()
                if not stream:
                    stream = yt.streams.filter(file_extension='mp4').first()
                ext = "mp4"
            
            if not stream:
                raise DownloadError("No suitable stream found")
            
            # Формируем имя файла
            filename = f"{user_id or 'temp'}_youtube_{video_id}.{ext}"
            output_path = self.download_dir / filename
            
            # Скачиваем (синхронно в отдельном потоке)
            await asyncio.to_thread(stream.download, output_path=str(self.download_dir), filename=filename)
            
            # Проверяем что файл создан
            if not output_path.exists():
                raise DownloadError("File not downloaded")
            
            file_size = output_path.stat().st_size / (1024 * 1024)  # MB
            
            print(f"[INFO] Downloaded with pytube: {filename} ({file_size:.2f} MB)")
            
            return {
                "file_path": str(output_path),
                "title": title,
                "platform": "youtube",
                "format": ext,
                "size_mb": round(file_size, 2)
            }
            
        except Exception as e:
            print(f"[WARNING] Pytube failed: {str(e)}")
            print("[INFO] Falling back to yt-dlp...")
            raise  # Пробросим ошибку чтобы fallback на yt-dlp
    
    async def _download_youtube(
        self,
        url: str,
        format_type: str,
        user_id: Optional[int]
    ) -> Dict[str, Any]:
        """Download from YouTube with advanced bypass"""
        output_template = str(self.download_dir / f"{user_id or 'temp'}_%(id)s.%(ext)s")
        
        # Используем прокси из конфига
        proxy = config.youtube_proxy
        
        # Configure yt-dlp options with PROXY + MAXIMUM bypass
        ydl_opts = {
            "outtmpl": output_template,
            "quiet": False,  # Показывать вывод для отладки
            "no_warnings": False,
            
            # МАКСИМАЛЬНЫЙ обход блокировок
            "geo_bypass": True,
            "geo_bypass_country": "US",
            
            # Использование разных методов извлечения
            "extractor_retries": 3,
            "fragment_retries": 10,
            "skip_unavailable_fragments": True,
            "retries": 5,
            
            # HTTP заголовки - притворяемся настоящим браузером
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "sec-ch-ua": '"Chromium";v="120"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
            },
            
            # КРИТИЧНО: Использовать мобильный клиент Android
            "extractor_args": {
                "youtube": {
                    "player_client": ["android", "ios", "web"],
                    "player_skip": ["configs", "webpage"],
                }
            },
            
            # Дополнительные опции
            "nocheckcertificate": True,
            "prefer_insecure": True,
            "cachedir": False,
            "no_cache_dir": True,
            
            # Таймауты увеличены для работы через прокси
            "socket_timeout": 60,
            
            # Отключаем IPv6 при использовании прокси
            "force_ipv4": True,
        }
        
        # ДОБАВЛЯЕМ ПРОКСИ если настроен в .env
        if proxy:
            ydl_opts["proxy"] = proxy
            print(f"[INFO] Using YouTube proxy: {proxy.split('@')[1] if '@' in proxy else proxy}")
        else:
            print("[INFO] No proxy configured, trying direct connection with bypass...")
        
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
    
    async def _download_vk(self, url: str, user_id: Optional[int]) -> Dict[str, Any]:
        """Download from VK (VKontakte)"""
        output_template = str(self.download_dir / f"{user_id or 'temp'}_vk_%(id)s.%(ext)s")
        
        ydl_opts = {
            "outtmpl": output_template,
            "quiet": False,  # Показывать ошибки
            "no_warnings": False,  # Показывать предупреждения
            "format": "best",
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        }
        
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, self._download_with_ytdlp, url, ydl_opts)
        
        return info
    
    async def _download_rutube(self, url: str, user_id: Optional[int]) -> Dict[str, Any]:
        """Download from Rutube"""
        output_template = str(self.download_dir / f"{user_id or 'temp'}_rutube_%(id)s.%(ext)s")
        
        ydl_opts = {
            "outtmpl": output_template,
            "quiet": False,  # Показывать ошибки
            "no_warnings": False,  # Показывать предупреждения
            "format": "best",
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
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

