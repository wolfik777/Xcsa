"""
URL parser for different platforms
"""
import re
from typing import Optional, Tuple
from urllib.parse import urlparse


class URLParser:
    """Parse URLs and detect platforms"""
    
    PATTERNS = {
        "youtube": [
            r"(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})",
            r"(?:https?://)?(?:www\.)?youtube\.com/shorts/([a-zA-Z0-9_-]{11})",
        ],
        "tiktok": [
            r"(?:https?://)?(?:www\.|vm\.)?tiktok\.com/@?[\w.-]+/video/(\d+)",
            r"(?:https?://)?(?:www\.|vt\.)?tiktok\.com/(\w+)",
        ],
        "instagram": [
            r"(?:https?://)?(?:www\.)?instagram\.com/(?:p|reel|tv)/([a-zA-Z0-9_-]+)",
            r"(?:https?://)?(?:www\.)?instagram\.com/stories/[\w.-]+/(\d+)",
        ],
        "twitter": [
            r"(?:https?://)?(?:www\.)?(?:twitter|x)\.com/\w+/status/(\d+)",
        ],
        "facebook": [
            r"(?:https?://)?(?:www\.)?facebook\.com/.+/videos/(\d+)",
            r"(?:https?://)?(?:www\.)?fb\.watch/([a-zA-Z0-9_-]+)",
        ],
        "vk": [
            r"(?:https?://)?(?:www\.)?vk\.com/video(-?\d+_\d+)",
            r"(?:https?://)?(?:www\.)?vk\.com/clip(-?\d+_\d+)",
            r"(?:https?://)?(?:www\.)?vk\.com/video\?z=video(-?\d+_\d+)",
        ],
        "rutube": [
            r"(?:https?://)?(?:www\.)?rutube\.ru/video/([a-zA-Z0-9]+)",
            r"(?:https?://)?(?:www\.)?rutube\.ru/play/embed/(\d+)",
        ],
    }
    
    @classmethod
    def detect_platform(cls, url: str) -> Optional[str]:
        """Detect platform from URL"""
        url = url.strip()
        
        for platform, patterns in cls.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, url, re.IGNORECASE):
                    return platform
        
        return None
    
    @classmethod
    def parse_url(cls, url: str) -> Tuple[Optional[str], str]:
        """
        Parse URL and return platform and clean URL
        Returns: (platform, clean_url)
        """
        platform = cls.detect_platform(url)
        
        # Clean URL
        clean_url = url.strip()
        
        # Remove tracking parameters
        try:
            parsed = urlparse(clean_url)
            # Rebuild URL without query parameters for some platforms
            # НЕ удаляем параметры для VK, так как они нужны
            if platform in ["instagram", "facebook", "rutube"]:
                clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        except:
            pass
        
        return platform, clean_url
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if string is a valid URL"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

