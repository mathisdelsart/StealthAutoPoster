"""
Facebook authentication module
"""
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from .config import Config
from .human_behavior import HumanBehavior

logger = logging.getLogger(__name__)


class FacebookAuthenticator:
    """Handles Facebook login with anti-detection measures"""
    
    def __init__(self, config: Config, human_behavior: HumanBehavior):
        self.config = config
        self.human = human_behavior
    
    def login(self, driver) -> bool:
        """
        Automated Facebook login with anti-detection measures

        Args:
            driver: Selenium WebDriver instance

        Returns:
            bool: True if login successful, False otherwise

        Raises:
            ValueError: If credentials are not configured
        """
        logger.info("Starting Facebook login process...")

        try:
            # Navigate to Facebook login page
            logger.info("Navigating to Facebook login page...")
            driver.get("https://www.facebook.com/login")

            # Wait for page to load
            self.human.page_load_delay()

            # Handle cookie consent dialog if present
            self._handle_cookie_consent(driver)

            # Locate and fill email field
            if not self._fill_email_field(driver):
                return False
            
            # Human-like pause between email and password
            self.human.pause_like_human(1.0, 2.5)
            
            # Locate and fill password field
            if not self._fill_password_field(driver):
                return False
            
            # Another human-like pause before clicking login
            self.human.pause_like_human(0.5, 1.5)
            
            # Click login button
            if not self._click_login_button(driver):
                return False
            
            # Wait for successful login
            return self._wait_for_login_success(driver)
            
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False
    
    def _handle_cookie_consent(self, driver) -> None:
        """Dismiss the cookie consent dialog if present"""
        # Quick check: see if any cookie banner exists before trying specific buttons
        try:
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-cookiebanner]'))
            )
        except TimeoutException:
            logger.debug("No cookie consent dialog detected")
            return

        logger.info("Cookie consent dialog detected, attempting to accept...")
        cookie_button_selectors = [
            (By.CSS_SELECTOR, 'button[data-cookiebanner="accept_button"]'),
            (By.CSS_SELECTOR, 'button[data-cookiebanner="accept_only_essential_button"]'),
            (By.XPATH, '//button[contains(text(), "Allow all cookies")]'),
            (By.XPATH, '//button[contains(text(), "Accept all")]'),
            (By.XPATH, '//button[contains(text(), "Tout accepter")]'),
            (By.XPATH, '//button[contains(text(), "Autoriser tous les cookies")]'),
            (By.XPATH, '//button[contains(text(), "Autoriser les cookies essentiels et facultatifs")]'),
        ]

        for by, selector in cookie_button_selectors:
            try:
                button = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((by, selector))
                )
                button.click()
                logger.info("Cookie consent accepted")
                self.human.pause_like_human(1.0, 2.0)
                return
            except TimeoutException:
                continue

        logger.warning("Cookie banner detected but could not find accept button")

    def _fill_email_field(self, driver) -> bool:
        """Fill email field with human-like behavior"""
        try:
            logger.debug("Locating email input field...")
            email_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            logger.debug("Email field found successfully")
            
            logger.info("Entering email address...")
            self.human.type_slowly(email_field, self.config.credentials.email)
            return True
            
        except TimeoutException:
            logger.error("Email field not found")
            return False
        except Exception as e:
            logger.error(f"Error filling email field: {e}")
            return False
    
    def _fill_password_field(self, driver) -> bool:
        """Fill password field with human-like behavior"""
        try:
            logger.debug("Locating password input field...")
            password_field = driver.find_element(By.ID, "pass")
            logger.debug("Password field found successfully")
            
            logger.info("Entering password...")
            # Use slow typing for password (more secure feeling)
            self.human.type_slowly(password_field, self.config.credentials.password)
            return True
            
        except Exception as e:
            logger.error(f"Error filling password field: {e}")
            return False
    
    def _click_login_button(self, driver) -> bool:
        """Click login button with human-like behavior"""
        try:
            logger.debug("Locating login button...")
            login_button = driver.find_element(By.NAME, "login")
            logger.debug("Login button found successfully")
            
            logger.info("Clicking login button...")

            # Use JavaScript to click the button because it's not clickable with 'human_like_click'
            # since there is the cookie consent popup that blocks the login button
            driver.execute_script("arguments[0].click();", login_button)

            return True
            
        except Exception as e:
            logger.error(f"Error clicking login button: {e}")
            return False
    
    def _wait_for_login_success(self, driver) -> bool:
        """Wait for login to complete successfully"""
        try:
            logger.info("Waiting for login to complete...")
            WebDriverWait(driver, 15).until(
                lambda driver: "facebook.com" in driver.current_url and "login" not in driver.current_url
            )
            
            logger.info("✅ Login successful!")
            
            # Long pause to have time to accept verification on main device
            self.human.pause_like_human(10.0, 20.0)
            
            return True
            
        except TimeoutException:
            logger.error("Login timeout - login may have failed")
            return False
        except Exception as e:
            logger.error(f"Error waiting for login success: {e}")
            return False
    
    def is_logged_in(self, driver) -> bool:
        """
        Check if user is currently logged in
        
        Args:
            driver: WebDriver instance
            
        Returns:
            bool: True if logged in, False otherwise
        """
        try:
            current_url = driver.current_url
            return "facebook.com" in current_url and "login" not in current_url
        except:
            return False
