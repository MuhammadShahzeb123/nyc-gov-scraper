from seleniumbase import SB
import re
import os
import json
import random
import time
import datetime
from proxy_config import proxy_rotator  # Import proxy rotation system

class RateLimitExceededException(Exception):
    """Custom exception raised when rate limit is detected - triggers proxy change"""
    def __init__(self, client_id, ticket_id, message="Rate limit exceeded, need to restart with new proxy"):
        self.client_id = client_id
        self.ticket_id = ticket_id
        self.message = message
        super().__init__(self.message)

class NYCDMVWebSummonsScraper:
    def __init__(self, client_id=None, ticket_id=None):
        """Initialize the scraper with data storage"""
        self.scraped_data = []
        self.client_id = client_id
        self.ticket_id = ticket_id
        self.results_dir = "results"
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)

    def generate_random_gmail(self):
        """Generate a random gmail address"""
        prefixes = ["john", "jane", "mike", "sarah", "david", "emma", "alex", "lisa", "chris", "anna"]
        suffixes = ["123", "456", "789", "2024", "2025", "test", "demo", "temp"]

        prefix = random.choice(prefixes)
        suffix = random.choice(suffixes)

        return f"{prefix}{suffix}@gmail.com"

    def scrape_tickets_with_regex(self, sb):
        """Scrape all tickets using regex pattern - EXACT SAME AS dmb_ny.py"""
        sb.cdp.sleep(5)  # Ensure page is fully loaded
        print("🔍 Scraping tickets using regex...")

        try:
            # Get page source
            page_source = sb.cdp.get_page_source()

            # EXACT SAME regex pattern from dmb_ny.py
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
                    'extracted_at': time.strftime('%Y-%m-%dT%H:%M:%S')
                }
                tickets.append(ticket_data)
                print(f"Found ticket: {ticket_data['ticket_number']} - {ticket_data['violation']}")

            if tickets:
                print(f"✓ Successfully scraped {len(tickets)} tickets")
                self.scraped_data.extend(tickets)
            else:
                print("No tickets found with regex pattern")
                # Debug: Save page source to check what we're getting
                debug_file = os.path.join(self.results_dir, 'debug_page_source.html')
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(page_source)
                print(f"Debug: Page source saved to {debug_file}")

        except Exception as e:
            print(f"Error scraping tickets with regex: {e}")

    def save_results(self, filename='dmv_tickets_sb.json'):
        """Save scraped data to JSON file"""
        if not self.scraped_data:
            print("No data to save")
            return
        filename_name = filename.split('.')[0]
        filename = f"{filename_name}_{self.client_id}_{self.ticket_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.results_dir, filename)
        try:
            with open(filepath, 'w') as f:
                json.dump(self.scraped_data, f, indent=4)
            print(f"✅ Results saved to {filepath}")
        except Exception as e:
            print(f"Error saving results: {e}")

    def reload_page_again_and_again(self, sb):
        if "ERR" in sb.cdp.get_page_source():
            sb.cdp.reload_page()
            time.sleep(2)
            if "ERR" in sb.cdp.get_page_source() or "" in sb.cdp.get_page_source():
                sb.cdp.reload_page()
                time.sleep(2)
        if "ERR" in sb.cdp.get_page_source():
            self.reload_page_again_and_again(sb)

    def check_for_rate_limit(self, sb):
        """Check if the page source contains rate limit messages and raise exception if found"""
        try:
            page_source = sb.cdp.get_page_source().lower()

            # Rate limit patterns to check for
            rate_limit_patterns = [
                "exceeded the maximum number",
                "too many requests",
                "rate limit exceeded",
                "maximum number of requests",
                "request limit exceeded",
                "too many attempts",
                "access temporarily blocked",
                "temporarily unavailable",
                "service temporarily unavailable",
                "maximum attempts exceeded"
            ]

            # Check for any of these patterns
            for pattern in rate_limit_patterns:
                if pattern in page_source:
                    print(f"🚫 RATE LIMIT DETECTED: Found pattern '{pattern}'")
                    raise RateLimitExceededException(
                        self.client_id,
                        self.ticket_id,
                        f"Rate limit detected: {pattern}"
                    )

            return False  # No rate limit detected

        except RateLimitExceededException:
            # Re-raise the rate limit exception
            raise
        except Exception as e:
            print(f"⚠️ Error checking for rate limit: {type(e).__name__}")
            return False

    def run_scraping_workflow(self):
        """Execute the complete scraping workflow - simple and clean"""
        # Get proxy configuration for SeleniumBase with validation
        proxy_string = proxy_rotator.get_seleniumbase_proxy_with_fallback(use_random=True)
        if proxy_string:
            print(f"🌐 Using rotating proxy: {proxy_string}")
        else:
            print("🌐 Using direct connection (no proxy)")

        # Simple Chrome setup - avoid conflicts with existing Chrome instances
        with SB(
            uc=True,
            headless=False,
            proxy=proxy_string,  # SeleniumBase authenticated proxy format (or None for direct)
            # Remove extension_dir and user_data_dir to avoid conflicts
            # extension_dir="extensions",
            # user_data_dir="chrome_profile"
        ) as sb:

            print("🚀 Starting NYC DMV Web Summons Scraper...")

            # Open the main page
            print("📋 Opening NYC DMV Web Summons page...")
            sb.activate_cdp_mode("https://process.dmv.ny.gov/WebSummons/")
            self.reload_page_again_and_again(sb)
            # Check for rate limit after initial page load
            self.check_for_rate_limit(sb)
            time.sleep(3)

            # Click the first submit button
            print("🖱️ Clicking first submit button...")
            try:
                sb.cdp.wait_for_element_visible('//*[@id="submit"]', timeout=60000)
                sb.cdp.click('//*[@id="submit"]')
            except Exception as e:
                self.reload_page_again_and_again(sb)
            self.reload_page_again_and_again(sb)
            # Check for rate limit after first submit
            self.check_for_rate_limit(sb)
            time.sleep(2)

            # Fill in the form details simply
            print("📝 Filling in form details...")
            try:
                sb.cdp.wait_for_element_visible('//*[@id="sClientID"]', timeout=None)
                print(f"   • Client ID: {self.client_id}")
                sb.cdp.type('//*[@id="sClientID"]', self.client_id)

                time.sleep(1)

                print(f"   • Ticket Number: {self.ticket_id}")
                sb.cdp.type('#sTicketNum', self.ticket_id)

                time.sleep(1)

                # Generate and fill email addresses
                random_email = self.generate_random_gmail()
                print(f"   • Email: {random_email}")

                sb.cdp.type('#sEmailAddress', random_email)
                time.sleep(1)

                sb.cdp.type('#sEmailAddress2', random_email)
                time.sleep(2)

                # Click the final submit button
                print("🖱️ Clicking final submit button...")
                sb.cdp.scroll_into_view('/html/body/div[1]/div[5]/form/div[2]/button')
                sb.cdp.wait_for_element_visible('/html/body/div[1]/div[5]/form/div[2]/button', timeout=60000)
                try:
                    sb.cdp.click('//*[@id="submit order"]')
                except Exception as e:
                    sb.cdp.click('/html/body/div[1]/div[5]/form/div[2]/button')  # Fallback for different button ID
                time.sleep(5)
                # Check for rate limit after final submit
                self.check_for_rate_limit(sb)
            except Exception as e:
                print(f"Error filling form: {e}")
                self.reload_page_again_and_again(sb)
            # can you add an if statement to check if the page has loaded correctly?
            if "ERR" in sb.cdp.get_page_source():
                self.reload_page_again_and_again(sb)
            self.reload_page_again_and_again(sb)
            # Check for rate limit before scraping data
            self.check_for_rate_limit(sb)
            # Scrape the data
            time.sleep(5)
            self.scrape_tickets_with_regex(sb)
            self.save_results()

            print("✅ Scraping workflow completed successfully!")

