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
from datetime import datetime, timedelta, timedelta
from stealth_config import *


class NYCDMVPleadPayScraper:
    def __init__(self):
        """Initialize the scraper with Chrome options and stealth strategies"""
        self.setup_driver()
        self.scraped_data = []
        self.client_id = "597872595"
        # Load ticket numbers from t_num2.txt
        self.ticket_numbers = self.load_ticket_numbers_from_file()
        self.max_retries = 3
        self.retry_delay_min = 2
        self.retry_delay_max = 5
        # Generate unique session ID for tracking
        self.session_id = f"session_{int(time.time())}"
        # Initialize persistent history
        self.init_persistent_history()

    def setup_driver(self):
        """Set up Chrome driver with maximum stealth options (copied from dmb_nv.py)"""
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

    def mouse_click_element(self, element):
        """Perform a human-like mouse click on an element"""
        try:
            # Move to element first
            self.actions.move_to_element(element).perform()
            self.random_delay(0.2, 0.5)

            # Click the element
            element.click()
            self.random_delay(0.3, 0.7)

            print("✓ Mouse click performed successfully")

        except Exception as e:
            print(f"Warning: Could not perform mouse click: {e}")
            # Fallback to regular click
            element.click()

    def extract_ticket_info_with_regex(self):
        """Extract ticket information using regex pattern"""
        print("Extracting ticket information using regex...")

        try:
            # Get page source
            page_source = self.driver.page_source

            # Regex pattern to match ticket information in <ul> tags
            pattern = r'<ul class="list-unstyled">(.*?)</ul>'

            ul_matches = re.findall(pattern, page_source, re.IGNORECASE | re.DOTALL)

            tickets = []
            for ul_content in ul_matches:
                # Extract individual fields from each ul
                ticket_data = {}

                # Traffic Ticket Number
                ticket_num_match = re.search(r'<strong>Traffic Ticket Number:</strong>\s*([^\s&]+)', ul_content)
                if ticket_num_match:
                    ticket_data['ticket_number'] = ticket_num_match.group(1).strip()

                # Violation Description
                violation_desc_match = re.search(r'<strong>Violation Description:</strong>\s*([^<]+)', ul_content)
                if violation_desc_match:
                    ticket_data['violation_description'] = violation_desc_match.group(1).strip()

                # Violation Date
                violation_date_match = re.search(r'<strong>Violation Date:</strong>\s*([^<]+)', ul_content)
                if violation_date_match:
                    ticket_data['violation_date'] = violation_date_match.group(1).strip()

                # Scheduled Hearing Date/Time
                hearing_date_match = re.search(r'<strong>Scheduled Hearing Date/Time:</strong>.*?<span>([^<]+)</span>', ul_content, re.DOTALL)
                if hearing_date_match:
                    ticket_data['hearing_date_time'] = hearing_date_match.group(1).strip()

                # TVB Hearing Location
                location_match = re.search(r'<strong>TVB Hearing Location:</strong>.*?>\s*([^<]+)\s*<span', ul_content, re.DOTALL)
                if location_match:
                    ticket_data['hearing_location'] = location_match.group(1).strip()

                # Driver Violation Points
                points_match = re.search(r'<strong>Driver Violation Points:</strong>\s*([^<]+)', ul_content)
                if points_match:
                    ticket_data['violation_points'] = points_match.group(1).strip()

                # Add extraction timestamp
                ticket_data['extracted_at'] = datetime.now().isoformat()                # Only add if we found at least a ticket number
                if ticket_data.get('ticket_number'):
                    tickets.append(ticket_data)
                    print(f"Found ticket: {ticket_data.get('ticket_number', 'Unknown')} - {ticket_data.get('violation_description', 'Unknown')}")

            if tickets:
                print(f"✓ Successfully extracted {len(tickets)} tickets")
                self.scraped_data.extend(tickets)
                return True
            else:
                print("No tickets found with regex pattern")
                return False

        except Exception as e:
            print(f"Error extracting ticket info with regex: {e}")
            return False

    def close_extra_tabs(self):
        """Close any extra tabs, keeping only the main tab"""
        try:
            # Keep only the first tab open
            while len(self.driver.window_handles) > 1:
                self.driver.switch_to.window(self.driver.window_handles[-1])
                self.driver.close()
                time.sleep(0.5)

            # Switch to the main (first) tab
            self.driver.switch_to.window(self.driver.window_handles[0])
            print("✓ Extra tabs closed, switched to main tab")
        except Exception as e:
            print(f"Warning: Could not close extra tabs: {e}")

    def enter_text_with_retry(self, xpath, text, description="field"):
        """Enter text with retry logic"""
        for retry_count in range(self.max_retries):
            try:
                print(f"⌨️ Entering {description}: {text}")
                field = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                self.actions.move_to_element(field).click().perform()
                self.random_delay(0.5, 1.0)
                self.human_like_typing(field, text)

                # Check if connection is blocked after entering text
                if self.check_connection_blocked():
                    print(f"🚫 Connection blocked after entering {description} (attempt {retry_count + 1})")
                    return False  # Let the ticket-level retry handle this

                print(f"✅ Successfully entered {description}")
                return True

            except Exception as e:
                print(f"❌ Error entering {description} (attempt {retry_count + 1}): {e}")
                if retry_count < self.max_retries - 1:
                    self.random_delay(2, 4)
                    continue
                else:
                    return False

        return False

    def process_single_ticket(self, ticket_number):
        """Process a single ticket through the workflow with ticket-level retry logic"""
        print(f"🎯 Processing ticket: {ticket_number}")

        # Ticket-level retry loop - start fresh each time
        for ticket_retry in range(self.max_retries):
            try:
                print(f"🔄 Ticket attempt {ticket_retry + 1}/{self.max_retries} for {ticket_number}")

                # Close any extra tabs and ensure we're on a fresh start
                self.close_extra_tabs()

                # If this is a retry, wander off first
                if ticket_retry > 0:
                    print("🚶 Connection issue detected - wandering off before retry...")
                    self.wander_off_strategy()
                    self.random_delay(3, 6)  # Extra delay after wandering

                # Start the ticket processing workflow
                if self.process_ticket_workflow(ticket_number):
                    print(f"✅ Successfully processed ticket: {ticket_number}")
                    return True
                else:
                    print(f"❌ Failed to process ticket {ticket_number} (attempt {ticket_retry + 1})")
                    if ticket_retry < self.max_retries - 1:
                        print(f"🔄 Will retry ticket {ticket_number} after delay...")
                        self.random_delay(5, 10)  # Delay between ticket retries
                    continue

            except Exception as e:
                print(f"❌ Error processing ticket {ticket_number} (attempt {ticket_retry + 1}): {e}")
                if ticket_retry < self.max_retries - 1:
                    print(f"🔄 Will retry ticket {ticket_number} after delay...")
                    self.random_delay(5, 10)  # Delay between ticket retries
                continue

        print(f"❌ Failed to process ticket {ticket_number} after {self.max_retries} attempts")
        return False

    def process_ticket_workflow(self, ticket_number):
        """Execute the complete workflow for a single ticket"""
        try:
            # Step 1: Navigate to initial URL
            if not self.navigate_with_retry("https://transact2.dmv.ny.gov/pleadnpay/", "initial DMV page"):
                print(f"❌ Failed to navigate to initial page for ticket {ticket_number}")
                return False

            # Step 2: Simulate human behavior
            self.simulate_human_behavior()
            self.random_delay(2, 4)

            # Step 3: Click on first radio button
            if not self.click_with_retry('//*[@id="DMVForm"]/div[1]/div/fieldset/div/div[1]/label', "first radio button"):
                print(f"❌ Failed to click first radio button for ticket {ticket_number}")
                return False

            # Step 4: Click submit button
            if not self.click_with_retry('//*[@id="btn-dmv-submit-div"]/input', "first submit button"):
                print(f"❌ Failed to click first submit button for ticket {ticket_number}")
                return False

            # Step 5: Wait for redirect and page load
            print("📍 Step 5: Waiting for redirect and page load...")
            if not self.wait_for_network_idle_with_retry():
                print(f"❌ Page load failed after first redirect for ticket {ticket_number}")
                return False

            self.simulate_human_behavior()
            self.random_delay(2, 4)

            # Step 6: Mouse click on second radio button
            if not self.click_with_retry('//*[@id="DMVForm"]/div[1]/div/fieldset/div/div[1]/label', "second radio button"):
                print(f"❌ Failed to click second radio button for ticket {ticket_number}")
                return False

            # Step 7: Enter Client ID
            print("📍 Step 7: Entering Client ID")
            if not self.enter_text_with_retry('//*[@id="sClientID"]', self.client_id, "Client ID"):
                print(f"❌ Failed to enter Client ID for ticket {ticket_number}")
                return False

            # Step 8: Mouse click on third radio button
            if not self.click_with_retry('//*[@id="DMVForm"]/div[6]/div/fieldset[1]/div/div[1]/label', "third radio button"):
                print(f"❌ Failed to click third radio button for ticket {ticket_number}")
                return False

            # Step 9: Enter Ticket ID
            print("📍 Step 9: Entering Ticket ID")
            if not self.enter_text_with_retry('//*[@id="ssearchTxt"]', ticket_number, "Ticket ID"):
                print(f"❌ Failed to enter Ticket ID for ticket {ticket_number}")
                return False

            # Step 10: Generate and enter email addresses
            print("📍 Step 10: Entering email addresses")
            random_email = self.generate_random_gmail()
            print(f"Using email: {random_email}")

            # First email field
            if not self.enter_text_with_retry('//*[@id="sEmailAddress"]', random_email, "first email"):
                print(f"❌ Failed to enter first email for ticket {ticket_number}")
                return False

            # Second email field
            if not self.enter_text_with_retry('//*[@id="sEmailAddress2"]', random_email, "second email"):
                print(f"❌ Failed to enter second email for ticket {ticket_number}")
                return False

            # Step 11: Human behavior before submit
            self.simulate_human_behavior()
            self.random_delay(1, 2)

            # Step 12: Click submit button
            if not self.click_with_retry('//*[@id="submitBtn"]', "main submit button"):
                print(f"❌ Failed to click main submit button for ticket {ticket_number}")
                return False

            # Step 13: Wait for redirection and page load
            print("📍 Step 13: Waiting for redirection and page load...")
            if not self.wait_for_network_idle_with_retry():
                print(f"❌ Page load failed after main submit for ticket {ticket_number}")
                return False

            self.simulate_human_behavior()
            self.random_delay(2, 4)

            # Step 14: Click Continue button
            if not self.click_with_retry('//*[@id="Continue"]', "Continue button"):
                print(f"❌ Failed to click Continue button for ticket {ticket_number}")
                return False

            # Step 15: Wait for final page
            print("📍 Step 15: Waiting for final page...")
            if not self.wait_for_network_idle_with_retry():
                print(f"❌ Final page load failed for ticket {ticket_number}")
                return False

            self.simulate_human_behavior()
            self.random_delay(2, 4)

            # Step 16: Extract ticket information
            print("📍 Step 16: Extracting ticket information...")
            extraction_success = self.extract_ticket_info_with_regex()

            if extraction_success:
                return True
            else:
                print(f"⚠️ Could not extract data for ticket: {ticket_number}")
                return False

        except Exception as e:
            print(f"❌ Error in ticket workflow for {ticket_number}: {e}")
            return False

    def save_results(self, filename='plead_pay_tickets.json'):
        """Save scraped data to JSON file"""
        try:
            # Create results directory if it doesn't exist
            os.makedirs("results", exist_ok=True)

            filepath = os.path.join("results", filename)

            with open(filepath, 'w', encoding='utf-8') as file:
                json.dump(self.scraped_data, file, indent=2, ensure_ascii=False)

            print(f"✓ Results saved to {filepath}")
            print(f"Total tickets processed: {len(self.scraped_data)}")

        except Exception as e:
            print(f"Error saving results: {e}")

    def run_scraping_workflow(self):
        """Execute the complete scraping workflow for all tickets"""
        try:
            print("🚀 Starting NYC DMV Plead & Pay scraping workflow...")

            # Step 1: Create browser history first
            self.create_browser_history()

            # Step 2: Process each ticket
            successful_tickets = 0
            failed_tickets = 0

            for i, ticket_number in enumerate(self.ticket_numbers):
                print(f"\n{'='*60}")
                print(f"Processing ticket {i+1}/{len(self.ticket_numbers)}: {ticket_number}")
                print(f"{'='*60}")

                try:
                    success = self.process_single_ticket(ticket_number)
                    if success:
                        successful_tickets += 1
                    else:
                        failed_tickets += 1

                    # Add delay between tickets if processing multiple
                    if i < len(self.ticket_numbers) - 1:
                        print(f"⏰ Waiting before processing next ticket...")
                        self.random_delay(5, 10)

                except Exception as e:
                    print(f"❌ Fatal error processing ticket {ticket_number}: {e}")
                    failed_tickets += 1
                    continue

            # Step 3: Save results
            self.save_results()

            print(f"\n🎉 Scraping workflow completed!")
            print(f"✅ Successful tickets: {successful_tickets}")
            print(f"❌ Failed tickets: {failed_tickets}")
            print(f"📊 Total data points collected: {len(self.scraped_data)}")

        except Exception as e:
            print(f"❌ Fatal error in scraping workflow: {e}")
            # Save whatever data we have
            if self.scraped_data:
                self.save_results()
            raise

    def add_ticket_numbers(self, ticket_numbers):
        """Add additional ticket numbers to process"""
        if isinstance(ticket_numbers, str):
            ticket_numbers = [ticket_numbers]

        self.ticket_numbers.extend(ticket_numbers)
        print(f"✓ Added {len(ticket_numbers)} ticket numbers. Total: {len(self.ticket_numbers)}")

    def cleanup(self):
        """Clean up resources"""
        try:
            if hasattr(self, 'driver'):
                self.driver.quit()
            print("✓ Browser closed successfully")
        except Exception as e:
            print(f"Warning: Error closing browser: {e}")

    def load_ticket_numbers_from_file(self):
        """Load ticket numbers from t_num2.txt file"""
        try:
            ticket_numbers = []
            with open('t_num2.txt', 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    if line:  # Skip empty lines
                        ticket_numbers.append(line)

            print(f"✓ Loaded {len(ticket_numbers)} ticket numbers from t_num2.txt")
            return ticket_numbers

        except FileNotFoundError:
            print("⚠️ t_num2.txt file not found. Using default ticket number.")
            return ["B255005941"]
        except Exception as e:
            print(f"❌ Error loading ticket numbers from file: {e}")
            return ["B255005941"]

    def init_persistent_history(self):
        """Initialize persistent browsing history for better website reputation"""
        try:
            # Ensure chrome_profile directory exists
            os.makedirs("chrome_profile", exist_ok=True)

            # Load existing history and add some initial entries if needed
            history_file = os.path.join("chrome_profile", "browsing_history.json")

            # If no history exists, create some initial legitimate browsing history
            if not os.path.exists(history_file):
                print("🏗️ Creating initial browsing history...")
                initial_history = []

                # Add some realistic browsing history from past few days
                base_sites = [
                    "https://www.google.com",
                    "https://www.wikipedia.org",
                    "https://www.news.google.com",
                    "https://www.weather.com",
                    "https://www.cnn.com",
                    "https://www.reddit.com",
                    "https://www.bbc.com",
                    "https://www.nytimes.com",
                    "https://www.amazon.com",
                    "https://www.youtube.com"
                ]

                # Create entries for past few days
                for days_ago in range(7, 0, -1):
                    sites_for_day = random.sample(base_sites, random.randint(2, 4))
                    for site in sites_for_day:
                        timestamp = datetime.now() - timedelta(days=days_ago)
                        timestamp += timedelta(hours=random.randint(9, 21), minutes=random.randint(0, 59))

                        history_entry = {
                            'url': site,
                            'timestamp': timestamp.isoformat(),
                            'session_id': f"historical_{days_ago}days_ago"
                        }
                        initial_history.append(history_entry)

                # Save initial history
                with open(history_file, 'w', encoding='utf-8') as f:
                    json.dump(initial_history, f, indent=2, ensure_ascii=False)

                print(f"✓ Created initial browsing history with {len(initial_history)} entries")
            else:
                print("✓ Persistent browsing history already exists")

        except Exception as e:
            print(f"Warning: Could not initialize persistent history: {e}")

    def check_connection_blocked(self):
        """Check if connection is blocked by looking for common blocking indicators"""
        try:
            page_source = self.driver.page_source.lower()
            current_url = self.driver.current_url.lower()

            # Common blocking indicators
            blocking_indicators = [
                'blocked',
                'access denied',
                'connection refused',
                'rate limit',
                'too many requests',
                'captcha',
                'suspicious activity',
                'temporarily unavailable',
                'service unavailable',
                'error 403',
                'error 429',
                'error 503',
                'cloudflare',
                'security check',
                'please wait',
                'verification required'
            ]

            # Check page source for blocking indicators
            for indicator in blocking_indicators:
                if indicator in page_source:
                    print(f"🚫 Connection blocked detected: {indicator}")
                    return True

            # Check if URL contains error indicators
            error_url_indicators = ['error', 'block', 'denied', 'captcha']
            for indicator in error_url_indicators:
                if indicator in current_url:
                    print(f"🚫 Blocking URL detected: {indicator}")
                    return True            # Check for specific DMV error pages
            if 'error' in current_url or 'block' in current_url:
                print("🚫 DMV error page detected")
                return True

            return False

        except Exception as e:
            print(f"Warning: Could not check connection status: {e}")
            return False

    def handle_connection_retry(self, retry_count=0):
        """Handle connection retry logic with connection reset detection"""
        if retry_count >= self.max_retries:
            print(f"❌ Maximum retries ({self.max_retries}) reached. Giving up.")
            return False

        print(f"🔄 Connection retry attempt {retry_count + 1}/{self.max_retries}")

        # Check if connection was reset
        connection_reset = self.is_connection_reset()
        if connection_reset:
            print("🔌 Connection reset detected - performing full reset")

            # Close all extra tabs first
            self.close_extra_tabs()

            # Perform extended wander off strategy
            self.wander_off_strategy()

            # Extended delay after connection reset
            extended_delay = random.uniform(10, 20)
            print(f"⏰ Extended delay after connection reset: {extended_delay:.1f} seconds...")
            time.sleep(extended_delay)

            return False  # Signal to the caller that they need to restart from beginning

        # Regular retry logic for other errors
        base_delay = random.uniform(self.retry_delay_min, self.retry_delay_max)
        progressive_delay = base_delay * (retry_count + 1)

        print(f"⏰ Waiting {progressive_delay:.1f} seconds before retry...")
        time.sleep(progressive_delay)

        # Light wander off for regular retries
        if retry_count > 0:
            print("🚶 Light wandering for regular retry...")
            self.wander_off_strategy()

        return True

    def is_connection_reset(self):
        """Check if the connection was reset by looking for specific indicators"""
        try:
            # Check if we can access the page at all
            try:
                current_url = self.driver.current_url
                page_source = self.driver.page_source.lower()
            except Exception as e:
                error_msg = str(e).lower()
                # Check for connection reset specific errors
                connection_reset_indicators = [
                    'connection reset',
                    'connection refused',
                    'connection aborted',
                    'connection closed',
                    'network error',
                    'timeout',
                    'disconnected',
                    'chrome not reachable',
                    'session not created',
                    'no such window',
                    'no such session'
                ]

                for indicator in connection_reset_indicators:
                    if indicator in error_msg:
                        print(f"🔌 Connection reset indicator found: {indicator}")
                        return True

                return False

            # Check page content for connection issues
            if not page_source or len(page_source) < 100:
                print("🔌 Page appears to be empty or too small - possible connection issue")
                return True

            # Check for specific connection reset page content
            reset_page_indicators = [
                'connection reset',
                'err_connection_reset',
                'err_connection_refused',
                'err_network_changed',
                'err_internet_disconnected',
                'this site can\'t be reached',
                'unable to connect',
                'connection timed out'
            ]

            for indicator in reset_page_indicators:
                if indicator in page_source:
                    print(f"� Connection reset page indicator found: {indicator}")
                    return True

            return False

        except Exception as e:
            print(f"🔌 Error checking connection reset status: {e}")
            return True  # Assume connection reset if we can't even check

    def wander_off_strategy(self, return_url=None):
        """Wander off to random sites to avoid detection and optionally return to original URL"""
        try:
            print("🚶 Wandering off to look more human...")

            # Save current URL if not provided
            if return_url is None:
                try:
                    return_url = self.driver.current_url
                except:
                    return_url = None

            # Random sites to visit
            wander_sites = [
                "https://www.google.com/search?q=weather+today",
                "https://www.google.com/search?q=news+today",
                "https://www.wikipedia.org/wiki/Main_Page",
                "https://www.reddit.com/r/news",
                "https://www.cnn.com",
                "https://www.bbc.com/news",
                "https://www.nytimes.com",
                "https://www.weather.com",
                "https://www.espn.com"
            ]

            # Visit 1-2 random sites
            sites_to_visit = random.sample(wander_sites, random.randint(1, 2))

            for site in sites_to_visit:
                try:
                    print(f"  🌐 Visiting: {site}")
                    self.driver.get(site)

                    # Wait for page load
                    time.sleep(random.uniform(2, 4))

                    # Simulate human behavior (but catch errors)
                    try:
                        self.simulate_human_behavior()
                    except Exception as e:
                        print(f"  ⚠️ Minor issue with human behavior simulation: {e}")

                    # Random interaction
                    if random.random() < 0.5:
                        try:
                            scroll_amount = random.randint(100, 500)
                            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                            time.sleep(random.uniform(1, 2))
                        except Exception as e:
                            print(f"  ⚠️ Minor issue with scrolling: {e}")

                    # Stay on page for random duration
                    stay_duration = random.uniform(3, 8)
                    time.sleep(stay_duration)

                    # Add to persistent history
                    self.add_to_persistent_history(site)

                except Exception as e:
                    print(f"  ⚠️ Issue wandering to {site}: {e}")
                    continue

            # Return to original URL if specified
            if return_url and return_url != "data:," and "about:blank" not in return_url:
                try:
                    print(f"  🔄 Returning to: {return_url}")
                    self.driver.get(return_url)
                    time.sleep(random.uniform(2, 4))
                except Exception as e:
                    print(f"  ⚠️ Could not return to original URL: {e}")

            print("✓ Wandering complete")

        except Exception as e:
            print(f"Warning: Could not execute wander off strategy: {e}")

    def add_to_persistent_history(self, url):
        """Add URL to persistent browsing history for future reputation"""
        try:
            history_file = os.path.join("chrome_profile", "browsing_history.json")

            # Load existing history
            browsing_history = []
            if os.path.exists(history_file):
                try:
                    with open(history_file, 'r', encoding='utf-8') as f:
                        browsing_history = json.load(f)
                except:
                    browsing_history = []

            # Add new entry
            history_entry = {
                'url': url,
                'timestamp': datetime.now().isoformat(),
                'session_id': getattr(self, 'session_id', 'unknown')
            }

            browsing_history.append(history_entry)

            # Keep only last 1000 entries to prevent file from growing too large
            if len(browsing_history) > 1000:
                browsing_history = browsing_history[-1000:]

            # Save back to file
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(browsing_history, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"Warning: Could not save to persistent history: {e}")

    def navigate_with_retry(self, url, description="page"):
        """Navigate to URL with retry logic"""
        for retry_count in range(self.max_retries):
            try:
                print(f"🌐 Navigating to {description}: {url}")
                self.driver.get(url)
                self.wait_for_network_idle()

                # Check if connection is blocked
                if self.check_connection_blocked():
                    print(f"🚫 Connection blocked on {description} (attempt {retry_count + 1})")
                    if retry_count < self.max_retries - 1:
                        if not self.handle_connection_retry(retry_count):
                            return False
                        # After wandering off, try to navigate to the URL again
                        continue
                    else:
                        return False

                # Success
                print(f"✅ Successfully navigated to {description}")
                return True

            except Exception as e:
                print(f"❌ Error navigating to {description} (attempt {retry_count + 1}): {e}")
                if retry_count < self.max_retries - 1:
                    if not self.handle_connection_retry(retry_count):
                        return False
                    # After wandering off, the loop will continue and retry
                else:
                    return False

        return False

    def click_with_retry(self, xpath, description="element"):
        """Click element with retry logic"""
        for retry_count in range(self.max_retries):
            try:
                print(f"🖱️ Clicking {description}")
                element = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                self.mouse_click_element(element)

                # Wait a bit and check if action was successful
                time.sleep(random.uniform(1, 2))

                # Check if connection is blocked after click
                if self.check_connection_blocked():
                    print(f"🚫 Connection blocked after clicking {description} (attempt {retry_count + 1})")
                    if retry_count < self.max_retries - 1:
                        if not self.handle_connection_retry(retry_count):
                            return False
                        # After wandering off, we need to re-navigate to the page before retrying the click
                        print("🔄 Re-navigating to page after wandering off...")
                        # The caller should handle re-navigation or we return False to let them handle it
                        return False  # Let the caller handle re-navigation
                    else:
                        return False

                # Success
                print(f"✅ Successfully clicked {description}")
                return True

            except Exception as e:
                print(f"❌ Error clicking {description} (attempt {retry_count + 1}): {e}")
                if retry_count < self.max_retries - 1:
                    if not self.handle_connection_retry(retry_count):
                        return False
                    # After wandering off, we need to re-navigate to the page
                    return False  # Let the caller handle re-navigation
                else:
                    return False

        return False

    def wait_for_network_idle_with_retry(self, timeout=30):
        """Wait for network idle with connection checking"""
        try:
            self.wait_for_network_idle(timeout)

            # Check if connection is blocked after waiting
            if self.check_connection_blocked():
                return False

            return True

        except Exception as e:
            print(f"Warning: Network idle check failed: {e}")
            return False

    # ...existing code...
def main():
    """Main execution function"""
    scraper = None
    try:
        print("🤖 Initializing NYC DMV Plead & Pay Scraper...")
        scraper = NYCDMVPleadPayScraper()

        print(f"📋 Processing {len(scraper.ticket_numbers)} ticket(s) from t_num2.txt")
        for i, ticket in enumerate(scraper.ticket_numbers):
            print(f"  {i+1}. {ticket}")

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
