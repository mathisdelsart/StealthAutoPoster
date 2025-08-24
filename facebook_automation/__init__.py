"""
Facebook Automation Package
A modular, human-like Facebook automation tool for group posting
"""

__version__ = "1.0.0"
__author__ = "Mathis Delsart"
__description__ = "Modular Facebook automation for group posting with human-like behavior"

# Import main classes for easy access
from .facebook_automation import FacebookAutomation
from .config import Config, FacebookCredentials, AutomationConfig, FacebookSelectors
from .driver_manager import WebDriverManager
from .human_behavior import HumanBehavior
from .facebook_auth import FacebookAuthenticator
from .group_extractor import GroupExtractor
from .post_publisher import PostPublisher

# Define what's available when using "from facebook_automation import *"
__all__ = [
    'FacebookAutomation',
    'Config',
    'FacebookCredentials', 
    'AutomationConfig',
    'FacebookSelectors',
    'WebDriverManager',
    'HumanBehavior',
    'FacebookAuthenticator',
    'GroupExtractor',
    'PostPublisher'
]

# Package-level configuration
DEFAULT_CONFIG = None

def get_default_config():
    """Get or create the default configuration instance"""
    global DEFAULT_CONFIG
    if DEFAULT_CONFIG is None:
        DEFAULT_CONFIG = Config()
    return DEFAULT_CONFIG

def create_automation(config=None):
    """
    Convenience function to create a FacebookAutomation instance
    
    Args:
        config: Optional Config instance. Uses default if None.
        
    Returns:
        FacebookAutomation: Configured automation instance
    """
    if config is None:
        config = get_default_config()
    return FacebookAutomation(config)
