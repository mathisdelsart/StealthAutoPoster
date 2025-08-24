"""
WebDriver management and initialization
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from typing import List, Optional
import logging
from .config import Config

logger = logging.getLogger(__name__)


class WebDriverManager:
    """Manages Chrome WebDriver instance with stealth configuration"""
    
    def __init__(self, config: Config):
        self.config = config
        self.driver: Optional[webdriver.Chrome] = None
    
    def initialize_driver(self) -> webdriver.Chrome:
        """
        Initialize Chrome WebDriver with enhanced stealth options
        
        Returns:
            webdriver.Chrome: Configured Chrome WebDriver instance
            
        Raises:
            Exception: If WebDriver initialization fails
        """
        chrome_options = Options()
        
        # Add all chrome arguments
        for arg in self.config.chrome_options_args:
            chrome_options.add_argument(arg)
        
        # Add preferences
        chrome_options.add_experimental_option("prefs", self.config.chrome_prefs)
        
        # Anti-detection options
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # Execute JavaScript to mask automation detection
            self._setup_stealth_mode()
            
            logger.info("WebDriver initialized successfully")
            return self.driver
            
        except Exception as e:
            logger.error(f"Error initializing WebDriver: {e}")
            raise
    
    def _setup_stealth_mode(self):
        """Configure stealth mode to avoid automation detection"""
        if not self.driver:
            return
            
        # Execute JavaScript to mask automation detection
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            """
        })
    
    def find_element_with_selectors(self, selectors: List[str], wait_time: int = 10) -> Optional:
        """
        Attempt to find an element using multiple XPath selectors
        
        Args:
            selectors: List of XPath selectors to try
            wait_time: Maximum wait time for element
            
        Returns:
            WebElement or None: Found element or None if not found
        """
        if not self.driver:
            return None
            
        wait = WebDriverWait(self.driver, wait_time)
        
        for selector in selectors:
            try:
                element = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                logger.debug(f"Element found using selector: {selector}")
                return element
            except TimeoutException:
                logger.debug(f"Selector failed: {selector}")
                continue
        
        logger.warning("No element found with any of the provided selectors")
        return None
    
    def close(self):
        """Close the WebDriver instance"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver closed successfully")
            except Exception as e:
                logger.warning(f"Error closing WebDriver: {e}")
            finally:
                self.driver = None
    
    def __enter__(self):
        """Context manager entry"""
        return self.initialize_driver()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
