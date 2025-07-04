import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import json
import time
import re
import random
import os
from datetime import datetime
from stealth_config import *


class NYCDMVWebSummonsScraper:
    def __init__(self):
        """Initialize the scraper with Chrome options and stealth strategies"""
        self.setup_driver()
        self.scraped_data = []
        self.client_id = "597872595"
        self.ticket_id = "B255005941"

    def setup_driver(self):
        """Set up Chrome driver with maximum stealth options (copied from main.py)"""
        options = uc.ChromeOptions()

        # Create a persistent user data directory
        user_data_dir = os.path.join(os.getcwd(), "chrome_profile")
        if not os.path.exists(user_data_dir):
            os.makedirs(user_data_dir)

        # Enhanced stealth options
        options.add_argument(f"--user-data-dir={user_data_dir}")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-notifications")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--start-maximized")
        # REMOVED INCOGNITO MODE for better stealth
        # options.add_argument("--incognito")

        # Random user agent
        selected_ua = random.choice(USER_AGENTS)
        options.add_argument(f'--user-agent={selected_ua}')

        # Additional stealth options
        options.add_argument("--disable-automation")
        options.add_argument("--disable-browser-side-navigation")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_argument("--disable-ipc-flooding-protection")

        # Set window size to common resolution
        options.add_argument("--window-size=1920,1080")

        # Try to add experimental options (these might not work with all Chrome versions)
        try:
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
        except Exception as e:
            print(f"Warning: Could not set experimental options: {e}")

        try:
            self.driver = uc.Chrome(options=options)
            self.wait = WebDriverWait(self.driver, 30)
            self.actions = ActionChains(self.driver)

            # Execute stealth scripts
            self.execute_stealth_scripts()

            print(f"✓ Browser initialized successfully with user agent: {selected_ua}")

        except Exception as e:
            print(f"Error initializing browser with full options: {e}")
            print("Trying with minimal options...")

            # Fallback to minimal options
            options = uc.ChromeOptions()
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--start-maximized")
            options.add_argument(f'--user-agent={selected_ua}')

            self.driver = uc.Chrome(options=options)
            self.wait = WebDriverWait(self.driver, 30)
            self.actions = ActionChains(self.driver)

            print(f"✓ Browser initialized with minimal options")

    def execute_stealth_scripts(self):
        """Execute JavaScript to make the browser more human-like"""
        for script in STEALTH_SCRIPTS:
            try:
                self.driver.execute_script(script)
            except Exception as e:
                print(f"Warning: Could not execute stealth script: {e}")

        print("✓ Stealth scripts executed successfully")

    def simulate_human_behavior(self):
        """Simulate human-like behavior with mouse movements and scrolling"""
        if not MOUSE_MOVEMENTS['enabled']:
            return

        try:
            # Random mouse movements
            num_movements = random.randint(MOUSE_MOVEMENTS['min_movements'], MOUSE_MOVEMENTS['max_movements'])
            for _ in range(num_movements):
                x_offset = random.randint(-MOUSE_MOVEMENTS['max_offset_x'], MOUSE_MOVEMENTS['max_offset_x'])
                y_offset = random.randint(-MOUSE_MOVEMENTS['max_offset_y'], MOUSE_MOVEMENTS['max_offset_y'])
                self.actions.move_by_offset(x_offset, y_offset).perform()
                time.sleep(random.uniform(MOUSE_MOVEMENTS['movement_delay_min'], MOUSE_MOVEMENTS['movement_delay_max']))

            # Random scrolling
            if SCROLLING['enabled']:
                scroll_amount = random.randint(SCROLLING['min_scroll'], SCROLLING['max_scroll'])
                self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                time.sleep(random.uniform(SCROLLING['scroll_delay_min'], SCROLLING['scroll_delay_max']))

                # Sometimes scroll back up
                if random.random() < SCROLLING['scroll_back_probability']:
                    self.driver.execute_script(f"window.scrollBy(0, -{scroll_amount // 2});")
                    time.sleep(random.uniform(SCROLLING['scroll_delay_min'], SCROLLING['scroll_delay_max']))

        except Exception as e:
            print(f"Warning: Could not simulate human behavior: {e}")

    def human_like_typing(self, element, text):
        """Type text in a human-like manner with random delays"""
        if not TYPING_BEHAVIOR['enabled']:
            element.send_keys(text)
            return

        element.clear()
        time.sleep(random.uniform(TYPING_BEHAVIOR['pre_type_delay_min'], TYPING_BEHAVIOR['pre_type_delay_max']))

        for char in text:
            element.send_keys(char)
            # Random typing speed
            time.sleep(random.uniform(TYPING_BEHAVIOR['char_delay_min'], TYPING_BEHAVIOR['char_delay_max']))

        # Sometimes make a "mistake" and correct it
        if random.random() < TYPING_BEHAVIOR['mistake_probability'] and len(text) > 3:
            time.sleep(random.uniform(0.2, 0.5))
            element.send_keys(Keys.BACKSPACE)
            time.sleep(random.uniform(0.1, 0.3))
            element.send_keys(text[-1])

    def create_browser_history(self):
        """Create some browser history to look more human with enhanced randomness"""
        if not BROWSER_HISTORY['enabled']:
            return

        try:
            print("Creating browser history...")

            # Enhanced sites list with more variety
            all_history_sites = [
                "https://www.google.com",
                "https://www.wikipedia.org",
                "https://www.news.google.com",
                "https://www.weather.com",
                "https://www.cnn.com",
                "https://www.reddit.com",
                "https://www.bbc.com",
                "https://www.nytimes.com",
                "https://www.espn.com",
                "https://www.forbes.com",
                "https://www.bloomberg.com",
                "https://stackoverflow.com",
                "https://www.github.com"
            ]

            # Random number of sites to visit (1-3 for initial history)
            visit_count = random.randint(1, 3)
            selected_sites = random.sample(all_history_sites, min(visit_count, len(all_history_sites)))

            for site in selected_sites:
                try:
                    print(f"  📖 Adding to history: {site}")
                    self.driver.execute_script(f"window.open('{site}', '_blank');")
                    time.sleep(random.uniform(1, 2))

                    # Switch to the new tab and interact briefly
                    self.driver.switch_to.window(self.driver.window_handles[-1])

                    # Brief interaction
                    visit_duration = random.uniform(1, 4)  # Shorter for initial history

                    # Sometimes scroll or click
                    if random.random() < 0.5:
                        scroll_amount = random.randint(100, 300)
                        self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                        time.sleep(0.5)

                    if random.random() < 0.3:  # 30% chance to click
                        try:
                            body = self.driver.find_element(By.TAG_NAME, "body")
                            self.actions.move_to_element(body).click().perform()
                        except:
                            pass

                    time.sleep(visit_duration)
                    self.driver.close()

                    # Switch back to main tab
                    self.driver.switch_to.window(self.driver.window_handles[0])
                    time.sleep(random.uniform(0.3, 0.8))

                except Exception as e:
                    print(f"  ⚠️ Issue with history site {site}: {type(e).__name__}")
                    try:
                        self.driver.close()
                        self.driver.switch_to.window(self.driver.window_handles[0])
                    except:
                        pass

            print("✓ Browser history created successfully")

        except Exception as e:
            print(f"Warning: Could not create browser history: {e}")

    def random_delay(self, min_seconds=1.0, max_seconds=3.0):
        """Add random delays to mimic human behavior"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)

    def wait_for_network_idle(self, timeout=30):
        """Wait for network to be idle"""
        print("Waiting for network to be idle...")
        
        # Wait for page to load and become interactive
        self.wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
        
        # Additional wait for network activity to settle
        time.sleep(3)
        
        # Check if there are any active requests
        try:
            # Wait for any AJAX requests to complete
            self.wait.until(lambda driver: driver.execute_script("return jQuery.active == 0") if driver.execute_script("return typeof jQuery != 'undefined'") else True)
        except:
            pass  # jQuery might not be available
        
        print("✓ Network appears to be idle")

    def generate_random_gmail(self):
        """Generate a random gmail address"""
        prefixes = ["john", "jane", "mike", "sarah", "david", "emma", "alex", "lisa", "chris", "anna"]
        suffixes = ["123", "456", "789", "2024", "2025", "test", "demo", "temp"]
        
        prefix = random.choice(prefixes)
        suffix = random.choice(suffixes)
        
        return f"{prefix}{suffix}@gmail.com"

    def scrape_tickets_with_regex(self):
        """Scrape all tickets using regex pattern"""
        print("Scraping tickets using regex...")
        
        try:
            # Get page source
            page_source = self.driver.page_source
            
            # Regex pattern to match ticket information
            pattern = r'<label for="chk-([^"]+)">\s*<span[^>]*><strong>Ticket Number:</strong>\s*([^<]+)</span><br>\s*<span[^>]*><strong>Section of Law:</strong>\s*([^<]+)</span><br>\s*<span[^>]*><strong>Violation:</strong>\s*([^<]+)</span><br>\s*<span[^>]*><strong>Violation Date:</strong>\s*([^<]+)</span>'
            
            matches = re.findall(pattern, page_source, re.IGNORECASE | re.DOTALL)
            
            tickets = []
            for match in matches:
                ticket_data = {
                    'ticket_checkbox_id': match[0],
                    'ticket_number': match[1].strip(),
                    'section_of_law': match[2].strip(),
                    'violation': match[3].strip(),
                    'violation_date': match[4].strip(),
                    'extracted_at': datetime.now().isoformat()
                }
                tickets.append(ticket_data)
                print(f"Found ticket: {ticket_data['ticket_number']} - {ticket_data['violation']}")
            
            if tickets:
                print(f"✓ Successfully scraped {len(tickets)} tickets")
                self.scraped_data.extend(tickets)
            else:
                print("No tickets found with regex pattern")
                
        except Exception as e:
            print(f"Error scraping tickets with regex: {e}")
            
    def save_results(self, filename='dmv_tickets.json'):
        """Save scraped data to JSON file"""
        try:
            # Create results directory if it doesn't exist
            os.makedirs("results", exist_ok=True)
            
            filepath = os.path.join("results", filename)
            
            with open(filepath, 'w', encoding='utf-8') as file:
                json.dump(self.scraped_data, file, indent=2, ensure_ascii=False)
            
            print(f"✓ Results saved to {filepath}")
            print(f"Total tickets scraped: {len(self.scraped_data)}")
            
        except Exception as e:
            print(f"Error saving results: {e}")

    def run_scraping_workflow(self):
        """Execute the complete scraping workflow"""
        try:
            print("🚀 Starting NYC DMV Web Summons scraping workflow...")
            
            # Step 1: Create browser history first
            self.create_browser_history()
            
            # Step 2: Navigate to initial URL
            print("📍 Step 1: Navigating to https://process.dmv.ny.gov/WebSummons/")
            self.driver.get("https://process.dmv.ny.gov/WebSummons/")
            
            # Step 3: Wait for network idle
            self.wait_for_network_idle()
            
            # Step 4: Simulate human behavior
            self.simulate_human_behavior()
            self.random_delay(2, 4)
            
            # Step 5: Click the submit button
            print("📍 Step 2: Clicking submit button")
            submit_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="submit"]')))
            
            # Human-like interaction
            self.actions.move_to_element(submit_button).perform()
            self.random_delay(0.5, 1.0)
            submit_button.click()
            
            # Step 6: Wait for redirect and page load
            print("📍 Step 3: Waiting for redirect and page load...")
            self.wait_for_network_idle()
            
            # Step 7: Log current URL
            current_url = self.driver.current_url
            print(f"📍 Current URL after redirect: {current_url}")
            
            # Step 8: Simulate human behavior
            self.simulate_human_behavior()
            self.random_delay(1, 3)
            
            # Step 9: Enter Client ID
            print("📍 Step 4: Entering Client ID")
            client_id_field = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="sClientID"]')))
            
            self.actions.move_to_element(client_id_field).click().perform()
            self.random_delay(0.5, 1.0)
            self.human_like_typing(client_id_field, self.client_id)
            
            # Step 10: Enter Ticket ID
            print("📍 Step 5: Entering Ticket ID")
            ticket_id_field = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="sTicketNum"]')))
            
            self.actions.move_to_element(ticket_id_field).click().perform()
            self.random_delay(0.5, 1.0)
            self.human_like_typing(ticket_id_field, self.ticket_id)
            
            # Step 11: Generate and enter random Gmail addresses
            print("📍 Step 6: Entering email addresses")
            random_email = self.generate_random_gmail()
            print(f"Using email: {random_email}")
            
            # First email field
            email_field1 = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="sEmailAddress"]')))
            self.actions.move_to_element(email_field1).click().perform()
            self.random_delay(0.5, 1.0)
            self.human_like_typing(email_field1, random_email)
            
            # Second email field
            email_field2 = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="sEmailAddress2"]')))
            self.actions.move_to_element(email_field2).click().perform()
            self.random_delay(0.5, 1.0)
            self.human_like_typing(email_field2, random_email)
            
            # Step 12: Human behavior before final submit
            self.simulate_human_behavior()
            self.random_delay(1, 2)
            
            # Step 13: Click final submit button
            print("📍 Step 7: Clicking submit order button")
            submit_order_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="submit order"]')))
            
            self.actions.move_to_element(submit_order_button).perform()
            self.random_delay(0.5, 1.0)
            submit_order_button.click()
            
            # Step 14: Wait for final redirect and page load
            print("📍 Step 8: Waiting for final redirect and page load...")
            self.wait_for_network_idle()
            
            # Step 15: Log final URL
            final_url = self.driver.current_url
            print(f"📍 Final URL after redirect: {final_url}")
            
            # Step 16: Simulate human behavior before scraping
            self.simulate_human_behavior()
            self.random_delay(2, 4)
            
            # Step 17: Scrape tickets
            print("📍 Step 9: Scraping tickets...")
            self.scrape_tickets_with_regex()
            
            # Step 18: Save results
            self.save_results()
            
            print("🎉 Scraping workflow completed successfully!")
            
        except Exception as e:
            print(f"❌ Error in scraping workflow: {e}")
            # Save whatever data we have
            if self.scraped_data:
                self.save_results()
            raise

    def cleanup(self):
        """Clean up resources"""
        try:
            if hasattr(self, 'driver'):
                self.driver.quit()
            print("✓ Browser closed successfully")
        except Exception as e:
            print(f"Warning: Error closing browser: {e}")


def main():
    """Main execution function"""
    scraper = None
    try:
        print("🤖 Initializing NYC DMV Web Summons Scraper...")
        scraper = NYCDMVWebSummonsScraper()
        
        print("🎯 Starting scraping process...")
        scraper.run_scraping_workflow()
        
    except KeyboardInterrupt:
        print("\n⚠️ Scraping interrupted by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
    finally:
        if scraper:
            scraper.cleanup()


if __name__ == "__main__":
    main()
