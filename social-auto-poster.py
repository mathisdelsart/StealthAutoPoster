from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from dotenv import load_dotenv
import pyperclip
import time
import platform
import random
import logging
import os

# Logging Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

POST_TEXT = os.environ.get('POST_TEXT')

MY_GROUPS_URL = "https://www.facebook.com/groups/joins/?nav_source=tab&ordering=viewer_added"

WRITE_SELECTORS = [
    '//span[contains(text(), "Exprimez-vous")]/ancestor::div[@role="button"]'
]

POST_SELECTORS = [
    '//div[@aria-label="Publier" and @role="button"]',
    '//span[text()="Publier"]/parent::div[@role="button"]',
    '//span[text()="Publier"]/ancestor::div[@role="button"]',
    '//div[contains(text(), "Publier") and @role="button"]'
]


def initialize_webdriver():
    """
    Initialize Chrome WebDriver with enhanced stealth options for better automation detection avoidance.
    
    Returns:
        webdriver.Chrome: Configured Chrome WebDriver instance
        
    Raises:
        Exception: If WebDriver initialization fails
    """
    chrome_options = Options()
    
    # Basic stealth options
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    chrome_options.add_argument("--disable-save-password-bubble")
    chrome_options.add_argument("--disable-password-generation")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-default-apps")

    prefs = {
        "profile.default_content_setting_values.notifications": 2,
        "profile.password_manager_enabled": False,
        "profile.default_content_settings.popups": 0,
        "credentials_enable_service": False,
        "profile.password_manager_leak_detection": False
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    # Realistic user agent
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    
    try:
        driver = webdriver.Chrome(options=chrome_options)

        # Execute JavaScript to mask automation detection
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            """
        })

        logger.info("WebDriver initialized successfully")
        return driver

    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation du driver: {e}")
        raise


def scroll_to_page_bottom(driver, max_scrolls=10):
    """
    Scroll to the bottom of the page to load all dynamic content.
    
    Args:
        driver: WebDriver instance
        max_scrolls (int): Maximum number of scroll attempts
    """
    logger.info("Starting page scroll to load all groups...")
    
    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_count = 0
    
    while scroll_count < max_scrolls:
        # Progressive scrolling
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # Intelligent wait with randomization
        time.sleep(random.uniform(2, 3))
        
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            logger.info("Reached end of content")
            break
            
        last_height = new_height
        scroll_count += 1
        logger.info(f"Scroll {scroll_count}/{max_scrolls} completed")
    
    # Return to top of page
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(1)


def extract_group_links(driver):
    """
    Extract and filter Facebook group links from the current page.
    
    Args:
        driver: WebDriver instance
        
    Returns:
        list: List of tuples containing (group_name, group_url)
    """
    logger.info("Navigating to Facebook groups page...")
    driver.get(MY_GROUPS_URL)

    time.sleep(1)

    scroll_to_page_bottom(driver)
    
    time.sleep(2)
    
    all_links = driver.find_elements(By.XPATH, '//a[@role="link" and @aria-label]')
    groups = []
    
    excluded_terms = ["user/", "permalink", "create", "joins", "category", "events", "members", "photos"]
    
    for link in all_links:
        try:
            href = link.get_attribute("href")
            name = link.get_attribute("aria-label")
            
            if not href or not name:
                continue
            
            # Filter valid group URLs
            if "/groups/" in href and href.count("/groups/") == 1:
                # Exclude unwanted URLs
                if any(term in href for term in excluded_terms):
                    continue
                    
                # Avoid duplicates
                if href not in [grp[1] for grp in groups]:
                    groups.append((name, href))
                    logger.info(f"Group discovered: {name}")
                    
        except Exception as e:
            logger.warning(f"Error processing link: {e}")
            continue

    logger.info(f"Total groups found: {len(groups)}")
    return groups


def type_slowly(element, text, min_delay=0.1, max_delay=0.3):
    """
    Types text character by character with random delays to mimic human behavior
    
    Args:
        element: WebDriver element to type into
        text: Text string to type
        min_delay: Minimum delay between characters in seconds
        max_delay: Maximum delay between characters in seconds
    """
    logger.debug(f"Starting slow typing for text of length {len(text)}")
    element.clear()
    
    for char in text:
        element.send_keys(char)
        # Random delay between each character to simulate human typing speed variation
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    logger.debug("Slow typing completed successfully")


def facebook_login(driver):
    """
    Automated Facebook login with anti-detection measures
    
    Args:
        driver: Selenium WebDriver instance
        
    Raises:
        ValueError: If environment variables are not set
        TimeoutException: If login elements are not found or login fails
    """
    logger.info("Starting Facebook login process...")
    
    # Retrieve credentials from environment variables for security
    email = os.environ.get('FACEBOOK_EMAIL')
    password = os.environ.get('FACEBOOK_PASSWORD')
    
    if not email or not password:
        logger.error("Missing environment variables for Facebook credentials")
        raise ValueError("Environment variables FACEBOOK_EMAIL and FACEBOOK_PASSWORD are required")
    
    logger.debug("Credentials loaded from environment variables")
    
    # Navigate to Facebook login page
    logger.info("Navigating to Facebook login page...")
    driver.get("https://www.facebook.com/login")
    
    # Wait for page to load completely
    page_load_delay = random.uniform(2, 4)
    logger.debug(f"Waiting {page_load_delay:.1f}s for page to load")
    time.sleep(page_load_delay)
    
    try:
        # Wait for and locate email input field
        logger.debug("Locating email input field...")
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        logger.debug("Email field found successfully")
        
        # Type email slowly with human-like delays
        logger.info("Entering email address...")
        type_slowly(email_field, email, min_delay=0.05, max_delay=0.25)
        
        # Natural pause between filling email and password (human behavior)
        pause_duration = random.uniform(1, 2.5)
        logger.debug(f"Pausing {pause_duration:.1f}s between email and password entry")
        time.sleep(pause_duration)
        
        # Locate password input field
        logger.debug("Locating password input field...")
        password_field = driver.find_element(By.ID, "pass")
        logger.debug("Password field found successfully")
        
        # Type password slowly with slightly longer delays (more careful with passwords)
        logger.info("Entering password...")
        type_slowly(password_field, password, min_delay=0.1, max_delay=0.3)
        
        # Another human-like pause before clicking login
        pre_login_pause = random.uniform(0.5, 1.5)
        logger.debug(f"Pausing {pre_login_pause:.1f}s before clicking login")
        time.sleep(pre_login_pause)
        
        # Locate login button
        logger.debug("Locating login button...")
        login_button = driver.find_element(By.NAME, "login")
        logger.debug("Login button found successfully")
        
        # Scroll to ensure button is visible (prevents click interception)
        logger.debug("Scrolling to login button...")
        driver.execute_script("arguments[0].scrollIntoView(true);", login_button)
        time.sleep(random.uniform(0.5, 1))
        
        # Click login button
        logger.info("Clicking login button...")
        driver.execute_script("arguments[0].click();", login_button)
        
        # Wait for successful login (URL change indicates success)
        logger.info("Waiting for login to complete...")
        WebDriverWait(driver, 15).until(
            lambda driver: "facebook.com" in driver.current_url and "login" not in driver.current_url
        )
        
        logger.info("✅ Login successful!")

        time.sleep(random.uniform(2, 5))
        
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise


def find_element_with_multiple_selectors(driver, selectors, wait_time=10):
    """
    Attempt to find an element using multiple XPath selectors.
    
    Args:
        driver: WebDriver instance
        selectors (list): List of XPath selectors to try
        wait_time (int): Maximum wait time for element
        
    Returns:
        WebElement or None: Found element or None if not found
    """
    wait = WebDriverWait(driver, wait_time)
    
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


def simulate_human_typing(element, text, delay_range=(0.05, 0.15)):
    """
    Simulate human-like typing behavior with random delays.
    
    Args:
        element: WebElement to type into
        text (str): Text to type
        delay_range (tuple): Range of delays between keystrokes
    """
    logger.debug("Simulating human typing...")
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(*delay_range))


def publish_group_post(driver, group_name, group_url, post_content, dry_run=False):
    """
    Publish a post to a specific Facebook group with comprehensive error handling.
    
    Args:
        driver: WebDriver instance
        group_name (str): Name of the group
        group_url (str): URL of the group
        post_content (str): Content to post
        dry_run (bool): If True, prepare post without actually publishing
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Navigate to group
        driver.get(group_url)
        time.sleep(random.uniform(3, 5))
        
        # Verify we're in a valid group page
        if "/groups/" not in driver.current_url:
            logger.warning(f"Invalid URL for {group_name}: {driver.current_url}")
            return False
        
        # Find post composition area
        post_box = find_element_with_multiple_selectors(driver, WRITE_SELECTORS)
        if not post_box:
            logger.error(f"Post composition area not found for {group_name}")
            return False
        
        # Scroll to element and click
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", post_box)
        time.sleep(1)
        
        # Use ActionChains for more natural clicking
        actions = ActionChains(driver)
        actions.move_to_element(post_box).click().perform()
        time.sleep(2)
        
        # Text input handling
        active_element = driver.switch_to.active_element
        if active_element:
            try:
                # Attempt clipboard paste first (faster and more reliable)
                pyperclip.copy(post_content)

                if platform.system() == "Darwin":
                    active_element.send_keys(Keys.COMMAND, 'v')
                else:
                    active_element.send_keys(Keys.CONTROL, 'v')

                time.sleep(2)
                
                # Verify paste operation success
                current_text = active_element.get_attribute("textContent") or active_element.get_attribute("innerText") or ""
                if len(current_text.strip()) < len(post_content.strip()) * 0.8:  # At least 80% of text
                    logger.warning("Clipboard paste failed, attempting manual typing...")
                    active_element.clear()
                    simulate_human_typing(active_element, post_content)
                else:
                    logger.debug("Clipboard paste successful")
                
            except Exception as e:
                logger.warning(f"Clipboard operation failed: {e}, using manual typing")
                simulate_human_typing(active_element, post_content)
        
        time.sleep(2)
        
        if dry_run:
            logger.info(f"[DRY RUN] Post prepared for {group_name} (not published)")
            return True
        
        # Find and click publish button
        publish_button = find_element_with_multiple_selectors(driver, POST_SELECTORS, wait_time=5)
        if not publish_button:
            logger.error(f"Publish button not found for {group_name}")
            return False
        
        # Human-like delay before publishing
        time.sleep(random.uniform(2, 4))
        
        # Click publish
        actions = ActionChains(driver)
        actions.move_to_element(publish_button).click().perform()
        
        logger.info(f"✅ Post published successfully in {group_name}!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error publishing to {group_name}: {e}")
        return False


def main():
    """
    Main execution function with enhanced error handling and user configuration options.
    """
    driver = None
    
    try:
        # User configuration options
        print("\n" + "="*60)
        print("FACEBOOK GROUP AUTO-POSTER CONFIGURATION")
        print("="*60)

        dry_run = os.getenv("DRY_RUN", "true").lower() == "true"

        max_groups_input = os.getenv("MAX_GROUPS", "").strip()
        max_groups = int(max_groups_input) if max_groups_input.isdigit() else None

        logger.info("Initializing browser...")
        driver = initialize_webdriver()
        
        print("\n" + "="*60)
        print("FACEBOOK LOGIN REQUIRED")
        print("="*60)
        print("1. Please log in to Facebook in the opened browser")
        print("="*60)

        facebook_login(driver)
        
        logger.info("Discovering groups...")
        groups = extract_group_links(driver)
        
        if not groups:
            logger.error("No groups found! Please check your login status and group memberships.")
            return
        
        logger.info(f"✅ {len(groups)} groups discovered")
        
        # Limit groups if requested
        if max_groups:
            groups = groups[:max_groups]
            logger.info(f"Limited to {len(groups)} groups as requested")
        
        # Execution statistics
        successful_posts = 0
        failed_posts = 0
        
        print(f"\n{'='*60}")
        print(f"STARTING PUBLICATION TO {len(groups)} GROUPS")
        print(f"Mode: {'TEST (no actual posting)' if dry_run else 'LIVE POSTING'}")
        print(f"{'='*60}")
        
        # Process each group
        for i, (name, url) in enumerate(groups, 1):
            logger.info(f"\n--- Processing Group {i}/{len(groups)} ---")
            
            success = publish_group_post(driver, name, url, POST_TEXT, dry_run)
            
            if success:
                successful_posts += 1
            else:
                failed_posts += 1
            
            # Human-like delay between posts
            delay = random.uniform(5, 10)
            logger.info(f"Waiting {delay:.1f}s before next group...")
            time.sleep(delay)
    
        # Final execution summary
        print("\n" + "="*60)
        print("EXECUTION SUMMARY")
        print("="*60)
        print(f"✅ Successful posts: {successful_posts}")
        print(f"❌ Failed posts: {failed_posts}")
        total_attempts = successful_posts + failed_posts
        success_rate = (successful_posts / total_attempts * 100) if total_attempts > 0 else 0
        print(f"📊 Success rate: {success_rate:.1f}%")
        print(f"🎯 Mode: {'Test Mode' if dry_run else 'Live Posting'}")
        print("="*60)
        
    except KeyboardInterrupt:
        logger.info("Execution interrupted by user")
        print("\n⚠️ Process interrupted by user")
        
    except Exception as e:
        logger.error(f"Critical error during execution: {e}")
        print(f"\n❌ Critical error: {e}")
        
    finally:
        if driver:
            logger.info("Closing browser...")
            try:
                driver.quit()
            except:
                pass


if __name__ == "__main__":
    main()
