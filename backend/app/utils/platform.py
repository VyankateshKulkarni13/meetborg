
import re

def detect_platform(url: str) -> str:
    """
    Detect the meeting platform from the URL
    """
    url = url.lower()
    
    if "meet.google.com" in url:
        return "google_meet"
    elif "zoom.us" in url or "zoom.com" in url:
        return "zoom"
    elif "teams.microsoft.com" in url or "teams.live.com" in url:
        return "microsoft_teams"
    
    return "unknown"
