import os
import time
import random
import json
from datetime import datetime

from seleniumbase import SB
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from stealth_config import *  # Contains USER_AGENTS, STEALTH_SCRIPTS, and behavior configs
from proxy_config import proxy_rotator  # Import proxy rotation system

class CaptchaDetectedException(Exception):
    """Custom exception raised when CAPTCHA is detected - triggers proxy change"""
    def __init__(self, violation_number, message="CAPTCHA detected, need to restart with new proxy"):
        self.violation_number = violation_number
        self.message = message
        super().__init__(self.message)

class NYCParkingTicketScraper:
    def __init__(self, sb):
        """Initialize the scraper with SeleniumBase SB (CDP Mode)"""
        self.sb = sb
        self.driver = sb.driver
        self.wait = WebDriverWait(self.driver, 30)
        self.actions = ActionChains(self.driver)
        self.violation_numbers = self.load_violation_numbers()
        self.scraped_data = []
        # Inject stealth scripts before any page loads
        self.execute_stealth_scripts()
        print("✓ SeleniumBase CDP Mode initialized successfully")

    def execute_stealth_scripts(self):
        """Inject stealth scripts via CDP and fallback to execute_script"""
        for script in STEALTH_SCRIPTS:
            try:
                # Add to evaluate on new document for maximum effect
                self.driver.execute_cdp_cmd(
                    "Page.addScriptToEvaluateOnNewDocument", {"source": script}
                )
            except Exception:
                try:
                    self.driver.execute_script(script)
                except Exception as e:
                    print(f"Warning: Could not execute stealth script: {e}")
        print("✓ Stealth scripts injected successfully")

    def simulate_human_behavior(self):
        """Simulate human-like mouse movements and scrolling with improved CDP compatibility"""
        try:
            print("🤖 Simulating human behavior...")

            if MOUSE_MOVEMENTS.get('enabled', False):
                try:
                    movements = random.randint(
                        MOUSE_MOVEMENTS.get('min_movements', 1),
                        MOUSE_MOVEMENTS.get('max_movements', 3)
                    )
                    for i in range(movements):
                        x = random.randint(
                            -MOUSE_MOVEMENTS.get('max_offset_x', 50),
                            MOUSE_MOVEMENTS.get('max_offset_x', 50)
                        )
                        y = random.randint(
                            -MOUSE_MOVEMENTS.get('max_offset_y', 50),
                            MOUSE_MOVEMENTS.get('max_offset_y', 50)
                        )
                        try:
                            # Use regular driver for scrolling with better error handling
                            if hasattr(self.driver, 'execute_script'):
                                self.driver.execute_script(f"window.scrollBy({x//10}, {y//10});")
                        except Exception as scroll_error:
                            # If scrolling fails, just continue without it
                            if "HTTPConnectionPool" not in str(scroll_error):
                                print(f"   ⚠️ Minor scrolling issue: {type(scroll_error).__name__}")
                            # Don't use ActionChains as fallback since it can also cause connection issues
                            pass
                        time.sleep(random.uniform(
                            MOUSE_MOVEMENTS.get('movement_delay_min', 0.1),
                            MOUSE_MOVEMENTS.get('movement_delay_max', 0.3)
                        ))
                except Exception as e:
                    print(f"   ⚠️ Mouse movements failed: {type(e).__name__}")

            if SCROLLING.get('enabled', True):
                try:
                    amount = random.randint(
                        SCROLLING.get('min_scroll', 50),
                        SCROLLING.get('max_scroll', 200)
                    )
                    # Use regular driver for scrolling with better error handling
                    try:
                        if hasattr(self.driver, 'execute_script'):
                            self.driver.execute_script(f"window.scrollBy(0, {amount});")
                            time.sleep(random.uniform(
                                SCROLLING.get('scroll_delay_min', 0.5),
                                SCROLLING.get('scroll_delay_max', 1.0)
                            ))
                            if random.random() < SCROLLING.get('scroll_back_probability', 0.3):
                                self.driver.execute_script(f"window.scrollBy(0, -{amount//2});")
                                time.sleep(random.uniform(
                                    SCROLLING.get('scroll_delay_min', 0.5),
                                    SCROLLING.get('scroll_delay_max', 1.0)
                                ))
                    except Exception as scroll_error:
                        if "HTTPConnectionPool" not in str(scroll_error):
                            print(f"   ⚠️ Scrolling failed: {type(scroll_error).__name__}")
                        # Skip scrolling if there are connection issues
                        pass
                except Exception as e:
                    print(f"   ⚠️ Scrolling behavior failed: {type(e).__name__}")

            print("   ✅ Human behavior simulation completed")

        except Exception as e:
            print(f"   ⚠️ Human behavior simulation error: {type(e).__name__}")
            # Don't let this stop the script

    def human_like_typing(self, element, text: str):
        """Type text with delays and occasional typo correction"""
        if not TYPING_BEHAVIOR.get('enabled', True):
            element.send_keys(text)
            return
        element.clear()
        time.sleep(random.uniform(
            TYPING_BEHAVIOR.get('pre_type_delay_min', 0.5),
            TYPING_BEHAVIOR.get('pre_type_delay_max', 1.0)
        ))
        for ch in text:
            element.send_keys(ch)
            time.sleep(random.uniform(
                TYPING_BEHAVIOR.get('char_delay_min', 0.05),
                TYPING_BEHAVIOR.get('char_delay_max', 0.15)
            ))
        # Occasional typo
        if random.random() < TYPING_BEHAVIOR.get('mistake_probability', 0.02) and len(text) > 3:
            time.sleep(random.uniform(0.2, 0.5))
            element.send_keys(Keys.BACKSPACE)
            time.sleep(random.uniform(0.1, 0.3))
            element.send_keys(text[-1])

    def random_delay(self, min_seconds=1.0, max_seconds=3.0):
        time.sleep(random.uniform(min_seconds, max_seconds))

    def load_violation_numbers(self):
        try:
            with open('v_num.txt') as f:
                nums = [l.strip() for l in f if l.strip()]
            print(f"Loaded {len(nums)} violation numbers")
            return nums
        except FileNotFoundError:
            print("Error: v_num.txt not found")
            return []

    def navigate_to_site(self) -> bool:
        self.create_browser_history()
        url = "https://a836-citypay.nyc.gov/citypay/Parking?stage=procurement"
        print(f"Navigating to: {url}")
        # Use CDP mode for navigation
        self.sb.activate_cdp_mode(url)
        # Wait for page load before any interactions
        self.random_delay(2, 4)
        try:
            # Use CDP mode for waiting
            self.sb.cdp.wait_for_element_visible('//*[@id="violation-number"]', timeout=14)
            print("Page loaded successfully")
            # Only simulate behavior after page is fully loaded and stable
            self.random_delay(1, 2)
            # try:
            #     self.simulate_human_behavior()
            # except Exception as e:
            #     print(f"Warning: Human behavior simulation failed during navigation: {e}")
            return True
        except Exception:
            print("Timeout waiting for violation input")
            return False

    def detect_captcha_error(self) -> bool:
        """
        Detect CAPTCHA error by checking if both 'unable' and 'verify' keywords
        are present in the page source after form submission.

        This method should be called after:
        1. Clicking the search/submit button
        2. Waiting for the page to load (via wait_for_results())
        3. Getting the full page content
        """
        try:
            print("🤖 Checking page source for CAPTCHA error keywords...")

            # Get the full page source using CDP
            time.sleep(7)
            page_source = self.sb.cdp.get_page_source().lower()

            # Check if both keywords are present in the page source
            has_unable = "unable" in page_source
            has_verify = "verify" in page_source

            print(f"   📋 Found 'unable': {has_unable}")
            print(f"   📋 Found 'verify': {has_verify}")

            # CAPTCHA error detected if BOTH keywords are present
            if has_unable and has_verify:
                print(f"🤖 CAPTCHA ERROR DETECTED: Both 'unable' and 'verify' keywords found in page source")
                return True
            else:
                print(f"✅ No CAPTCHA error detected - missing one or both keywords")
                return False

        except Exception as e:
            print(f"⚠️ Error checking for captcha: {type(e).__name__}")
            return False

    def handle_captcha_retry(self, num: str) -> bool:
        """Handle CAPTCHA detection by raising exception to trigger browser restart with new proxy"""
        print(f"🤖 CAPTCHA detected for {num} - Raising exception to restart with new proxy...")
        raise CaptchaDetectedException(num, f"CAPTCHA detected for violation {num}, restarting with new proxy")

    def search_violation_number_internal(self, num: str, is_retry=False) -> bool:
        try:
            print(f"🎯 Starting search for {num}{' (retry)' if is_retry else ''}...")

            # # Add some human behavior before starting
            # try:
            #     self.simulate_human_behavior()
            # except Exception as e:
            #     print(f"Warning: Pre-search human behavior failed: {e}")

            # Try the standard search method first
            try:
                print("📍 Waiting for violation number input field...")
                self.sb.cdp.wait_for_element_visible('//*[@id="violation-number"]', timeout=30)

                print("🧹 Clearing input field...")
                # Use select_all and then type to clear and replace content
                self.sb.cdp.select_all('//*[@id="violation-number"]')
                self.random_delay(0.2, 0.5)

                print("🖱️ Clicking input field...")
                self.sb.cdp.click('//*[@id="violation-number"]')
                self.random_delay(0.3, 0.8)

                # Type using CDP mode with human-like delays
                print(f"⌨️ Typing violation number: {num}")
                if TYPING_BEHAVIOR.get('enabled', True):
                    # Human-like typing with delays - type the entire number at once, then add delays
                    self.sb.cdp.type('//*[@id="violation-number"]', num)
                    # Add a small delay to simulate human typing speed
                    time.sleep(random.uniform(
                        TYPING_BEHAVIOR.get('char_delay_min', 0.05) * len(num),
                        TYPING_BEHAVIOR.get('char_delay_max', 0.15) * len(num)
                    ))
                else:
                    # Fast typing - use set_value for immediate replacement
                    self.sb.cdp.set_value('//*[@id="violation-number"]', num)

                self.random_delay(0.5, 1.0)

                # Click search button using CDP
                print("🔍 Clicking search button...")
                self.sb.cdp.click('//*[@id="by-violation-form"]/div[3]/button')
                print(f"✅ Search initiated for violation number: {num}{' (retry)' if is_retry else ''}")

            except Exception as search_error:
                print(f"⚠️ Standard search failed: {search_error}")
                print("🔄 Attempting fallback method - looking for expanded ticket view...")

                # Fallback: Try to click the expand button to reveal hidden tickets
                try:
                    expand_xpath = '/html/body/div[1]/main/div/div[3]/div/table/tbody/tr[1]/td/div[3]/div[1]/div'
                    print(f"🎯 Clicking expand button at: {expand_xpath}")
                    self.sb.cdp.click(expand_xpath)
                    self.random_delay(1, 2)
                    print("✅ Expand button clicked, tickets should now be visible")
                except Exception as expand_error:
                    print(f"❌ Expand button click failed: {expand_error}")
                    # Try alternative expand button selectors
                    alternative_selectors = [
                        '//div[@class="block-cell"]//div[@class="ico-wrapper"]',
                        '//i[@class="ico ico-caret-right"]',
                        '//div[contains(@class, "block-wrapper")]//div[contains(@class, "block-cell")]',
                        '//div[contains(text(), "Judgment Violations")]//div[@class="ico-wrapper"]',
                        '//div[contains(text(), "Violations")]//div[@class="ico-wrapper"]'
                    ]

                    for selector in alternative_selectors:
                        try:
                            print(f"🔄 Trying alternative selector: {selector}")
                            self.sb.cdp.click(selector)
                            self.random_delay(1, 2)
                            print(f"✅ Alternative expand clicked: {selector}")
                            break
                        except Exception:
                            continue
                    else:
                        print("❌ All expand button attempts failed")
                        return False

            print("⏳ Waiting for results...")
            self.wait_for_results()

            print("🤖 Checking for CAPTCHA...")
            captcha_detected = self.detect_captcha_error()
            if captcha_detected:
                try:
                    time.sleep(random.randint(3, 7))
                    self.sb.cdp.click('//*[@id="by-violation-form"]/div[3]/button')  # Click to refocus input
                    temp_captcha_detected = self.detect_captcha_error()
                    if temp_captcha_detected:
                        raise Exception(f"CAPTCHA detected after refocusing for {num}")
                except Exception as e:
                    if is_retry:
                        print(f"🤖 Captcha detected again on retry for {num} - skipping this violation")
                        return False
                return self.handle_captcha_retry(num)
            else:
                print("✅ No CAPTCHA detected - continuing with extraction")

            print("🔧 Attempting to click search filters...")
            time.sleep(5)
            self.try_click_search_filters_stealthily()

            print(f"✅ Search process completed successfully for {num}")
            return True

        except Exception as e:
            time.sleep(5)
            self.try_click_search_filters_stealthily()
            print(f"❌ Error searching {num}: {e}")
            import traceback
            traceback.print_exc()
            return False


    def search_violation_number(self, num: str) -> bool:
        return self.search_violation_number_internal(num, is_retry=False)

    def wait_for_results(self):
        try:
            # Use CDP mode for waiting for results
            max_wait_time = 30  # seconds
            start_time = time.time()

            while time.time() - start_time < max_wait_time:
                try:
                    # Check if results are loaded using CDP
                    page_source = self.sb.cdp.get_page_source()
                    if ('ticket-' in page_source and '<tr id="ticket-' in page_source) or \
                       'No violations found' in page_source or 'no results' in page_source:
                        time.sleep(2)
                        print("Results loaded")
                        return
                except Exception:
                    pass
                time.sleep(1)
            print("Timeout waiting for search results")
        except Exception as e:
            print(f"Error waiting for results: {e}")

    def extract_ticket_data(self, num: str) -> list:
        tickets = []
        try:
            print(f"🔍 Extracting ticket data for {num}...")
            # Use CDP mode to get page source and parse
            page_source = self.sb.cdp.get_page_source()

            # Check if ticket is flagged as deleted - skip extraction if found
            if 'flagged as deleted' in page_source.lower():
                print(f"🚫 Ticket {num} is flagged as deleted - skipping extraction")
                return tickets  # Return empty list and move to next violation

            # Check for expanded format first (tbody class="parking-results")
            if 'tbody class="parking-results"' in page_source:
                print(f"📋 Found expanded format tickets for {num}")
                tickets = self.parse_expanded_ticket_format(page_source, num)
                if tickets:
                    print(f"✅ Successfully extracted {len(tickets)} tickets from expanded format")
                    return tickets
                else:
                    print(f"⚠️ No tickets extracted from expanded format, trying standard format...")

            # Check for standard format (ticket- rows)
            if 'ticket-' not in page_source or '<tr id="ticket-' not in page_source:
                print(f"No tickets found in either format for violation number: {num}")
                # Check for "No violations found" or similar messages
                if any(msg in page_source.lower() for msg in ['no violations found', 'no results', 'no records found']):
                    print(f"✓ Confirmed: No violations found for {num}")
                else:
                    print(f"⚠️ Warning: No ticket rows found, but page might still be loading")
                return tickets

            print(f"📄 Found standard format ticket data for {num}")

            # Reconnect to use WebDriver for complex DOM parsing if needed
            try:
                # Try to reconnect temporarily for element parsing
                if not self.sb.is_connected():
                    print("🔄 Temporarily reconnecting for data extraction...")
                    self.sb.reconnect()

                # Use regular selenium for complex parsing since CDP doesn't support find_elements well
                rows = self.driver.find_elements(By.XPATH, "//tr[starts-with(@id,'ticket-')]")
                if not rows:
                    print(f"No ticket rows found via WebDriver for violation number: {num}")
                    # Disconnect again to maintain stealth
                    self.sb.disconnect()
                    return tickets

                print(f"Found {len(rows)} ticket(s) in standard format for violation number: {num}")
                for r in rows:
                    try:
                        data = self.parse_ticket_row(r, num)
                        if data:
                            tickets.append(data)
                            print(f"✓ Parsed ticket: {data.get('ticket_id', 'Unknown')} - {data.get('violation_number', 'Unknown')}")
                    except Exception as e:
                        print(f"Error parsing ticket row: {str(e)}")
                        continue

                # Disconnect again to maintain stealth
                print("🔒 Disconnecting WebDriver to maintain stealth...")
                self.sb.disconnect()

            except Exception as extraction_error:
                print(f"⚠️ WebDriver extraction failed: {extraction_error}")
                # WebDriver extraction failed, return empty tickets list
                print("🔄 WebDriver failed, returning empty results...")
                # tickets remains as empty list

        except Exception as e:
            print(f"Error extracting ticket data: {str(e)}")
            import traceback
            traceback.print_exc()

        print(f"✓ Extraction complete for {num}: {len(tickets)} tickets found")
        return tickets

    def parse_expanded_ticket_format(self, page_source: str, num: str) -> list:
        """Parse tickets from the expanded format shown in tbody.parking-results"""
        tickets = []
        try:
            print(f"🔍 Parsing expanded ticket format for {num}...")

            # Look for tbody with class "parking-results"
            if 'tbody class="parking-results"' not in page_source:
                print(f"⚠️ No parking-results tbody found for {num}")
                return tickets

            # Reconnect temporarily for DOM parsing
            try:
                if not self.sb.is_connected():
                    print("🔄 Temporarily reconnecting for expanded format parsing...")
                    self.sb.reconnect()

                # Look for all ticket rows in the expanded format
                rows = self.driver.find_elements(By.XPATH, "//tr[starts-with(@id,'ticket-')]")
                if not rows:
                    print(f"No ticket rows found in expanded format for {num}")
                    self.sb.disconnect()
                    return tickets

                print(f"Found {len(rows)} ticket(s) in expanded format for {num}")
                for row in rows:
                    try:
                        # Check if this row is visible or has style="display: none;"
                        style = row.get_attribute('style') or ''
                        if 'display: none' in style:
                            print(f"  ⚠️ Skipping hidden ticket row")
                            continue

                        # Parse the expanded format ticket row
                        data = self.parse_expanded_ticket_row(row, num)
                        if data:
                            tickets.append(data)
                            print(f"✓ Parsed expanded ticket: {data.get('ticket_id', 'Unknown')} - {data.get('violation_number', 'Unknown')}")
                    except Exception as e:
                        print(f"Error parsing expanded ticket row: {str(e)}")
                        continue

                # Disconnect again to maintain stealth
                print("🔒 Disconnecting WebDriver after expanded parsing...")
                self.sb.disconnect()

            except Exception as parsing_error:
                print(f"⚠️ Expanded format parsing failed: {parsing_error}")

        except Exception as e:
            print(f"Error in expanded ticket parsing: {str(e)}")
            import traceback
            traceback.print_exc()

        print(f"✓ Expanded parsing complete for {num}: {len(tickets)} tickets found")
        return tickets

    def parse_expanded_ticket_row(self, row, num: str) -> dict:
        """Parse a single ticket row from the expanded format"""
        try:
            t = {
                'search_violation_number': num,
                'extracted_at': datetime.now().isoformat(),
                'ticket_id': '', 'violation_number': '', 'license_plate': '',
                'violation_type': '', 'date': '', 'liability_amount': '',
                'paid_amount': '', 'amount_due': '', 'payment_amount': '',
                'view_ticket_link': '', 'status': ''
            }

            # Extract ticket ID from row id attribute
            tid = row.get_attribute('id') or ''
            if tid.startswith('ticket-'):
                t['ticket_id'] = tid.replace('ticket-', '')

            # Check if this is a paid/not-addable ticket
            class_attr = row.get_attribute('class') or ''
            if 'not-addable' in class_attr:
                t['status'] = 'paid_in_full'

            # Extract cells from the expanded format
            cells = row.find_elements(By.TAG_NAME, 'td')
            if len(cells) >= 8:
                # Cell 1 (index 1): Violation number and view ticket link
                if len(cells) > 1:
                    violation_cell = cells[1]
                    # Extract violation number from span
                    spans = violation_cell.find_elements(By.TAG_NAME, 'span')
                    if spans:
                        t['violation_number'] = spans[0].text.strip()
                    # Extract view ticket link
                    links = violation_cell.find_elements(By.TAG_NAME, 'a')
                    if links:
                        t['view_ticket_link'] = links[0].get_attribute('href')

                # Cell 2 (index 2): License plate
                if len(cells) > 2:
                    license_cell = cells[2]
                    spans = license_cell.find_elements(By.TAG_NAME, 'span')
                    if spans:
                        t['license_plate'] = spans[0].text.strip()

                # Cell 3 (index 3): Violation type
                if len(cells) > 3:
                    t['violation_type'] = cells[3].text.strip()

                # Cell 4 (index 4): Date
                if len(cells) > 4:
                    t['date'] = cells[4].text.strip()

                # Cell 5 (index 5): Liability amount
                if len(cells) > 5:
                    liability_cell = cells[5]
                    data_elements = liability_cell.find_elements(By.TAG_NAME, 'data')
                    if data_elements:
                        t['liability_amount'] = data_elements[0].text.strip()

                # Cell 6 (index 6): Paid amount
                if len(cells) > 6:
                    paid_cell = cells[6]
                    data_elements = paid_cell.find_elements(By.TAG_NAME, 'data')
                    if data_elements:
                        t['paid_amount'] = data_elements[0].text.strip()

                # Cell 7 (index 7): Amount due
                if len(cells) > 7:
                    due_cell = cells[7]
                    data_elements = due_cell.find_elements(By.TAG_NAME, 'data')
                    if data_elements:
                        t['amount_due'] = data_elements[0].text.strip()

                    # Check for "Payment in process" or "Paid in Full" messages
                    if 'Payment of' in due_cell.text and 'is in process' in due_cell.text:
                        t['status'] = 'payment_in_process'

                # Cell 8 (index 8): Payment amount input
                if len(cells) > 8:
                    payment_cell = cells[8]
                    inputs = payment_cell.find_elements(By.XPATH, './/input[@name="paymentAmount"]')
                    if inputs:
                        t['payment_amount'] = inputs[0].get_attribute('value') or ''

                # Cell 9 (index 9): Add to cart / status
                if len(cells) > 9:
                    cart_cell = cells[9]
                    if 'Paid in Full' in cart_cell.text:
                        t['status'] = 'paid_in_full'

            print(f"Extracted expanded ticket: {t['ticket_id']} - {t['violation_number']} - Status: {t['status']}")
            return t

        except Exception as e:
            print(f"Error parsing expanded ticket row: {str(e)}")
            return {
                'search_violation_number': num,
                'extracted_at': datetime.now().isoformat(),
                'ticket_id': '', 'violation_number': '', 'license_plate': '',
                'violation_type': '', 'date': '', 'liability_amount': '',
                'paid_amount': '', 'amount_due': '', 'payment_amount': '',
                'view_ticket_link': '', 'status': 'error', 'error': str(e)
            }

    def parse_ticket_row(self, row, num: str) -> dict:
        try:
            t = {
                'search_violation_number': num,
                'extracted_at': datetime.now().isoformat(),
                'ticket_id': '', 'violation_number': '', 'license_plate': '',
                'violation_type': '', 'date': '', 'liability_amount': '',
                'paid_amount': '', 'amount_due': '', 'payment_amount': '',
                'view_ticket_link': ''
            }

            # Extract ticket ID from row id attribute
            tid = row.get_attribute('id') or ''
            if tid.startswith('ticket-'):
                t['ticket_id'] = tid.replace('ticket-', '')

            # Extract cells
            cells = row.find_elements(By.TAG_NAME, 'td')
            if len(cells) >= 8:
                # Violation number and view ticket link (usually in 2nd cell, index 1)
                if len(cells) > 1:
                    violation_cell = cells[1]
                    # Extract violation number
                    sp = violation_cell.find_elements(By.TAG_NAME, 'span')
                    if sp: t['violation_number'] = sp[0].text.strip()
                    # Extract view ticket link
                    ln = violation_cell.find_elements(By.TAG_NAME, 'a')
                    if ln: t['view_ticket_link'] = ln[0].get_attribute('href')

                # License plate (usually in 3rd cell, index 2)
                if len(cells) > 2:
                    license_cell = cells[2]
                    sp2 = license_cell.find_elements(By.TAG_NAME, 'span')
                    if sp2: t['license_plate'] = sp2[0].text.strip()

                # Violation type (usually in 4th cell, index 3)
                if len(cells) > 3:
                    t['violation_type'] = cells[3].text.strip()

                # Date (usually in 5th cell, index 4)
                if len(cells) > 4:
                    t['date'] = cells[4].text.strip()

                # Liability amount (usually in 6th cell, index 5)
                if len(cells) > 5:
                    data_elements = cells[5].find_elements(By.TAG_NAME, 'data')
                    if data_elements:
                        t['liability_amount'] = data_elements[0].text.strip()

                # Paid amount (usually in 7th cell, index 6)
                if len(cells) > 6:
                    data_elements = cells[6].find_elements(By.TAG_NAME, 'data')
                    if data_elements:
                        t['paid_amount'] = data_elements[0].text.strip()

                # Amount due (usually in 8th cell, index 7)
                if len(cells) > 7:
                    data_elements = cells[7].find_elements(By.TAG_NAME, 'data')
                    if data_elements:
                        t['amount_due'] = data_elements[0].text.strip()

                # Payment amount (usually in 9th cell, index 8)
                if len(cells) > 8:
                    inp = cells[8].find_elements(By.XPATH, './/input[@name="paymentAmount"]')
                    if inp: t['payment_amount'] = inp[0].get_attribute('value')

            print(f"Extracted ticket data: {t['ticket_id']} - {t['violation_number']}")
            return t
        except Exception as e:
            print(f"Error parsing ticket row: {str(e)}")
            return {
                'search_violation_number': num,
                'extracted_at': datetime.now().isoformat(),
                'ticket_id': '', 'violation_number': '', 'license_plate': '',
                'violation_type': '', 'date': '', 'liability_amount': '',
                'paid_amount': '', 'amount_due': '', 'payment_amount': '',
                'view_ticket_link': '', 'error': str(e)
            }

    def save_data_to_json(self, fname='nyc_parking_tickets.json'):
        try:
            with open(fname, 'w', encoding='utf-8') as f:
                json.dump(self.scraped_data, f, indent=2, ensure_ascii=False)
            print(f"Data saved to {fname}")
            print(f"Total records saved: {len(self.scraped_data)}")
        except Exception as e:
            print(f"Error saving data to JSON: {str(e)}")

    def save_results_immediately(self, tickets: list, num: str):
        """Save results immediately as they are scraped to prevent data loss"""
        try:
            # Always save, even if tickets list is empty (to record the attempt)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            os.makedirs("results", exist_ok=True)

            # Create result entry
            result_entry = {
                'violation_number': num,
                'timestamp': ts,
                'tickets_found': len(tickets),
                'tickets': tickets,
                'status': 'success' if tickets else 'no_results'
            }

            # Save individual file for this violation number
            indiv = f"results/violation_{num}_{ts}.json"
            with open(indiv,'w',encoding='utf-8') as f:
                json.dump(result_entry, f, indent=2, ensure_ascii=False)

            # Also append to master file immediately
            master = "results/all_tickets_live.json"
            existing = []
            if os.path.exists(master):
                try:
                    with open(master) as mf:
                        existing = json.load(mf)
                except:
                    existing = []
            existing.append(result_entry)
            with open(master,'w',encoding='utf-8') as mf:
                json.dump(existing, mf, indent=2, ensure_ascii=False)

            # Create a simple CSV for quick viewing
            csv_file = "results/tickets_summary.csv"
            csv_exists = os.path.exists(csv_file)
            with open(csv_file, 'a', encoding='utf-8') as cf:
                if not csv_exists:
                    cf.write("Violation_Number,Timestamp,Tickets_Found,Status\n")
                cf.write(f"{num},{ts},{len(tickets)},{'success' if tickets else 'no_results'}\n")

            print(f"✓ Results saved immediately: {len(tickets)} tickets for violation {num}")
            print(f"  Individual file: {indiv}")
            print(f"  Master file updated: {master}")
            print(f"  CSV summary updated: {csv_file}")

            if tickets:
                for ticket in tickets:
                    print(f"    📋 Ticket: {ticket.get('ticket_id', 'Unknown')} - Amount Due: {ticket.get('amount_due', 'Unknown')}")
            else:
                print(f"    📋 No tickets found for {num}")

        except Exception as e:
            print(f"Warning: Could not save results immediately: {e}")
            import traceback
            traceback.print_exc()

    def try_click_search_filters_stealthily(self):
        """Try to click search filters in a stealthy way - CRUCIAL for progression"""
        try:
            # Always attempt this since it's crucial for progression
            print("🔍 Attempting to interact with search filters (CRUCIAL STEP)...")
            self.random_delay(0.5, 1.5)

            # Multiple XPath options to try (in order of preference)
            search_filter_xpaths = [
                '//*[@id="search-filters"]/p/a',  # Most specific path - the crucial one
                '//*[@id="search-filters"]//a',   # Any link within search-filters
                '//*[@id="search-filters"]/p',    # The paragraph container
                '//*[@id="search-filters"]',      # The main container
            ]

            element_found = False

            for xpath in search_filter_xpaths:
                try:
                    # Try to click using CDP first
                    try:
                        self.sb.cdp.click(xpath)
                        print(f"✅ SUCCESS: CDP clicked search filters using {xpath}")
                        self.random_delay(0.5, 1.2)
                        element_found = True
                        break
                    except Exception:
                        # Fallback to regular selenium
                        search_filters = self.driver.find_elements(By.XPATH, xpath)
                        if search_filters and len(search_filters) > 0:
                            element = search_filters[0]
                            print(f"🎯 Found search filter element using: {xpath}")

                            if element.is_displayed() and element.is_enabled():
                                try:
                                    element.click()
                                    print("✅ SUCCESS: Clicked search filters - can now progress!")
                                    self.random_delay(0.5, 1.2)
                                    element_found = True
                                    break
                                except Exception:
                                    try:
                                        self.driver.execute_script("arguments[0].click();", element)
                                        print("✅ SUCCESS: JavaScript clicked search filters!")
                                        element_found = True
                                        break
                                    except:
                                        continue

                except Exception as e:
                    print(f"🔍 XPath {xpath} not found: {type(e).__name__}")
                    continue

            if not element_found:
                print("⚠️ WARNING: No search filter elements found - this may block progression!")
                # Try to scroll down and look again
                print("🔄 Scrolling down to look for hidden elements...")
                try:
                    # Use CDP scroll methods instead of execute_script
                    self.sb.cdp.scroll_down(amount=300)
                except Exception:
                    try:
                        # Fallback to regular driver
                        self.driver.execute_script("window.scrollBy(0, 300);")
                    except Exception as scroll_error:
                        print(f"   ⚠️ Scrolling failed: {type(scroll_error).__name__}")
                self.random_delay(1, 2)

            # Random additional behavior after interaction
            if element_found and random.random() < 0.4:
                self.simulate_human_behavior()

        except Exception as e:
            print(f"🔍 Search filters interaction error: {type(e).__name__}")
            # Don't let this stop the scraper

    def create_browser_history(self):
        if not BROWSER_HISTORY.get('enabled'): return
        try:
            print("Creating browser history...")
            # Enhanced sites list with more variety
            sites = [
                "https://www.google.com", "https://www.wikipedia.org",
                "https://www.news.google.com", "https://www.weather.com",
                "https://www.cnn.com", "https://www.reddit.com",
                "https://www.bbc.com", "https://www.nytimes.com",
                "https://www.espn.com", "https://www.forbes.com",
                "https://www.bloomberg.com", "https://stackoverflow.com",
                "https://www.github.com"
            ]

            # Random number of sites to visit (1-3 for initial history)
            visit_count = random.randint(1, 3)
            selected_sites = random.sample(sites, min(visit_count, len(sites)))

            original = self.driver.current_window_handle
            for site in selected_sites:
                try:
                    print(f"  📖 Adding to history: {site}")
                    self.driver.execute_script(f"window.open('{site}','_blank');")
                    time.sleep(random.uniform(1,2))
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
                    self.driver.switch_to.window(original)
                    time.sleep(random.uniform(0.3, 0.8))

                except Exception as e:
                    print(f"  ⚠️ Issue with history site {site}: {type(e).__name__}")
                    try:
                        self.driver.close()
                        self.driver.switch_to.window(original)
                    except:
                        pass
            print("✓ Browser history created successfully")
        except Exception as e:
            print(f"Warning: Could not create browser history: {e}")

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

            orig = self.driver.current_window_handle
            for i, site in enumerate(selected_sites):
                try:
                    print(f"  🌐 Visiting {site} ({i+1}/{sites_to_visit})")
                    self.driver.execute_script(f"window.open('{site}','_blank');")
                    self.driver.switch_to.window(self.driver.window_handles[-1])

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
                                # Look for safe clickable elements
                                safe_elements = []
                                possible_selectors = [
                                    "//body", "//header", "//nav",
                                    "//div[@class*='content']", "//div[@class*='main']",
                                    "//span", "//p", "//h1", "//h2", "//h3",
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

                    self.driver.close()

                except Exception as e:
                    print(f"    ⚠️ Issue with {site}: {type(e).__name__}")
                    try:
                        self.driver.close()
                    except:
                        pass

            # Return to original window
            try:
                self.driver.switch_to.window(orig)
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

    def return_to_base_url(self) -> bool:
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

            # Navigate back to base URL using CDP mode
            self.sb.activate_cdp_mode(base_url)

            # Wait for page to load with human-like behavior
            self.random_delay(1,3)

            # Only simulate behavior after ensuring page is stable
            try:
                self.simulate_human_behavior()
            except Exception as e:
                print(f"Warning: Human behavior simulation failed during return: {e}")

            # Wait for the violation input field using CDP
            try:
                self.sb.cdp.wait_for_element_visible('//*[@id="violation-number"]', timeout=30)
                print("✓ Successfully returned to base URL and page is ready")
                return True
            except Exception:
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

        print("🚀 Starting violation number processing...")
        total = len(self.violation_numbers)
        count = 0
        last_break = 0
        freq = random.randint(8,15)
        idx = 0  # Initialize idx variable

        for idx, num in enumerate(self.violation_numbers, start=1):
            print(f"\n--- Processing {idx}/{total}: {num} ---")
            try:
                # Random break decision (5% chance each iteration, or forced after break_frequency)
                should_take_break = (
                    (idx - last_break >= freq) or
                    (idx > 1 and random.random() < 0.05)
                )

                if should_take_break and idx > 1:
                    print("🏖️ Time for a strategic break!")
                    self.take_random_break()

                    # Return to base URL after break
                    if not self.return_to_base_url():
                        print("⚠️ Failed to return to base URL after break, retrying...")
                        if not self.navigate_to_site():
                            print("❌ Critical: Cannot navigate to site after break")
                            break

                    last_break = idx
                    freq = random.randint(8,15)

                # Add random delay between searches using config with fallback
                if idx > 1:  # Skip delay for first request
                    try:
                        delay_time = random.uniform(
                            DELAYS.get('between_requests_min', 2.0),
                            DELAYS.get('between_requests_max', 5.0)
                        )
                        print(f"Waiting {delay_time:.1f} seconds before next search...")
                        time.sleep(delay_time)
                    except Exception as e:
                        print(f"Warning: Delay config issue, using default: {e}")
                        time.sleep(random.uniform(2, 5))
                print(f"🔍 Starting search for violation number: {num}")
                search_success = self.search_violation_number(num)

                if search_success:
                    print(f"✅ Search completed for {num}, extracting data...")
                    tickets = self.extract_ticket_data(num)
                else:
                    print(f"❌ Search failed for violation number: {num}")
                    tickets = []  # Empty list for failed searches

                # IMMEDIATE SAVING - Save results as soon as they're scraped (even if empty)
                self.save_results_immediately(tickets, num)

                # Also add to main data structure
                self.scraped_data.extend(tickets)
                count += len(tickets)

                # Save backup file periodically (every 10 records)
                if idx % 10 == 0:
                    os.makedirs("backup", exist_ok=True)
                    self.save_data_to_json(f'backup/nyc_parking_tickets_backup_{idx}.json')

                # Longer random delay occasionally (every 5-10 requests) with fallback
                try:
                    break_frequency_check = random.randint(
                        DELAYS.get('longer_break_frequency_min', 5),
                        DELAYS.get('longer_break_frequency_max', 10)
                    )
                    if idx % break_frequency_check == 0:
                        longer_delay = random.uniform(
                            DELAYS.get('longer_break_duration_min', 10.0),
                            DELAYS.get('longer_break_duration_max', 20.0)
                        )
                        print(f"Taking a longer pause: {longer_delay:.1f} seconds...")
                        time.sleep(longer_delay)

                        # Sometimes simulate tab switching or other activity
                        if random.random() < 0.5:
                            try:
                                self.simulate_human_behavior()
                            except Exception as e:
                                print(f"Warning: Human behavior during break failed: {e}")
                except Exception as e:
                    print(f"Warning: Break frequency config issue: {e}")

            except Exception as e:
                print(f"Error processing {num}: {str(e)}")
                # Even on error, save what we have and add some delay
                if self.scraped_data:
                    os.makedirs("backup",exist_ok=True)
                    self.save_data_to_json(f'backup/error_backup_{idx}.json')
                time.sleep(random.uniform(2,5))
                continue

        # Final save
        print(f"\n🎯 Scraping session complete!")
        print(f"📊 Final statistics:")
        print(f"   • Processed: {idx}/{total} violation numbers")
        print(f"   • Total tickets found: {count}")
        print(f"   • Success rate: {(count/total*100):.1f}%" if total > 0 else "   • No data to process")

        # Create final backup
        if self.scraped_data:
            fn = f"final_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            self.save_data_to_json(fn)
            print(f"✓ Final backup saved: {fn}")

    def close(self):
        try:
            self.driver.quit()
            print("Browser closed")
        except Exception as e:
            print(f"Cleanup error: {e}")


def run_scraping_session(proxy_string, used_proxies=None):
    """Run a single scraping session with the given proxy"""
    if used_proxies is None:
        used_proxies = set()

    if proxy_string:
        print(f"🌐 Using rotating proxy: {proxy_string}")
        used_proxies.add(proxy_string)
    else:
        print("🌐 Using direct connection (no proxy)")

    with SB(
        uc=True,
        headless=False,
        proxy=proxy_string,  # SeleniumBase authenticated proxy format (or None for direct)
        # Removed conflicting parameters that interfere with proxy authentication:
        # user_data_dir, agent, undetectable, incognito, chromium_arg
    ) as sb:
        scraper = NYCParkingTicketScraper(sb)
        try:
            scraper.run_scraping_loop()
            return True, used_proxies, None  # Success
        except CaptchaDetectedException as e:
            print(f"🤖 CAPTCHA detected: {e.message}")
            # Save any data collected before CAPTCHA
            if scraper.scraped_data:
                emergency = f"captcha_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                scraper.save_data_to_json(emergency)
                print(f"💾 Saved data before CAPTCHA restart: {emergency}")
            return False, used_proxies, e.violation_number  # CAPTCHA detected, need restart
        except KeyboardInterrupt:
            print("Interrupted by user")
            if scraper.scraped_data:
                emergency = f"emergency_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                scraper.save_data_to_json(emergency)
            return True, used_proxies, None  # User interrupted, don't restart
        except Exception as e:
            print(f"Unexpected error: {e}")
            if scraper.scraped_data:
                emergency = f"error_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                scraper.save_data_to_json(emergency)
            return True, used_proxies, None  # Other error, don't restart
        finally:
            scraper.close()

def main():
    print("=== NYC Parking Ticket Scraper - SeleniumBase CDP Mode Edition ===")
    print("🔄 Enhanced with CAPTCHA-triggered proxy rotation")
    os.makedirs("results", exist_ok=True)
    os.makedirs("backup", exist_ok=True)

    used_proxies = set()
    max_proxy_attempts = 5  # Maximum number of different proxies to try
    current_attempt = 0
    success = False  # Initialize success variable

    while current_attempt < max_proxy_attempts:
        current_attempt += 1
        print(f"\n🚀 Starting scraping session #{current_attempt}")

        # Get a new proxy that hasn't been used yet
        proxy_string = None
        attempts_to_get_new_proxy = 0
        max_attempts_for_new_proxy = 10  # Prevent infinite loop

        while attempts_to_get_new_proxy < max_attempts_for_new_proxy:
            proxy_string = proxy_rotator.get_seleniumbase_proxy_with_fallback(use_random=True)

            if proxy_string is None or proxy_string not in used_proxies:
                break  # Found unused proxy or no proxy

            attempts_to_get_new_proxy += 1
            print(f"   🔄 Proxy already used, getting another... (attempt {attempts_to_get_new_proxy})")

        if attempts_to_get_new_proxy >= max_attempts_for_new_proxy:
            print("⚠️ Warning: Could not find unused proxy, using random proxy anyway")
            proxy_string = proxy_rotator.get_seleniumbase_proxy_with_fallback(use_random=True)

        # Run scraping session
        success, used_proxies, failed_violation = run_scraping_session(proxy_string, used_proxies)

        if success:
            print("✅ Scraping session completed successfully!")
            break
        else:
            print(f"🤖 CAPTCHA detected for violation: {failed_violation}")
            print(f"📊 Used proxies so far: {len(used_proxies)}")

            if current_attempt < max_proxy_attempts:
                wait_time = random.uniform(10, 30)  # Wait 10-30 seconds between restarts
                print(f"⏳ Waiting {wait_time:.1f} seconds before restarting with new proxy...")
                time.sleep(wait_time)
            else:
                print("❌ Maximum proxy attempts reached. Consider running again later.")
                break

    print(f"\n📊 Final Statistics:")
    print(f"   • Total proxy attempts: {current_attempt}")
    print(f"   • Proxies used: {len(used_proxies)}")
    print(f"   • Session result: {'Success' if success else 'CAPTCHA limit reached'}")

if __name__ == "__main__":
    main()
