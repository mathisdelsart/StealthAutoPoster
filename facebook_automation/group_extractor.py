"""
Facebook group extraction and discovery
"""
import time
import random
import logging
from typing import List, Tuple, Set
from selenium.webdriver.common.by import By
from .config import Config
from .human_behavior import HumanBehavior

logger = logging.getLogger(__name__)


class GroupExtractor:
    """Extracts Facebook group information and URLs"""
    
    def __init__(self, config: Config, human_behavior: HumanBehavior):
        self.config = config
        self.human = human_behavior
        self.excluded_terms = [
            "user/", "permalink", "create", "joins", "category", 
            "events", "members", "photos", "discover", "feed"
        ]
    
    def extract_group_urls(self, driver, max_iterations: int = 10) -> List[str]:
        """
        Extract URLs from Facebook groups using incremental scrolling
        
        Args:
            driver: WebDriver instance
            max_iterations: Maximum scroll iterations
            
        Returns:
            List of group URLs
        """
        logger.info("Starting incremental URL extraction...")
        
        driver.get(self.config.my_groups_url)
        self.human.pause_like_human(2, 4)
        
        all_urls = set()
        iterations_without_new = 0
        max_no_change = 5
        
        for iteration in range(max_iterations):
            logger.info(f"Iteration #{iteration + 1}")
            
            # Perform human-like scroll
            self.human.human_like_scroll(driver)
            self.human.pause_like_human(1, 3)
            
            # Get current URLs
            current_urls = self._get_group_urls_current_view(driver)
            
            # Track new URLs
            urls_before = len(all_urls)
            all_urls.update(current_urls)
            urls_after = len(all_urls)
            new_count = urls_after - urls_before
            
            logger.info(f"URLs found this view: {len(current_urls)}")
            logger.info(f"New URLs: {new_count}")
            logger.info(f"Total accumulated: {urls_after}")
            
            # Stop condition
            if new_count == 0:
                iterations_without_new += 1
                if iterations_without_new >= max_no_change:
                    logger.info(f"Stopping: no new URLs for {max_no_change} iterations")
                    break
            else:
                iterations_without_new = 0
        
        # Clean URLs
        all_urls = [url for url in list(all_urls) if url.endswith("/")]
        
        logger.info("\n=== FINAL RESULTS ===")
        logger.info(f"Total iterations: {iteration + 1}")
        logger.info(f"Total unique URLs: {len(all_urls)}")
        
        return list(all_urls)
    
    def extract_group_links_with_names(self, driver) -> List[Tuple[str, str]]:
        """
        Extract Facebook group links with names using aggressive scrolling
        
        Args:
            driver: WebDriver instance
            
        Returns:
            List of tuples containing (group_name, group_url)
        """
        logger.info("Navigating to Facebook groups page...")
        driver.get(self.config.my_groups_url)
        self.human.pause_like_human(8, 12)
        
        # Aggressive scroll to load all groups
        self._scroll_to_load_all_groups(driver)
        self.human.pause_like_human(3, 5)
        
        # Extract group information
        return self._extract_groups_with_names(driver)
    
    def _get_group_urls_current_view(self, driver) -> Set[str]:
        """Extract URLs from current view"""
        current_urls = set()
        
        try:
            # Find links containing "/groups/"
            links = driver.find_elements(By.XPATH, '//a[contains(@href, "/groups/")]')
            
            for link in links:
                href = link.get_attribute("href")
                if self._is_valid_group_url(href):
                    current_urls.add(href)
                    
        except Exception as e:
            logger.debug(f"Error extracting URLs: {e}")
        
        return current_urls
    
    def _is_valid_group_url(self, url: str) -> bool:
        """
        Validate if URL is a valid Facebook group URL
        
        Args:
            url: URL to validate
            
        Returns:
            bool: True if valid group URL
        """
        if not url or "/groups/" not in url:
            return False
        
        # Check for excluded terms
        if any(exclude in url for exclude in self.excluded_terms):
            return False
        
        # Must have a group ID
        try:
            group_id = url.split("/groups/")[1].split("/")[0].split("?")[0]
            return len(group_id) > 3
        except:
            return False
    
    def _scroll_to_load_all_groups(self, driver):
        """
        Aggressive scroll to load ALL Facebook groups
        
        Args:
            driver: WebDriver instance
        """
        max_time_minutes = self.config.automation.max_scroll_time_minutes
        logger.info(f"Starting scroll for {max_time_minutes} minutes to load all groups...")
        
        start_time = time.time()
        max_duration = max_time_minutes * 60
        
        previous_group_count = 0
        no_change_counter = 0
        max_no_change = 15
        
        scroll_position = 0
        scroll_increment = 800
        
        while time.time() - start_time < max_duration:
            # Scroll in increments
            scroll_position += scroll_increment
            driver.execute_script(f"window.scrollTo(0, {scroll_position});")
            
            # Wait for content to load
            self.human.pause_like_human(2, 4)
            
            # Count current groups
            current_links = driver.find_elements(
                By.XPATH, 
                '//a[@role="link" and @aria-label and contains(@href, "/groups/")]'
            )
            current_count = len(current_links)
            
            # Check for new groups
            if current_count == previous_group_count:
                no_change_counter += 1
                if no_change_counter >= max_no_change:
                    logger.info(f"No new groups found after {max_no_change} attempts, stopping scroll")
                    break
            else:
                no_change_counter = 0
            
            previous_group_count = current_count
            
            # Handle page bottom
            page_height = driver.execute_script("return document.body.scrollHeight")
            if scroll_position >= page_height:
                logger.info("Reached apparent page bottom, forcing more scroll...")
                
                # Force additional loading
                for _ in range(3):
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    self.human.pause_like_human(3, 5)
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height > page_height:
                        page_height = new_height
                        scroll_position = new_height
                        break
                else:
                    logger.info("Truly reached end of content")
                    break
        
        logger.info("Scroll completed. All groups loaded")
        
        # Return to top
        driver.execute_script("window.scrollTo(0, 0);")
        self.human.pause_like_human(1, 2)
    
    def _extract_groups_with_names(self, driver) -> List[Tuple[str, str]]:
        """
        Extract group names and URLs from the page
        
        Args:
            driver: WebDriver instance
            
        Returns:
            List of (group_name, group_url) tuples
        """
        all_links = driver.find_elements(By.XPATH, '//a[@role="link" and @aria-label]')
        groups = []
        
        for link in all_links:
            try:
                href = link.get_attribute("href")
                name = link.get_attribute("aria-label")

                if not href or not name:
                    continue
                
                # Filter valid group URLs
                if "/groups/" in href and href.count("/groups/") == 1:
                    # Exclude unwanted URLs
                    if any(term in href for term in self.excluded_terms):
                        continue
                    
                    # Avoid duplicates
                    if href not in [grp[1] for grp in groups]:
                        groups.append((name, href))
                        logger.info(f"Found group: {name} - {href}")
                        
            except Exception as e:
                logger.warning(f"Error processing link: {e}")
                continue
        
        logger.info(f"Total groups found: {len(groups)}")
        return groups
