from seleniumbase import SB
import re
import os
import json
import random
import time

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
        print("🔍 Scraping tickets using regex...")

        try:
            # Get page source
            page_source = sb.get_page_source()

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

        filepath = os.path.join(self.results_dir, filename)
        try:
            with open(filepath, 'w') as f:
                json.dump(self.scraped_data, f, indent=4)
            print(f"✅ Results saved to {filepath}")
        except Exception as e:
            print(f"Error saving results: {e}")

    def reload_page_again_and_again(self, sb):
        if "ERR" in sb.get_page_source():
            sb.reload_page()
            time.sleep(2)
        if "ERR" in sb.get_page_source():
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
            sb.open("https://process.dmv.ny.gov/WebSummons/")

            # Simple wait
            time.sleep(3)

            # Click the first submit button
            print("🖱️ Clicking first submit button...")
            sb.click('#submit')

            # Simple wait
            time.sleep(2)

            # Fill in the form details simply
            print("📝 Filling in form details...")
            print(f"   • Client ID: {self.client_id}")
            sb.type('#sClientID', self.client_id)

            time.sleep(1)

            print(f"   • Ticket Number: {self.ticket_id}")
            sb.type('#sTicketNum', self.ticket_id)

            time.sleep(1)

            # Generate and fill email addresses
            random_email = self.generate_random_gmail()
            print(f"   • Email: {random_email}")

            sb.type('#sEmailAddress', random_email)
            time.sleep(1)

            sb.type('#sEmailAddress2', random_email)
            time.sleep(2)

            # Click the final submit button
            print("🖱️ Clicking final submit button...")
            sb.click('//*[@id="submit order"]')

            # Wait for results page
            time.sleep(5)

            # can you add an if statement to check if the page has loaded correctly?
            self.reload_page_again_and_again(sb)
            # Scrape the data
            time.sleep(5)
            self.scrape_tickets_with_regex(sb)
            self.save_results()

            print("✅ Scraping workflow completed successfully!")

if __name__ == "__main__":

    scraper = NYCDMVWebSummonsScraper(client_id="597872595", ticket_id="B255005941")
    scraper.run_scraping_workflow()
