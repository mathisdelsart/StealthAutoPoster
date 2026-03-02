"""
Human-like behavior simulation for automation
"""
import time
import random
import platform
import pyperclip
import logging
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from .config import Config

logger = logging.getLogger(__name__)


class HumanBehavior:
    """Simulates human-like behavior for web automation"""
    
    def __init__(self, config: Config):
        self.config = config
    
    def random_delay(self, min_seconds: float, max_seconds: float) -> float:
        """Generate random delay within specified range"""
        delay = random.uniform(min_seconds, max_seconds)
        logger.debug(f"Random delay: {delay:.2f}s")
        time.sleep(delay)
        return delay
    
    def typing_delay(self) -> float:
        """Generate typing delay"""
        return self.random_delay(
            self.config.automation.typing_delay_min,
            self.config.automation.typing_delay_max
        )
    
    def page_load_delay(self) -> float:
        """Generate page load delay"""
        return self.random_delay(
            self.config.automation.page_load_delay_min,
            self.config.automation.page_load_delay_max
        )
    
    def post_delay(self) -> float:
        """Generate delay between posts"""
        return self.random_delay(
            self.config.automation.post_delay_min,
            self.config.automation.post_delay_max
        )
    
    def type_slowly(self, element, text: str):
        """
        Types text character by character with random delays to mimic human behavior
        
        Args:
            element: WebDriver element to type into
            text: Text string to type
        """
        logger.debug(f"Starting slow typing for text of length {len(text)}")
        element.clear()
        
        for char in text:
            element.send_keys(char)
            # Random delay between each character
            delay = random.uniform(
                self.config.automation.typing_delay_min,
                self.config.automation.typing_delay_max
            )
            time.sleep(delay)
        
        logger.debug("Slow typing completed successfully")
    
    def paste_text(self, driver, element, text: str) -> bool:
        """
        Insert multi-line text into a contenteditable element.

        Uses document.execCommand('insertText') which is the most reliable
        way to insert multi-line text into Facebook's React contenteditable.

        Args:
            driver: WebDriver instance
            element: WebDriver element to paste into
            text: Text to paste

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Clipboard paste (Cmd+V / Ctrl+V) - preserves newlines in contenteditable
            pyperclip.copy(text)
            actions = ActionChains(driver)
            actions.click(element)
            if platform.system() == "Darwin":
                actions.key_down(Keys.COMMAND).send_keys('v').key_up(Keys.COMMAND)
            else:
                actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL)
            actions.perform()
            time.sleep(1)
            logger.info(f"Text pasted via clipboard ({len(text)} chars)")
            return True

        except Exception as e:
            logger.warning(f"Paste operation failed: {e}")
            return False
    
    def input_text(self, element, text: str, driver=None):
        """
        Input text using either clipboard paste or slow typing

        Args:
            element: WebDriver element to input text into
            text: Text to input
            driver: WebDriver instance (needed for paste)
        """
        line_count = text.count('\n') + 1
        logger.info(f"Inputting text: {len(text)} chars, {line_count} lines")

        # Try JS-based paste first (most reliable for multi-line in contenteditable)
        if driver and self.paste_text(driver, element, text):
            return
        # Fall back to slow typing
        logger.info("Using manual typing as fallback")
        self.type_slowly(element, text)
    
    def human_like_click(self, driver, element):
        """
        Perform human-like click with movement and delay
        
        Args:
            driver: WebDriver instance
            element: Element to click
        """
        # Scroll element into view
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        time.sleep(random.uniform(0.2, 0.5))

        # Use ActionChains for more natural clicking
        actions = ActionChains(driver)
        actions.move_to_element(element)

        # Small random delay before click
        time.sleep(random.uniform(0.1, 0.3))
        
        actions.click().perform()
        logger.debug("Human-like click performed")
    
    def human_like_scroll(self, driver, pixels: int = None):
        """
        Perform human-like scrolling
        
        Args:
            driver: WebDriver instance
            pixels: Pixels to scroll (random if not specified)
        """
        if pixels is None:
            pixels = random.randint(300, 800)
        
        # Smooth scroll with random variations
        scroll_steps = random.randint(3, 7)
        step_size = pixels // scroll_steps
        
        current_scroll = driver.execute_script("return window.pageYOffset;")
        
        for i in range(scroll_steps):
            current_scroll += step_size + random.randint(-50, 50)
            driver.execute_script(f"window.scrollTo(0, {current_scroll});")
            time.sleep(random.uniform(0.1, 0.3))
    
    def pause_like_human(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """
        Pause execution to simulate human thinking/reading time
        
        Args:
            min_seconds: Minimum pause duration
            max_seconds: Maximum pause duration
        """
        duration = self.random_delay(min_seconds, max_seconds)
        logger.debug(f"Human-like pause: {duration:.2f}s")