def run_dmv_scraping_session(client_id, ticket_id, proxy_string, used_proxies=None):
    """Run a single DMV scraping session with the given proxy"""
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
    ) as sb:
        scraper = NYCDMVWebSummonsScraper(client_id=client_id, ticket_id=ticket_id)
        try:
            scraper.run_scraping_workflow()
            return True, used_proxies, None  # Success
        except RateLimitExceededException as e:
            print(f"🚫 RATE LIMIT detected: {e.message}")
            # Save any data collected before rate limit
            if scraper.scraped_data:
                emergency = f"rate_limit_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                scraper.save_results(emergency)
                print(f"💾 Saved data before rate limit restart: {emergency}")
            return False, used_proxies, (client_id, ticket_id)  # Rate limit detected, need restart
        except KeyboardInterrupt:
            print("Interrupted by user")
            if scraper.scraped_data:
                emergency = f"emergency_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                scraper.save_results(emergency)
            return True, used_proxies, None  # User interrupted, don't restart
        except Exception as e:
            print(f"Unexpected error: {e}")
            if scraper.scraped_data:
                emergency = f"error_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                scraper.save_results(emergency)
            return True, used_proxies, None  # Other error, don't restart

def process_single_record_with_retry(client_id, ticket_id):
    """Process a single record with automatic proxy retry on rate limit"""
    used_proxies = set()
    max_proxy_attempts = 5  # Maximum number of different proxies to try
    current_attempt = 0

    while current_attempt < max_proxy_attempts:
        current_attempt += 1
        print(f"\n🚀 DMV Session #{current_attempt} for Client ID={client_id}, Ticket ID={ticket_id}")

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

        # Run scraping session
        success, used_proxies, failed_record = run_dmv_scraping_session(client_id, ticket_id, proxy_string, used_proxies)

        if success:
            print(f"✅ DMV scraping completed successfully for Client ID={client_id}, Ticket ID={ticket_id}")
            break
        else:
            print(f"🚫 Rate limit detected for Client ID={client_id}, Ticket ID={ticket_id}")
            print(f"📊 Used proxies so far: {len(used_proxies)}")

            if current_attempt < max_proxy_attempts:
                wait_time = random.uniform(10, 30)  # Wait 10-30 seconds between restarts
                print(f"⏳ Waiting {wait_time:.1f} seconds before restarting with new proxy...")
                time.sleep(wait_time)
            else:
                print(f"❌ Maximum proxy attempts reached for Client ID={client_id}, Ticket ID={ticket_id}")
                break

if __name__ == "__main__":
    print("=== NYC DMV Web Summons Scraper ===")
    print("🔄 Enhanced with Rate Limit Detection and Proxy Rotation")

    # Read all rows from CSV (skip header)
    with open('l_and_v_list.csv', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    if len(lines) <= 1:
        print("No data found in l_and_v_list.csv")
    else:
        for row in lines[1:]:
            ticket_id, client_id = row.strip().split(',')
            print(f"\n🔄 Processing Client ID={client_id}, Ticket ID={ticket_id}")

            # Process with automatic proxy retry on rate limit
            process_single_record_with_retry(client_id, ticket_id)
