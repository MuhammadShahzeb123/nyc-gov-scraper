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

class NYCParkingTicketScraper:
    def __init__(self):
        """Initialize the scraper with Chrome options"""
        self.setup_driver()
        self.violation_numbers = self.load_violation_numbers()
        self.scraped_data = []

    def setup_driver(self):
        """Set up Chrome driver with maximum stealth options"""
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

    def load_violation_numbers(self):
        """Load violation numbers from v_num.txt file"""
        try:
            with open('v_num.txt', 'r') as file:
                numbers = [line.strip() for line in file if line.strip()]
            print(f"Loaded {len(numbers)} violation numbers")
            return numbers
        except FileNotFoundError:
            print("Error: v_num.txt file not found!")
            return []

    def navigate_to_site(self):
        """Navigate to the NYC parking ticket website with human-like behavior"""
        # First create some browser history
        self.create_browser_history()

        url = "https://a836-citypay.nyc.gov/citypay/Parking?stage=procurement"
        print(f"Navigating to: {url}")
          # Simulate human-like navigation
        self.driver.get(url)

        # Simulate human behavior while page loads
        self.random_delay(DELAYS['page_load_min'], DELAYS['page_load_max'])
        self.simulate_human_behavior()

        # Wait for page to load
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="violation-number"]')))
            print("Page loaded successfully")

            # More human-like behavior after page load
            self.simulate_human_behavior()
            self.random_delay(1, 2)

            return True
        except TimeoutException:
            print("Timeout waiting for page to load")
            return False

    def detect_captcha_error(self):
        """Detect if a captcha error is present on the page"""
        try:
            # Get the full page source
            page_source = self.driver.page_source.lower()

            # Various captcha error patterns to check for
            captcha_patterns = [
                "unable to verify recaptcha with google",
                "unable to verify recaptcha",
                "recaptcha verification failed",
                "captcha verification failed",
                "captcha error",
                "recaptcha error",
                "please verify you are human",
                "verify you are not a robot",
                "security verification required",
                "anti-bot verification",
                "please complete the captcha",
                "captcha challenge",
                "human verification required"
            ]

            # Check for any of these patterns
            for pattern in captcha_patterns:
                if pattern in page_source:
                    print(f"🤖 CAPTCHA DETECTED: Found pattern '{pattern}'")
                    return True

            # Also check for common reCAPTCHA elements
            captcha_elements = [
                "//div[@class*='recaptcha']",
                "//iframe[@title*='recaptcha']",
                "//div[@id*='captcha']",
                "//div[@class*='captcha']",
                "//*[contains(@class, 'g-recaptcha')]",
                "//*[contains(text(), 'I am not a robot')]"
            ]

            for xpath in captcha_elements:
                try:
                    elements = self.driver.find_elements(By.XPATH, xpath)
                    if elements and any(elem.is_displayed() for elem in elements):
                        print(f"🤖 CAPTCHA DETECTED: Found visible element with xpath '{xpath}'")
                        return True
                except:
                    continue

            return False

        except Exception as e:
            print(f"⚠️ Error checking for captcha: {type(e).__name__}")
            return False

    def handle_captcha_retry(self, violation_number):
        """Handle captcha detection by wandering and retrying once"""
        print(f"🤖 Captcha detected for violation {violation_number} - initiating evasion sequence...")

        # Take a random break to avoid captcha
        self.take_random_break()

        # Return to base URL
        self.return_to_base_url()

        # Wait a bit more
        self.random_delay(3, 8)

        # Try the search one more time
        print(f"🔄 Retrying search for violation {violation_number} after captcha evasion...")
        return self.search_violation_number_internal(violation_number, is_retry=True)

    def search_violation_number_internal(self, violation_number, is_retry=False):
        """Internal search method that can handle retries"""
        try:
            # Simulate human behavior before interacting
            self.simulate_human_behavior()
            self.random_delay(0.5, 1.5)

            # Find and interact with input field in a human-like way
            input_field = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="violation-number"]')))

            # Clear the field first
            input_field.clear()
            self.random_delay(0.2, 0.5)

            # Move mouse to input field and click
            self.actions.move_to_element(input_field).click().perform()
            self.random_delay(0.3, 0.8)

            # Human-like typing
            self.human_like_typing(input_field, violation_number)

            self.random_delay(0.5, 1.0)

            # Find and click search button with human-like behavior
            search_button = self.driver.find_element(By.XPATH, '//*[@id="by-violation-form"]/div[3]/button')

            # Move mouse to button and click
            self.actions.move_to_element(search_button).perform()
            self.random_delay(0.2, 0.5)
            search_button.click()

            print(f"Searching for violation number: {violation_number}" + (" (retry)" if is_retry else ""))

            # Wait for network to be idle and page to load results
            self.wait_for_results()

            # Check for captcha after search results load
            if self.detect_captcha_error():
                if is_retry:
                    print(f"🤖 Captcha detected again on retry for {violation_number} - skipping this violation")
                    return False
                else:
                    # Handle captcha with wandering and retry
                    return self.handle_captcha_retry(violation_number)

            # Try to interact with search filters stealthily after successful search
            self.try_click_search_filters_stealthily()

            return True

        except (TimeoutException, NoSuchElementException) as e:
            print(f"Error searching for {violation_number}: {str(e)}")
            return False

    def search_violation_number(self, violation_number):
        """Search for a specific violation number with human-like behavior and captcha handling"""
        return self.search_violation_number_internal(violation_number, is_retry=False)

    def wait_for_results(self):
        """Wait for search results to load completely"""
        try:
            # Wait for either results to appear or no results message
            self.wait.until(
                lambda driver:
                driver.find_elements(By.XPATH, '//tr[starts-with(@id, "ticket-")]') or
                driver.find_elements(By.XPATH, '//*[contains(text(), "No violations found")]') or
                driver.find_elements(By.XPATH, '//*[contains(text(), "no results")]')
            )

            # Additional wait to ensure all content is loaded
            time.sleep(2)
            print("Results loaded")

        except TimeoutException:
            print("Timeout waiting for search results")

    def extract_ticket_data(self, violation_number):
        """Extract ticket information from the search results"""
        tickets = []

        try:
            # Find all ticket rows
            ticket_rows = self.driver.find_elements(By.XPATH, '//tr[starts-with(@id, "ticket-")]')

            if not ticket_rows:
                print(f"No tickets found for violation number: {violation_number}")
                return tickets

            print(f"Found {len(ticket_rows)} ticket(s) for violation number: {violation_number}")

            for row in ticket_rows:
                try:
                    ticket_data = self.parse_ticket_row(row, violation_number)
                    if ticket_data:
                        tickets.append(ticket_data)
                except Exception as e:
                    print(f"Error parsing ticket row: {str(e)}")
                    continue

        except Exception as e:
            print(f"Error extracting ticket data: {str(e)}")

        return tickets

    def parse_ticket_row(self, row, search_violation_number):
        """Parse individual ticket row and extract relevant information"""
        try:
            ticket_data = {
                'search_violation_number': search_violation_number,
                'extracted_at': datetime.now().isoformat(),
                'ticket_id': '',
                'violation_number': '',
                'license_plate': '',
                'violation_type': '',
                'date': '',
                'liability_amount': '',
                'paid_amount': '',
                'amount_due': '',
                'payment_amount': '',
                'view_ticket_link': ''
            }

            # Extract ticket ID from row id attribute
            ticket_id = row.get_attribute('id')
            if ticket_id and ticket_id.startswith('ticket-'):
                ticket_data['ticket_id'] = ticket_id.replace('ticket-', '')

            # Extract cells
            cells = row.find_elements(By.TAG_NAME, 'td')

            if len(cells) >= 8:
                # Violation number and view ticket link (usually in 2nd cell, index 1)
                if len(cells) > 1:
                    violation_cell = cells[1]
                    # Extract violation number
                    span_elements = violation_cell.find_elements(By.TAG_NAME, 'span')
                    if span_elements:
                        ticket_data['violation_number'] = span_elements[0].text.strip()

                    # Extract view ticket link
                    link_elements = violation_cell.find_elements(By.TAG_NAME, 'a')
                    if link_elements:
                        ticket_data['view_ticket_link'] = link_elements[0].get_attribute('href')

                # License plate (usually in 3rd cell, index 2)
                if len(cells) > 2:
                    license_cell = cells[2]
                    span_elements = license_cell.find_elements(By.TAG_NAME, 'span')
                    if span_elements:
                        ticket_data['license_plate'] = span_elements[0].text.strip()

                # Violation type (usually in 4th cell, index 3)
                if len(cells) > 3:
                    ticket_data['violation_type'] = cells[3].text.strip()

                # Date (usually in 5th cell, index 4)
                if len(cells) > 4:
                    ticket_data['date'] = cells[4].text.strip()

                # Liability amount (usually in 6th cell, index 5)
                if len(cells) > 5:
                    data_elements = cells[5].find_elements(By.TAG_NAME, 'data')
                    if data_elements:
                        ticket_data['liability_amount'] = data_elements[0].text.strip()

                # Paid amount (usually in 7th cell, index 6)
                if len(cells) > 6:
                    data_elements = cells[6].find_elements(By.TAG_NAME, 'data')
                    if data_elements:
                        ticket_data['paid_amount'] = data_elements[0].text.strip()

                # Amount due (usually in 8th cell, index 7)
                if len(cells) > 7:
                    data_elements = cells[7].find_elements(By.TAG_NAME, 'data')
                    if data_elements:
                        ticket_data['amount_due'] = data_elements[0].text.strip()

                # Payment amount (usually in 9th cell, index 8)
                if len(cells) > 8:
                    input_elements = cells[8].find_elements(By.XPATH, './/input[@name="paymentAmount"]')
                    if input_elements:
                        ticket_data['payment_amount'] = input_elements[0].get_attribute('value')

            print(f"Extracted ticket data: {ticket_data['ticket_id']} - {ticket_data['violation_number']}")
            return ticket_data

        except Exception as e:
            print(f"Error parsing ticket row: {str(e)}")
            return None

    def save_data_to_json(self, filename='nyc_parking_tickets.json'):
        """Save scraped data to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                json.dump(self.scraped_data, file, indent=2, ensure_ascii=False)
            print(f"Data saved to {filename}")
            print(f"Total records saved: {len(self.scraped_data)}")
        except Exception as e:
            print(f"Error saving data to JSON: {str(e)}")

    def save_results_immediately(self, tickets, violation_number):
        """Save results immediately as they are scraped to prevent data loss"""
        if not tickets:
            return

        try:
            # Create individual file for this violation number
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            individual_filename = f"results/violation_{violation_number}_{timestamp}.json"

            # Create results directory if it doesn't exist
            os.makedirs("results", exist_ok=True)

            # Save individual result
            with open(individual_filename, 'w', encoding='utf-8') as file:
                json.dump(tickets, file, indent=2, ensure_ascii=False)

            # Also append to master file immediately
            master_filename = "results/all_tickets_live.json"

            # Load existing data if file exists
            existing_data = []
            if os.path.exists(master_filename):
                try:
                    with open(master_filename, 'r', encoding='utf-8') as file:
                        existing_data = json.load(file)
                except:
                    existing_data = []

            # Append new tickets
            existing_data.extend(tickets)

            # Save updated master file
            with open(master_filename, 'w', encoding='utf-8') as file:
                json.dump(existing_data, file, indent=2, ensure_ascii=False)

            print(f"✓ Results saved immediately: {len(tickets)} tickets for violation {violation_number}")
            print(f"  Individual file: {individual_filename}")
            print(f"  Master file updated: {master_filename}")

        except Exception as e:
            print(f"Warning: Could not save results immediately: {e}")

    def try_click_search_filters_stealthily(self):
        """Try to click search filters in a stealthy way - CRUCIAL for progression"""
        try:
            # Always attempt this since it's crucial for progression
            print("🔍 Attempting to interact with search filters (CRUCIAL STEP)...")

            # Simulate looking around the page first
            self.simulate_human_behavior()
            self.random_delay(0.5, 1.5)

            # Multiple XPath options to try (in order of preference)
            search_filter_xpaths = [
                '//*[@id="search-filters"]/p/a',  # Most specific path - the crucial one
                '//*[@id="search-filters"]//a',   # Any link within search-filters
                '//*[@id="search-filters"]/p',    # The paragraph container
                '//*[@id="search-filters"]',      # The main container
                '//a[contains(@href, "search")]', # Any search-related link
                '//a[contains(text(), "filter")]', # Any filter-related link
                '//a[contains(text(), "Filter")]'  # Capitalized filter
            ]

            element_found = False

            for xpath in search_filter_xpaths:
                try:
                    search_filters = self.driver.find_elements(By.XPATH, xpath)

                    if search_filters and len(search_filters) > 0:
                        element = search_filters[0]

                        print(f"🎯 Found search filter element using: {xpath}")

                        # Check if element is visible and clickable
                        if element.is_displayed() and element.is_enabled():
                            # Move mouse to the element naturally
                            self.actions.move_to_element(element).perform()
                            self.random_delay(0.3, 0.8)

                            # ALWAYS click since this is crucial
                            try:
                                element.click()
                                print("✅ SUCCESS: Clicked search filters - can now progress!")
                                self.random_delay(0.5, 1.2)
                                element_found = True
                                break
                            except Exception as click_error:
                                print(f"⚠️ Click failed, trying JavaScript click...")
                                try:
                                    self.driver.execute_script("arguments[0].click();", element)
                                    print("✅ SUCCESS: JavaScript clicked search filters!")
                                    element_found = True
                                    break
                                except:
                                    print(f"⚠️ JavaScript click also failed for {xpath}")
                                    continue
                        else:
                            print(f"🔍 Element found but not clickable: {xpath}")

                except Exception as e:
                    print(f"🔍 XPath {xpath} not found: {type(e).__name__}")
                    continue

            if not element_found:
                print("⚠️ WARNING: No search filter elements found - this may block progression!")
                # Try to scroll down and look again
                print("🔄 Scrolling down to look for hidden elements...")
                self.driver.execute_script("window.scrollBy(0, 300);")
                self.random_delay(1, 2)

                # Try one more time after scrolling
                for xpath in search_filter_xpaths[:3]:  # Try top 3 again
                    try:
                        search_filters = self.driver.find_elements(By.XPATH, xpath)
                        if search_filters and len(search_filters) > 0:
                            element = search_filters[0]
                            if element.is_displayed():
                                self.actions.move_to_element(element).click().perform()
                                print("✅ SUCCESS: Found and clicked after scrolling!")
                                element_found = True
                                break
                    except:
                        continue

            # Random additional behavior after interaction
            if element_found and random.random() < 0.4:
                self.simulate_human_behavior()

        except Exception as e:
            print(f"🔍 Search filters interaction error: {type(e).__name__}")
            # Don't let this stop the scraper

    def take_random_break(self):
        """Take a random break by visiting other websites with enhanced randomness"""
        try:
            print("🏖️ Taking a random break - wandering to other sites...")

            # Enhanced sites list with more variety
            break_sites = [
                "https://www.google.com",
                "https://www.weather.com",
                "https://www.reddit.com",
                "https://news.google.com",
                "https://www.wikipedia.org",
                "https://www.cnn.com",
                "https://www.bbc.com",
                "https://stackoverflow.com",
                "https://www.youtube.com",
                "https://www.amazon.com",
                "https://www.nytimes.com",
                "https://www.espn.com",
                "https://www.twitter.com",
                "https://www.facebook.com",
                "https://www.instagram.com",
                "https://www.linkedin.com",
                "https://www.forbes.com",
                "https://www.bloomberg.com"
            ]

            # Random number of sites to visit (1-4 sites)
            sites_to_visit = random.randint(1, 4)
            selected_sites = random.sample(break_sites, min(sites_to_visit, len(break_sites)))

            original_window = self.driver.current_window_handle

            for i, site in enumerate(selected_sites):
                try:
                    print(f"  🌐 Visiting {site} ({i+1}/{sites_to_visit})")

                    # Open in new tab
                    self.driver.execute_script(f"window.open('{site}', '_blank');")

                    # Switch to new tab
                    all_windows = self.driver.window_handles
                    self.driver.switch_to.window(all_windows[-1])

                    # Wait for page to load
                    self.random_delay(2, 5)

                    # Enhanced human activity simulation
                    activity_rounds = random.randint(2, 6)
                    for round_num in range(activity_rounds):
                        # Random scrolling
                        if random.random() < 0.8:  # 80% chance
                            scroll_amount = random.randint(100, 800)
                            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                            self.random_delay(0.5, 1.5)

                        # Random mouse movements
                        self.simulate_human_behavior()

                        # Random clicking on safe elements
                        if random.random() < 0.4:  # 40% chance to click something
                            try:
                                # Try to find safe clickable elements
                                safe_elements = []

                                # Look for common safe elements
                                possible_selectors = [
                                    "//body",
                                    "//header",
                                    "//nav",
                                    "//div[@class*='content']",
                                    "//div[@class*='main']",
                                    "//span",
                                    "//p",
                                    "//h1", "//h2", "//h3",
                                    "//div[@role='button']"
                                ]

                                for selector in possible_selectors[:3]:  # Try first 3
                                    try:
                                        elements = self.driver.find_elements(By.XPATH, selector)
                                        if elements:
                                            safe_elements.extend(elements[:2])  # Take first 2
                                    except:
                                        continue

                                if safe_elements:
                                    random_element = random.choice(safe_elements)
                                    if random_element.is_displayed():
                                        # Move to element and click
                                        self.actions.move_to_element(random_element).perform()
                                        self.random_delay(0.2, 0.6)

                                        # Sometimes just hover, sometimes click
                                        if random.choice([True, False]):
                                            try:
                                                random_element.click()
                                                print(f"    🖱️ Clicked a {random_element.tag_name} element")
                                            except:
                                                print(f"    🖱️ Hovered over {random_element.tag_name} element")

                                        self.random_delay(0.3, 1.0)

                            except Exception as click_error:
                                # Safe fallback - just click body
                                try:
                                    body = self.driver.find_element(By.TAG_NAME, "body")
                                    self.actions.move_to_element(body).click().perform()
                                    print(f"    🖱️ Clicked page body")
                                except:
                                    pass

                        # Random delay between activities
                        self.random_delay(0.5, 2.5)

                    # Stay on the page for a realistic amount of time
                    browse_time = random.uniform(3, 18)  # 3-18 seconds
                    print(f"    📖 Browsing for {browse_time:.1f} seconds...")
                    time.sleep(browse_time)

                    # Sometimes scroll back up before leaving
                    if random.random() < 0.3:
                        self.driver.execute_script("window.scrollTo(0, 0);")
                        self.random_delay(0.5, 1.0)

                    # Close the tab
                    self.driver.close()

                except Exception as e:
                    print(f"    ⚠️ Issue with {site}: {type(e).__name__}")
                    try:
                        self.driver.close()
                    except:
                        pass

            # Return to original window
            try:
                self.driver.switch_to.window(original_window)
                print("✓ Returned to main scraping window")
            except:
                # If original window is gone, get a new one
                remaining_windows = self.driver.window_handles
                if remaining_windows:
                    self.driver.switch_to.window(remaining_windows[0])
                    print("✓ Switched to available window")

            # Wait a bit before resuming
            final_break_time = random.uniform(2, 8)
            print(f"🏖️ Break complete - final pause of {final_break_time:.1f} seconds before resuming...")
            time.sleep(final_break_time)

        except Exception as e:
            print(f"🏖️ Break completed with minor issues: {type(e).__name__}")
            # Ensure we're back to a working window
            try:
                windows = self.driver.window_handles
                if windows:
                    self.driver.switch_to.window(windows[0])
            except:
                pass

    def return_to_base_url(self):
        """Return to the base URL and prepare for more processing"""
        try:
            print("🏠 Returning to base URL...")
            base_url = "https://a836-citypay.nyc.gov/citypay/Parking?stage=procurement"

            # Close any extra tabs first
            try:
                while len(self.driver.window_handles) > 1:
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
            except:
                pass

            # Navigate back to base URL
            self.driver.get(base_url)

            # Wait for page to load with human-like behavior
            self.random_delay(2, 4)
            self.simulate_human_behavior()

            # Wait for the violation input field
            try:
                self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="violation-number"]')))
                print("✓ Successfully returned to base URL and page is ready")
                return True
            except TimeoutException:
                print("⚠️ Base URL loaded but violation input not immediately visible")
                return False

        except Exception as e:
            print(f"⚠️ Issue returning to base URL: {e}")
            return False

    def run_scraping_loop(self):
        """Main scraping loop with enhanced stealth and immediate saving"""
        if not self.violation_numbers:
            print("No violation numbers to process")
            return

        if not self.navigate_to_site():
            print("Failed to navigate to website")
            return

        total_numbers = len(self.violation_numbers)
        processed_count = 0
        index = 0  # Initialize index for proper scope

        # Track when to take breaks
        last_break_at = 0
        break_frequency = random.randint(8, 15)  # Take break every 8-15 requests

        for index, violation_number in enumerate(self.violation_numbers, 1):
            print(f"\n--- Processing {index}/{total_numbers}: {violation_number} ---")

            try:                # Random break decision (5% chance each iteration, or forced after break_frequency)
                should_take_break = (
                    (index - last_break_at >= break_frequency) or
                    (index > 1 and random.random() < 0.05)
                )

                if should_take_break and index > 1:
                    print("🏖️ Time for a strategic break!")
                    self.take_random_break()

                    # Return to base URL after break
                    if not self.return_to_base_url():
                        print("⚠️ Failed to return to base URL after break, retrying...")
                        if not self.navigate_to_site():
                            print("❌ Critical: Cannot navigate to site after break")
                            break

                    last_break_at = index
                    break_frequency = random.randint(8, 15)  # Reset break frequency

                # Add random delay between searches using config
                if index > 1:  # Skip delay for first request
                    delay_time = random.uniform(DELAYS['between_requests_min'], DELAYS['between_requests_max'])
                    print(f"Waiting {delay_time:.1f} seconds before next search...")
                    time.sleep(delay_time)

                # Random human behavior before search
                if random.random() < DELAYS['random_behavior_probability']:
                    print("Performing random human behavior...")
                    self.simulate_human_behavior()

                if self.search_violation_number(violation_number):
                    tickets = self.extract_ticket_data(violation_number)

                    # IMMEDIATE SAVING - Save results as soon as they're scraped
                    self.save_results_immediately(tickets, violation_number)

                    # Also add to main data structure
                    self.scraped_data.extend(tickets)
                    processed_count += len(tickets)

                    # Save backup file periodically (every 10 records)
                    if index % 10 == 0:
                        self.save_data_to_json(f'backup/nyc_parking_tickets_backup_{index}.json')

                # Longer random delay occasionally (every 5-10 requests)
                break_frequency_check = random.randint(DELAYS['longer_break_frequency_min'], DELAYS['longer_break_frequency_max'])
                if index % break_frequency_check == 0:
                    longer_delay = random.uniform(DELAYS['longer_break_duration_min'], DELAYS['longer_break_duration_max'])
                    print(f"Taking a longer pause: {longer_delay:.1f} seconds...")
                    time.sleep(longer_delay)

                    # Sometimes simulate tab switching or other activity
                    if random.random() < 0.5:
                        self.simulate_human_behavior()

            except Exception as e:
                print(f"Error processing {violation_number}: {str(e)}")
                # Even on error, save what we have and add some delay
                if self.scraped_data:
                    self.save_data_to_json(f'backup/error_backup_{index}.json')
                time.sleep(random.uniform(2, 5))
                continue

        # Final save
        print(f"\n🎯 Scraping session complete!")
        print(f"📊 Final statistics:")
        print(f"   • Processed: {index}/{total_numbers} violation numbers")
        print(f"   • Total tickets found: {processed_count}")
        print(f"   • Success rate: {(processed_count/total_numbers*100):.1f}%" if total_numbers > 0 else "   • No data to process")

        # Create final backup
        if self.scraped_data:
            final_filename = f"final_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            self.save_data_to_json(final_filename)
            print(f"✓ Final backup saved: {final_filename}")

    def close(self):
        """Clean up and close the driver"""
        try:
            if hasattr(self, 'driver'):
                self.driver.quit()
                print("Browser closed safely")
        except Exception as e:
            print(f"Warning during browser cleanup: {e}")

def main():
    """Main function to run the scraper with enhanced error handling"""
    scraper = None
    try:
        print("=== NYC Parking Ticket Scraper - Maximum Stealth Edition ===")
        print("🚀 Starting enhanced scraping process...")
        print("💾 Results will be saved immediately to prevent data loss")
        print("🏖️ Random breaks included for maximum stealth")
        print("🔍 Search filters interaction enabled")
        print("=" * 60)

        # Create necessary directories
        os.makedirs("results", exist_ok=True)
        os.makedirs("backup", exist_ok=True)

        scraper = NYCParkingTicketScraper()
        scraper.run_scraping_loop()

    except KeyboardInterrupt:
        print("\n⏹️ Scraping interrupted by user")
        if scraper and hasattr(scraper, 'scraped_data') and scraper.scraped_data:
            emergency_filename = f"emergency_save_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            scraper.save_data_to_json(emergency_filename)
            print(f"💾 Emergency save completed: {emergency_filename}")
    except Exception as e:
        print(f"💥 Unexpected error: {str(e)}")
        if scraper and hasattr(scraper, 'scraped_data') and scraper.scraped_data:
            emergency_filename = f"emergency_save_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            scraper.save_data_to_json(emergency_filename)
            print(f"💾 Emergency save completed: {emergency_filename}")
    finally:
        if scraper:
            scraper.close()

if __name__ == "__main__":
    main()