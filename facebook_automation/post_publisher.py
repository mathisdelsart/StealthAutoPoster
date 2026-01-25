"""
Facebook post publishing module
"""
import logging
from typing import Optional
from .config import Config
from .human_behavior import HumanBehavior
from .driver_manager import WebDriverManager

logger = logging.getLogger(__name__)


class PostPublisher:
    """Handles publishing posts to Facebook groups"""
    
    def __init__(self, config: Config, human_behavior: HumanBehavior, driver_manager: WebDriverManager):
        self.config = config
        self.human = human_behavior
        self.driver_manager = driver_manager
    
    def publish_to_group(self, driver, group_name: str, group_url: str, 
                        post_content: str, dry_run: bool = False) -> bool:
        """
        Publish a post to a specific Facebook group
        
        Args:
            driver: WebDriver instance
            group_name: Name of the group
            group_url: URL of the group
            post_content: Content to post
            dry_run: If True, prepare post without actually publishing
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"Publishing to group: {group_name}")
            
            # Navigate to group
            if not self._navigate_to_group(driver, group_url, group_name):
                return False
            
            # Find and click post composition area
            if not self._click_post_composition_area(driver, group_name):
                return False
            
            # Input post content
            if not self._input_post_content(driver, post_content, group_name):
                return False
            
            if dry_run:
                logger.info(f"[DRY RUN] Post prepared for {group_name} (not published)")
                return True
            
            # Publish the post
            return self._publish_post(driver, group_name)
            
        except Exception as e:
            logger.error(f"❌ Error publishing to {group_name}: {e}")
            return False
    
    def _navigate_to_group(self, driver, group_url: str, group_name: str) -> bool:
        """Navigate to the Facebook group"""
        try:
            driver.get(group_url)
            self.human.pause_like_human(3, 5)
            
            # Verify we're in a valid group page
            if "/groups/" not in driver.current_url:
                logger.warning(f"Invalid URL for {group_name}: {driver.current_url}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error navigating to {group_name}: {e}")
            return False
    
    def _click_post_composition_area(self, driver, group_name: str) -> bool:
        """Find and click the post composition area"""
        try:
            # Find post composition area using multiple selectors
            post_box = self.driver_manager.find_element_with_selectors(
                self.config.selectors.write_selectors
            )
            
            if not post_box:
                logger.error(f"Post composition area not found for {group_name}")
                return False
            
            # Click with human-like behavior
            self.human.human_like_click(driver, post_box)
            self.human.pause_like_human(1, 2)
            
            return True
            
        except Exception as e:
            logger.error(f"Error clicking post composition area for {group_name}: {e}")
            return False
            
    
    def _input_post_content(self, driver, post_content: str, group_name: str) -> bool:
        """Input the post content into the active text area"""
        try:
            # Get the active element (should be the text input)
            active_element = driver.switch_to.active_element
            
            if not active_element:
                logger.error(f"No active text element found for {group_name}")
                return False
            
            # Input text using human-like behavior
            self.human.input_text(active_element, post_content)
            self.human.pause_like_human(1, 2)
            
            logger.info(f"Post content entered for {group_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error inputting post content for {group_name}: {e}")
            return False
    
    def _publish_post(self, driver, group_name: str) -> bool:
        """Find and click the publish button"""
        try:
            # Find publish button using multiple selectors
            publish_button = self.driver_manager.find_element_with_selectors(
                self.config.selectors.post_selectors, wait_time=5
            )
            
            if not publish_button:
                logger.error(f"Publish button not found for {group_name}")
                return False
            
            # Human-like delay before publishing
            self.human.pause_like_human(2, 4)
            
            # Click publish with human-like behavior
            self.human.human_like_click(driver, publish_button)
            
            # Wait a moment to confirm publication
            self.human.pause_like_human(2, 3)
            
            logger.info(f"✅ Post published successfully in {group_name}!")
            return True
            
        except Exception as e:
            logger.error(f"Error publishing post for {group_name}: {e}")
            return False
    
    def bulk_publish(self, driver, groups: list, post_content: str, 
                    dry_run: bool = False, max_groups: Optional[int] = None) -> dict:
        """
        Publish to multiple groups
        
        Args:
            driver: WebDriver instance
            groups: List of groups (can be URLs or (name, url) tuples)
            post_content: Content to post
            dry_run: If True, don't actually publish
            max_groups: Maximum number of groups to process
            
        Returns:
            dict: Statistics about the publishing process
        """
        stats = {
            'successful': 0,
            'failed': 0,
            'total': 0,
            'success_rate': 0.0
        }
        
        # Limit groups if requested
        if max_groups:
            groups = groups[:max_groups]
        
        stats['total'] = len(groups)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"STARTING PUBLICATION TO {len(groups)} GROUPS")
        logger.info(f"Mode: {'TEST (no actual posting)' if dry_run else 'LIVE POSTING'}")
        logger.info(f"{'='*60}")
        
        for i, group in enumerate(groups, 1):
            # Handle different group formats
            if isinstance(group, tuple):
                group_name, group_url = group
            else:
                group_name = f"Group {i}"
                group_url = group
            
            logger.info(f"\n--- Processing Group {i}/{len(groups)} ---")
            logger.info(f"Group: {group_name}")
            logger.info(f"URL: {group_url}")
            
            # Publish to group
            success = self.publish_to_group(
                driver, group_name, group_url, post_content, dry_run
            )
            
            if success:
                stats['successful'] += 1
            else:
                stats['failed'] += 1
            
            # Human-like delay between posts (except for last group)
            if i < len(groups):
                delay = self.human.post_delay()
                logger.info(f"Waiting {delay:.1f}s before next group...")
        
        # Calculate success rate
        if stats['total'] > 0:
            stats['success_rate'] = (stats['successful'] / stats['total']) * 100
        
        self._print_final_stats(stats, dry_run)
        return stats
    
    def _print_final_stats(self, stats: dict, dry_run: bool):
        """Print final execution statistics"""
        print("\n" + "="*60)
        print("EXECUTION SUMMARY")
        print("="*60)
        print(f"✅ Successful posts: {stats['successful']}")
        print(f"❌ Failed posts: {stats['failed']}")
        print(f"📊 Success rate: {stats['success_rate']:.1f}%")
        print(f"🎯 Mode: {'Test Mode' if dry_run else 'Live Posting'}")
        print("="*60)
