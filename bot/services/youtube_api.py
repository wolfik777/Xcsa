"""
YouTube Download API Service
Free tier: 100 requests/day
"""
import aiohttp
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class YouTubeAPIDownloader:
    """YouTube downloader using free API"""
    
    def __init__(self):
        self.api_urls = [
            # API 1: yt5s.io (бесплатно, без ограничений)
            {
                "name": "YT5S",
                "info_url": "https://yt5s.io/api/ajaxSearch",
                "download_url": "https://yt5s.io/api/ajaxConvert"
            },
            # API 2: y2mate.com (бесплатно, 100/день)
            {
                "name": "Y2MATE",
                "info_url": "https://www.y2mate.com/mates/analyze/ajax",
                "download_url": "https://www.y2mate.com/mates/convert"
            }
        ]
        
    async def download_video(self, url: str, quality: str = "720") -> Optional[Dict[str, Any]]:
        """
        Download video from YouTube using API
        
        Args:
            url: YouTube URL
            quality: Video quality (360, 480, 720, 1080)
            
        Returns:
            Dict with download_url, title, size
        """
        # Пробуем API по порядку
        for api in self.api_urls:
            try:
                result = await self._try_api(api, url, quality)
                if result:
                    logger.info(f"Successfully got download link from {api['name']}")
                    return result
            except Exception as e:
                logger.warning(f"API {api['name']} failed: {str(e)}")
                continue
        
        return None
    
    async def _try_api(self, api: Dict, url: str, quality: str) -> Optional[Dict[str, Any]]:
        """Try to download using specific API"""
        if api['name'] == "YT5S":
            return await self._download_yt5s(url, quality)
        elif api['name'] == "Y2MATE":
            return await self._download_y2mate(url, quality)
        return None
    
    async def _download_yt5s(self, url: str, quality: str) -> Optional[Dict[str, Any]]:
        """Download using YT5S API"""
        async with aiohttp.ClientSession() as session:
            # Step 1: Get video info
            data = {
                "url": url,
                "vt": "home"
            }
            
            async with session.post(
                "https://yt5s.io/api/ajaxSearch",
                data=data,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status != 200:
                    return None
                
                result = await resp.json()
                if result.get('status') != 'ok':
                    return None
                
                # Parse video info
                links = result.get('links', {})
                mp4_links = links.get('mp4', {})
                
                # Выбираем нужное качество
                quality_map = {
                    '360': '360',
                    '480': '480',
                    '720': '720',
                    '1080': '1080'
                }
                
                selected_quality = quality_map.get(quality, '720')
                
                # Ищем подходящее качество
                video_data = None
                for q in [selected_quality, '720', '480', '360']:
                    if q in mp4_links:
                        video_data = mp4_links[q]
                        break
                
                if not video_data:
                    return None
                
                # Step 2: Get download link
                convert_data = {
                    "vid": result['vid'],
                    "k": video_data['k']
                }
                
                async with session.post(
                    "https://yt5s.io/api/ajaxConvert",
                    data=convert_data,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp2:
                    if resp2.status != 200:
                        return None
                    
                    convert_result = await resp2.json()
                    if convert_result.get('status') != 'ok':
                        return None
                    
                    return {
                        'download_url': convert_result['dlink'],
                        'title': result.get('title', 'video'),
                        'quality': video_data.get('q', quality),
                        'size': video_data.get('size', 'Unknown')
                    }
    
    async def _download_y2mate(self, url: str, quality: str) -> Optional[Dict[str, Any]]:
        """Download using Y2Mate API"""
        # Y2Mate API implementation
        # Этот API требует больше шагов, оставлю как резерв
        return None
    
    async def download_audio(self, url: str) -> Optional[Dict[str, Any]]:
        """Download audio from YouTube"""
        async with aiohttp.ClientSession() as session:
            # YT5S audio download
            data = {
                "url": url,
                "vt": "home"
            }
            
            try:
                async with session.post(
                    "https://yt5s.io/api/ajaxSearch",
                    data=data,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        return None
                    
                    result = await resp.json()
                    if result.get('status') != 'ok':
                        return None
                    
                    # Get MP3 link
                    links = result.get('links', {})
                    mp3_links = links.get('mp3', {})
                    
                    if '128' in mp3_links:
                        audio_data = mp3_links['128']
                    elif 'mp3128' in mp3_links:
                        audio_data = mp3_links['mp3128']
                    else:
                        return None
                    
                    # Convert to MP3
                    convert_data = {
                        "vid": result['vid'],
                        "k": audio_data['k']
                    }
                    
                    async with session.post(
                        "https://yt5s.io/api/ajaxConvert",
                        data=convert_data,
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as resp2:
                        if resp2.status != 200:
                            return None
                        
                        convert_result = await resp2.json()
                        if convert_result.get('status') != 'ok':
                            return None
                        
                        return {
                            'download_url': convert_result['dlink'],
                            'title': result.get('title', 'audio'),
                            'format': 'mp3'
                        }
            except Exception as e:
                logger.error(f"Audio download failed: {str(e)}")
                return None

