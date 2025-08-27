"""
Configuration management module for Facebook automation
"""
import os
from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()


@dataclass
class FacebookCredentials:
    """Facebook login credentials"""
    email: str
    password: str
    
    @classmethod
    def from_env(cls) -> 'FacebookCredentials':
        email = os.environ.get('FACEBOOK_EMAIL')
        password = os.environ.get('FACEBOOK_PASSWORD')
        
        if not email or not password:
            raise ValueError("Environment variables FACEBOOK_EMAIL and FACEBOOK_PASSWORD are required")
        
        return cls(email=email, password=password)


@dataclass
class AutomationConfig:
    """Configuration for automation behavior"""
    dry_run: bool = False
    max_groups: Optional[int] = None
    max_scroll_time_minutes: int = 10
    post_delay_min: float = 5.0
    post_delay_max: float = 10.0
    typing_delay_min: float = 0.05
    typing_delay_max: float = 0.25
    page_load_delay_min: float = 2.0
    page_load_delay_max: float = 4.0


@dataclass
class FacebookSelectors:
    """CSS/XPath selectors for Facebook elements"""
    write_selectors: List[str]
    post_selectors: List[str]
    
    @classmethod
    def default(cls) -> 'FacebookSelectors':
        return cls(
            write_selectors=[
                '//span[contains(text(), "Exprimez-vous")]/ancestor::div[@role="button"]'
            ],
            post_selectors=[
                '//div[@aria-label="Publier" and @role="button"]',
                '//span[text()="Publier"]/parent::div[@role="button"]',
                '//span[text()="Publier"]/ancestor::div[@role="button"]',
                '//div[contains(text(), "Publier") and @role="button"]'
            ]
        )


class Config:
    """Main configuration class"""
    
    def __init__(self):
        self.credentials = FacebookCredentials.from_env()
        self.automation = AutomationConfig
        self.selectors = FacebookSelectors.default()
        self.post_text = self.get_post_text()
        self.my_groups_url = "https://www.facebook.com/groups/joins/?nav_source=tab&ordering=viewer_added"
        
        if not self.post_text:
            raise ValueError("Environment variable POST_TEXT is required")
    
    @property
    def chrome_options_args(self) -> List[str]:
        """Chrome options for stealth browsing"""
        return [
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--window-size=1920,1080",
            "--disable-save-password-bubble",
            "--disable-password-generation",
            "--disable-notifications",
            "--disable-infobars",
            "--disable-extensions",
            "--disable-popup-blocking",
            "--disable-default-apps",
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
    
    @property
    def chrome_prefs(self) -> dict:
        """Chrome preferences"""
        return {
            "profile.default_content_setting_values.notifications": 2,
            "profile.password_manager_enabled": False,
            "profile.default_content_settings.popups": 0,
            "credentials_enable_service": False,
            "profile.password_manager_leak_detection": False
        }

    def get_post_text(self):
        today = datetime.today()
        month, day = today.month, today.day

        if (month == 8 and day >= 25) or (month == 9) or (month == 10 and day <= 19):
            return os.environ.get("POST_TEXT_BACK_TO_SCHOOL", "")
        elif (month == 10 and day >= 20) or (month == 11 and day <= 2):
            return os.environ.get("POST_TEXT_AUTUMN_HOLIDAYS", "")
        elif (month == 11 and 3 <= day <= 30):
            return os.environ.get("POST_TEXT_MID_TERM", "")
        elif (month == 12 and 1 <= day <= 19):
            return os.environ.get("POST_TEXT_EXAMS_DECEMBER", "")
        elif (month == 12 and day >= 20) or (month == 1 and day <= 4):
            return os.environ.get("POST_TEXT_CHRISTMAS_HOLIDAYS", "")
        elif (month == 1 and 5 <= day <= 31) or (month == 2 and day <= 12):
            return os.environ.get("POST_TEXT_SECOND_TRIMESTER_1", "")
        elif (month == 2 and 13 <= day <= 29) or (month == 3 and day == 1):
            return os.environ.get("POST_TEXT_CARNIVAL_HOLIDAYS", "")
        elif (month == 3 and day >= 2) or (month == 4 and day <= 24):
            return os.environ.get("POST_TEXT_SECOND_TRIMESTER_2", "")
        elif (month == 4 and day >= 25) or (month == 5 and day <= 9):
            return os.environ.get("POST_TEXT_SPRING_HOLIDAYS", "")
        elif (month == 5 and day >= 10) or (month == 6 and day <= 28):
            return os.environ.get("POST_TEXT_EXAMS_JUNE", "")
        elif (month == 6 and day >= 29) or (month in [7, 8] and day <= 24):
            return os.environ.get("POST_TEXT_SUMMER_HOLIDAYS", "")
        else:
            raise ValueError("No post text found for the current date") # Should never happen
