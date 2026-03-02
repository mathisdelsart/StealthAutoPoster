"""
Main Facebook automation orchestrator
"""
import logging
from typing import List, Tuple, Optional, Union
from .config import Config
from .driver_manager import WebDriverManager
from .human_behavior import HumanBehavior
from .facebook_auth import FacebookAuthenticator
from .group_extractor import GroupExtractor
from .post_publisher import PostPublisher
import time

logger = logging.getLogger(__name__)


class FacebookAutomation:
    """Main orchestrator for Facebook automation tasks"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.driver_manager = WebDriverManager(self.config)
        self.driver = None
        self.human_behavior = HumanBehavior(self.config)
        self.authenticator = FacebookAuthenticator(self.config, self.human_behavior)
        self.group_extractor = GroupExtractor(self.config, self.human_behavior)
        self.post_publisher = PostPublisher(self.config, self.human_behavior, self.driver_manager)
        
        logger.info("Facebook Automation initialized")
    
    def start(self):
        """Start driver (open session)"""
        self.driver = self.driver_manager.__enter__()
        return self.driver

    def stop(self):
        """Stop driver (close session)"""
        if self.driver:
            self.driver_manager.__exit__(None, None, None)
            self.driver = None

    def login(self) -> bool:
        """
        Login functionality
        
        Returns:
            bool: True if login successful
        """
        login_info = self._login(self.driver)
        time.sleep(5) # To have time to accept notification if new device
        return login_info
    
    def extract_groups(self) -> Union[List[str], List[Tuple[str, str]]]:
        """
        Extract groups
        
        Returns:
            List of group URLs or (name, url) tuples
        """
        return self._extract_groups(self.driver)
    
    def publish_to_specific_groups(self, groups: Union[List[str], List[Tuple[str, str]]],
                                 post_content: Optional[str] = None,
                                 post_title: Optional[str] = None) -> dict:
        """
        Publish posts to specific groups without extracting

        Args:
            groups: List of group URLs or (name, url) tuples
            post_content: Content to post (uses config default if None)
            post_title: Title for the post (uses config default if None)

        Returns:
            dict: Execution statistics
        """
        if post_content is None:
            post_content = self.config.post_text
        if post_title is None:
            post_title = self.config.post_title

        return self.post_publisher.bulk_publish(
            self.driver, groups, post_content,
            post_title=post_title,
            dry_run=self.config.automation.dry_run,
            max_groups=self.config.automation.max_groups
        )
    
    def _login(self, driver) -> bool:
        """Handle login process"""
        logger.info("Attempting to login...")
        
        if self.authenticator.is_logged_in(driver):
            logger.info("Already logged in")
            return True
        
        return self.authenticator.login(driver)
    
    def _extract_groups(self, driver) -> Union[List[str], List[Tuple[str, str]]]:
        """Extract groups based on configuration"""
        logger.info("Extracting groups...")
        
        groups = self.group_extractor.extract_group_links_with_names(driver)
        
        logger.info(f"Extracted {len(groups)} groups")
        return groups
    
    def _publish_posts(self, driver, groups: list) -> dict:
        """Publish posts to extracted groups"""
        logger.info("Starting post publication...")

        return self.post_publisher.bulk_publish(
            driver, groups, self.config.post_text,
            post_title=self.config.post_title,
            dry_run=self.config.automation.dry_run,
            max_groups=self.config.automation.max_groups
        )
    
    def _create_error_stats(self, error_message: str) -> dict:
        """Create error statistics dictionary"""
        return {
            'successful': 0,
            'failed': 0,
            'total': 0,
            'success_rate': 0.0,
            'error': error_message
        }
    
    def update_config(self, **kwargs):
        """
        Update configuration at runtime
        
        Args:
            **kwargs: Configuration parameters to update
        """
        for key, value in kwargs.items():
            if hasattr(self.config.automation, key):
                setattr(self.config.automation, key, value)
                logger.info(f"Updated config: {key} = {value}")
            else:
                logger.warning(f"Unknown configuration parameter: {key}")
    
    def get_stats_summary(self, stats: dict) -> str:
        """
        Generate a human-readable summary of execution statistics
        
        Args:
            stats: Statistics dictionary from execution
            
        Returns:
            str: Formatted summary
        """
        if 'error' in stats:
            return f"❌ Automation failed: {stats['error']}"
        
        summary = f"""
            📊 Automation Results Summary:
            • Total groups processed: {stats['total']}
            • Successful posts: {stats['successful']} ✅
            • Failed posts: {stats['failed']} ❌
            • Success rate: {stats['success_rate']:.1f}%
            • Mode: {'Test Mode (no actual posting)' if self.config.automation.dry_run else 'Live Posting'}
        """.strip()
        
        return summary
