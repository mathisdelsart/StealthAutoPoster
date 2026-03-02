"""
Facebook authentication module
"""
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
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
            
            # Locate and fill password field (also submits the form via Enter)
            if not self._fill_password_field(driver):
                return False

            # Wait for successful login
            return self._wait_for_login_success(driver)
            
        except Exception as e:
            logger.error(f"Login failed: {e}")
            self._save_debug_screenshot(driver, "login_failed")
            return False
    
    def _handle_cookie_consent(self, driver) -> None:
        """Dismiss the cookie consent dialog if present"""
        logger.info("Checking for cookie consent dialog...")

        # Use ActionChains to click the cookie button at its coordinates
        # This works with React apps where DOM manipulation breaks state
        try:
            # Find the "Autoriser tous les cookies" button via JS and get its position
            js_find_cookie_btn = """
            var texts = ["Autoriser tous les cookies", "Allow all cookies", "Tout accepter", "Accept all"];
            for (var i = 0; i < texts.length; i++) {
                var xpath = '//*[contains(., "' + texts[i] + '")]';
                var results = document.evaluate(xpath, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                var best = null;
                var bestSize = Infinity;
                for (var j = 0; j < results.snapshotLength; j++) {
                    var el = results.snapshotItem(j);
                    var rect = el.getBoundingClientRect();
                    var size = rect.width * rect.height;
                    if (size > 0 && size < bestSize && rect.width > 50) {
                        best = el;
                        bestSize = size;
                    }
                }
                if (best) {
                    var r = best.getBoundingClientRect();
                    return {x: r.x + r.width/2, y: r.y + r.height/2, text: texts[i]};
                }
            }
            return null;
            """

            self.human.pause_like_human(1.0, 2.0)
            btn_info = driver.execute_script(js_find_cookie_btn)

            if btn_info:
                logger.info(f"Cookie button found: '{btn_info['text']}' at ({btn_info['x']}, {btn_info['y']})")
                # Click at the exact coordinates using ActionChains
                actions = ActionChains(driver)
                actions.move_by_offset(int(btn_info['x']), int(btn_info['y'])).click().perform()
                actions.reset_actions()
                logger.info("Cookie consent accepted via coordinate click")
                self.human.pause_like_human(1.0, 2.0)
            else:
                logger.debug("No cookie consent dialog found")
        except Exception as e:
            logger.warning(f"Cookie consent handling error: {e}")

    def _find_element_with_fallbacks(self, driver, selectors, timeout=10):
        """Try multiple selectors to find an element"""
        for by, selector in selectors:
            try:
                element = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((by, selector))
                )
                logger.debug(f"Element found with selector: {selector}")
                return element
            except TimeoutException:
                logger.debug(f"Selector not found: {selector}")
                continue
        return None

    def _save_debug_screenshot(self, driver, name: str) -> None:
        """Save a screenshot for debugging"""
        try:
            path = f"debug_{name}.png"
            driver.save_screenshot(path)
            logger.info(f"Debug screenshot saved: {path}")
            logger.info(f"Current URL: {driver.current_url}")
            logger.info(f"Page title: {driver.title}")
        except Exception as e:
            logger.warning(f"Could not save debug screenshot: {e}")

    def _fill_email_field(self, driver) -> bool:
        """Fill email field with human-like behavior"""
        try:
            logger.debug("Locating email input field...")
            email_selectors = [
                (By.ID, "email"),
                (By.NAME, "email"),
                (By.CSS_SELECTOR, 'input[type="email"]'),
                (By.CSS_SELECTOR, 'input[name="email"]'),
                (By.CSS_SELECTOR, 'input[data-testid="royal_email"]'),
                (By.XPATH, '//input[@autocomplete="username"]'),
            ]
            email_field = self._find_element_with_fallbacks(driver, email_selectors, timeout=5)

            if not email_field:
                logger.error("Email field not found with any selector")
                self._save_debug_screenshot(driver, "email_not_found")
                return False

            logger.info("Entering email address...")
            self.human.type_slowly(email_field, self.config.credentials.email)
            return True

        except Exception as e:
            logger.error(f"Error filling email field: {e}")
            self._save_debug_screenshot(driver, "email_error")
            return False
    
    def _fill_password_field(self, driver) -> bool:
        """Fill password field with human-like behavior"""
        try:
            logger.debug("Locating password input field...")
            password_selectors = [
                (By.ID, "pass"),
                (By.NAME, "pass"),
                (By.CSS_SELECTOR, 'input[type="password"]'),
                (By.CSS_SELECTOR, 'input[name="pass"]'),
                (By.CSS_SELECTOR, 'input[data-testid="royal_pass"]'),
                (By.XPATH, '//input[@autocomplete="current-password"]'),
            ]
            password_field = self._find_element_with_fallbacks(driver, password_selectors, timeout=5)

            if not password_field:
                logger.error("Password field not found with any selector")
                self._save_debug_screenshot(driver, "password_not_found")
                return False

            logger.info("Entering password...")
            self.human.type_slowly(password_field, self.config.credentials.password)

            # Submit the form by pressing Enter on the password field
            self.human.pause_like_human(0.3, 0.8)
            logger.info("Submitting login form via Enter key...")
            password_field.send_keys(Keys.RETURN)
            return True

        except Exception as e:
            logger.error(f"Error filling password field: {e}")
            self._save_debug_screenshot(driver, "password_error")
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
            self._save_debug_screenshot(driver, "login_timeout")
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
