from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
import random

# Configuration
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME", "manuj_rai_official")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD", "#ruhman0207")
MAX_SCROLL_ATTEMPTS = 15
BASE_DELAY = 2

class InstagramUnfollower:
    def __init__(self):
        self.options = Options()
        self._setup_options()
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=self.options
        )
        self.wait = WebDriverWait(self.driver, 20)

    def _setup_options(self):
        """Configure browser options"""
        self.options.add_argument("--start-maximized")
        self.options.add_argument("--disable-notifications")
        self.options.add_argument("--disable-infobars")
        self.options.add_argument("--disable-extensions")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option("useAutomationExtension", False)

    def _random_delay(self, multiplier=1):
        """Generate random delay to mimic human behavior"""
        time.sleep(BASE_DELAY * multiplier + random.uniform(0, 1.5))

    def login(self):
        """Handle Instagram login with improved reliability"""
        self.driver.get("https://www.instagram.com/accounts/login/")
        
        try:
            # Handle cookie consent
            self._random_delay(2)
            cookie_accept = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(),'Allow essential and optional cookies')]"))
            )
            cookie_accept.click()
        except TimeoutException:
            pass
        
        # Fill login form
        username_field = self.wait.until(EC.presence_of_element_located((By.NAME, "username")))
        username_field.send_keys(INSTAGRAM_USERNAME)
        
        password_field = self.driver.find_element(By.NAME, "password")
        password_field.send_keys(INSTAGRAM_PASSWORD)
        
        submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_button.click()
        
        # Handle post-login verification
        self._handle_post_login_checks()

    def _handle_post_login_checks(self):
        """Handle potential security checks after login"""
        try:
            # Check for "Save Info" prompt
            self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(),'Not Now')]")
            )).click()
            self._random_delay()
        except TimeoutException:
            pass

    def _get_follow_list(self, list_type):
        """Generic function to get followers/following list"""
        self._random_delay()
        scroll_box = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, "//div[@role='dialog']//div[@style='flex-direction: column;']")
        ))
        
        last_height = 0
        scroll_attempts = 0
        
        while scroll_attempts < MAX_SCROLL_ATTEMPTS:
            self.driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight", scroll_box
            )
            self._random_delay()
            new_height = self.driver.execute_script("return arguments[0].scrollTop", scroll_box)
            
            if new_height == last_height:
                break
                
            last_height = new_height
            scroll_attempts += 1

        return {user.text for user in scroll_box.find_elements(By.TAG_NAME, "a") if user.text}

    def unfollow_non_followers(self):
        """Main logic to unfollow non-followers"""
        # Get followers
        self.driver.get(f"https://www.instagram.com/{INSTAGRAM_USERNAME}/followers/")
        followers = self._get_follow_list("followers")
        print(f"Found {len(followers)} followers")
        
        # Get following
        self.driver.get(f"https://www.instagram.com/{INSTAGRAM_USERNAME}/following/")
        following = self._get_follow_list("following")
        print(f"Found {len(following)} following")
        
        non_followers = following - followers
        print(f"Found {len(non_followers)} non-followers to unfollow")
        
        for index, user in enumerate(non_followers, 1):
            try:
                self.driver.get(f"https://www.instagram.com/{user}/")
                self._random_delay(1.5)
                
                # Find and click unfollow button
                unfollow_btn = self.wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//button[.//div[contains(text(), 'Following')]]")
                ))
                unfollow_btn.click()
                
                # Confirm unfollow
                confirm_btn = self.wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(., 'Unfollow')]")
                ))
                confirm_btn.click()
                
                print(f"Unfollowed {user} ({index}/{len(non_followers)})")
                self._random_delay(random.choice([1, 2, 3]))
                
            except Exception as e:
                print(f"Failed to unfollow {user}: {str(e)}")
                continue

    def run(self):
        try:
            self.login()
            self.unfollow_non_followers()
        finally:
            self.driver.quit()

if __name__ == "__main__":
    bot = InstagramUnfollower()
    bot.run()
