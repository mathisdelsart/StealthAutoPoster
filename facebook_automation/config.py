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
            raise ValueError("Environment variable is required. Check 'get_post_text()' method.")
    
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
        return os.environ.get('POST_TEXT', '')