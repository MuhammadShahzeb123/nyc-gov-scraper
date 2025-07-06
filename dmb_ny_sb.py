from seleniumbase import SB
import re
import os
import json
import random
import time
import datetime

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
        if "ERR" in sb.cdp.get_page_source():
            self.reload_page_again_and_again(sb)

    def run_scraping_workflow(self):
        """Execute the complete scraping workflow - simple and clean"""
        # Simple Chrome setup - avoid conflicts with existing Chrome instances
        with SB(
            uc=True,
            headless=False,
            # Remove extension_dir and user_data_dir to avoid conflicts
            # extension_dir="extensions",
            # user_data_dir="chrome_profile"
        ) as sb:

            print("🚀 Starting NYC DMV Web Summons Scraper...")

            # Open the main page
            print("📋 Opening NYC DMV Web Summons page...")
            sb.activate_cdp_mode("https://process.dmv.ny.gov/WebSummons/")
            self.reload_page_again_and_again(sb)
            # Simple wait
            time.sleep(3)

            # Click the first submit buttonc
            print("🖱️ Clicking first submit button...")
            sb.cdp.wait_for_element_visible('//*[@id="submit"]', timeout=60000)
            sb.cdp.click('//*[@id="submit"]')
            self.reload_page_again_and_again(sb)
            # Simple wait
            time.sleep(2)

            # Fill in the form details simply
            print("📝 Filling in form details...")
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

            # can you add an if statement to check if the page has loaded correctly?
            self.reload_page_again_and_again(sb)
            # Scrape the data
            time.sleep(5)
            self.scrape_tickets_with_regex(sb)
            self.save_results()

            print("✅ Scraping workflow completed successfully!")

if __name__ == "__main__":
    # Read all rows from CSV (skip header)
    with open('l_and_v_list.csv', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    if len(lines) <= 1:
        print("No data found in l_and_v_list.csv")
    else:
        for row in lines[1:]:
            ticket_id, client_id = row.strip().split(',')
            print(f"\n🔄 Processing Client ID={client_id}, Ticket ID={ticket_id}")

            scraper = NYCDMVWebSummonsScraper(client_id=client_id, ticket_id=ticket_id)
            scraper.run_scraping_workflow()
