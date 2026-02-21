"""
Platform Detector Service
Auto-detects meeting platform from URL and extracts meeting codes
"""
import re
from typing import Optional, Tuple
from app.models.meeting import PlatformType


class PlatformDetector:
    """Service to detect meeting platform and extract meeting codes from URLs"""
    
    # URL patterns for different platforms with meeting code extraction
    PATTERNS = {
        PlatformType.GOOGLE_MEET: [
            r'meet\.google\.com/([a-z]{3}(?:-[a-z]{4}){2})',  # abc-defg-hij
            r'g\.co/meet/([a-z]{3}(?:-[a-z]{4}){2})',
        ],
        PlatformType.ZOOM: [
            r'zoom\.us/j/(\d{9,})(?:\?pwd=([^&\s]+))?',  # Meeting ID with optional password
            r'zoom\.us/meeting/(\d{9,})(?:\?pwd=([^&\s]+))?',
            r'us\d+web\.zoom\.us/j/(\d{9,})(?:\?pwd=([^&\s]+))?',
            r'(?:[\w-]+\.)?zoom\.us/my/([\w.-]+)',  # Personal Meeting Link
        ],
        PlatformType.MICROSOFT_TEAMS: [
            r'teams\.microsoft\.com/.*meetup-join/([^/\?]+)',
            r'teams\.live\.com/meet/([^/\?]+)',
            # Launch-redirect URL: coords param contains meetingCode as Base64 JSON
            r'teams\.live\.com/light-meetings/launch.*[?&]p=([^&]+)',
        ],
        PlatformType.WEBEX: [
            r'(?:webex\.com|meet\.webex\.com)/meet/([^/\?]+)',
        ],
        PlatformType.JITSI: [
            r'meet\.jit\.si/([^/\?]+)',
        ],
    }
    
    @classmethod
    def detect_platform(cls, url: str) -> Tuple[PlatformType, Optional[str]]:
        """
        Detect platform and extract meeting code from URL
        
        Args:
            url: Meeting URL
            
        Returns:
            Tuple of (platform_type, meeting_code)
        """
        if not url:
            return PlatformType.OTHER, None
        
        url = url.lower().strip()
        
        # Try each platform's patterns
        for platform, patterns in cls.PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    meeting_code = match.group(1)
                    return platform, meeting_code
        
        # No match found
        return PlatformType.OTHER, None
    
    @classmethod
    def is_valid_url(cls, url: str) -> bool:
        """
        Check if URL is a valid meeting URL
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid meeting URL, False otherwise
        """
        if not url:
            return False
        
        url = url.lower().strip()
        
        # Check if URL contains any known meeting platform domain
        meeting_domains = [
            'meet.google.com',
            'g.co/meet',
            'zoom.us',
            'teams.microsoft.com',
            'teams.live.com',
            'webex.com',
            'meet.webex.com',
            'meet.jit.si',
        ]
        
        return any(domain in url for domain in meeting_domains)
    
    @classmethod
    def get_platform_name(cls, platform: PlatformType) -> str:
        """
        Get human-readable platform name
        
        Args:
            platform: Platform type enum
            
        Returns:
            Human-readable platform name
        """
        names = {
            PlatformType.GOOGLE_MEET: "Google Meet",
            PlatformType.ZOOM: "Zoom",
            PlatformType.MICROSOFT_TEAMS: "Microsoft Teams",
            PlatformType.WEBEX: "Cisco Webex",
            PlatformType.JITSI: "Jitsi Meet",
            PlatformType.OTHER: "Other Platform",
        }
        return names.get(platform, "Unknown")
    
    @classmethod
    def get_join_url(cls, platform: PlatformType, meeting_code: str) -> str:
        """
        Construct standard meeting URL from platform and code
        
        Args:
            platform: Platform type
            meeting_code: Meeting code/ID
            
        Returns:
            Full meeting URL
        """
        templates = {
            PlatformType.GOOGLE_MEET: f"https://meet.google.com/{meeting_code}",
            PlatformType.ZOOM: f"https://zoom.us/j/{meeting_code}",
            PlatformType.MICROSOFT_TEAMS: f"https://teams.microsoft.com/l/meetup-join/{meeting_code}",
            PlatformType.WEBEX: f"https://meet.webex.com/meet/{meeting_code}",
            PlatformType.JITSI: f"https://meet.jit.si/{meeting_code}",
        }
        return templates.get(platform, "#")


# Singleton instance
platform_detector = PlatformDetector()
