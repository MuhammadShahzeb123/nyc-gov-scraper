import html
from seleniumbase import SB
import re
import os
import json
import random
import time

class PleadAndPayScraperSB:
    def __init__(self, client_id=None, ticket_id=None, email=None):
        """Initialize the scraper with data storage"""
        self.scraped_data = []
        self.client_id = client_id
        self.ticket_id = ticket_id
        self.email = email
        self.session_id = f"session_{int(time.time())}"
        self.results_dir = "results"

        # Ensure results directory exists
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)

    def generate_random_email(self):
        """Generate a random email address"""
        japanese_names = ["tonie", "satoshi", "yuki", "haruto", "sakura", "akira", "emi", "kento", "miku"]
        sites = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]
        r = random.randint(100, 1000)

        return f"{random.choice(japanese_names)}{r}@{random.choice(sites)}"


    def save_results_to_json(self, filename=None):
        """Save scraped data to JSON file"""
        if not filename:
            filename = f"plead_pay_tickets_{self.session_id}.json"

        if self.scraped_data:
            filepath = os.path.join(self.results_dir, filename)
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(self.scraped_data, f, indent=2, ensure_ascii=False)
                print(f"✅ Results saved to {filepath}")
            except Exception as e:
                print(f"❌ Error saving results: {e}")
        else:
            print("📝 No data to save.")

    def run_plead_and_pay_workflow(self):
        """Execute the complete plead and pay workflow using SeleniumBase"""

        print("🚀 Starting Plead and Pay Automation...")
        print(f"📧 Email: {self.email}")
        print(f"🎫 Ticket ID: {self.ticket_id}")
        print(f"🆔 Client ID: {self.client_id}")

        # Use SeleniumBase with clean configuration
        with SB(
            uc=True,
            headless=False,
            # Add extensions directory if it exists
            #extension_dir="extensions" if os.path.exists("extensions") else None
        ) as sb:
            self._run_automation_steps(sb)

    def _run_automation_steps(self, sb):
        """Execute the automation steps using CDP Mode for stealth"""
        try:
            print("🌐 Chrome started successfully!")

            # Step 1: Open the plead and pay page using CDP Mode
            print("📋 Opening DMV Plead and Pay page with CDP Mode...")
            sb.activate_cdp_mode("https://transact2.dmv.ny.gov/pleadnpay/")
            sb.cdp.sleep(2)
            print(f"🔗 Current URL: {sb.cdp.get_current_url()}")

            # Step 2: Initial Page - Click radio button and submit using CDP
            print("🖱️ Initial Page: Clicking radio button and submit (CDP Mode)...")
            sb.cdp.click('//*[@id="DMVForm"]/div[1]/div/fieldset/div/div[1]/label', timeout=15)
            sb.cdp.sleep(0.5)
            sb.cdp.click('//*[@id="btn-dmv-submit-div"]/input')
            sb.cdp.sleep(2)
            print(f"🔗 After initial submit: {sb.cdp.get_current_url()}")

            # Step 3: Second Page - Fill out the form using CDP
            print("📝 Second Page: Filling out form (CDP Mode)...")

            # Click first radio button
            sb.cdp.click('//*[@id="DMVForm"]/div[1]/div/fieldset/div/div[1]/label')
            sb.cdp.sleep(0.5)
            sb.cdp.scroll_into_view('//*[@id="TypeOfSearchTicket"]')
            sb.cdp.click('//*[@id="TypeOfSearchTicket"]')
            sb.cdp.click('//*[@id="DMVForm"]/div[6]/div/fieldset[1]/div/div[1]/label')
            sb.cdp.sleep(0.5)

            # Fill in the form fields using CDP
            print(f"   • Client ID: {self.client_id}")
            sb.cdp.type('//*[@id="sClientID"]', self.client_id)
            sb.cdp.sleep(1)

            print(f"   • Ticket ID: {self.ticket_id}")
            sb.cdp.sleep(2)
            sb.cdp.type('//*[@id="ssearchTxt"]', self.ticket_id)
            sb.cdp.sleep(0.5)

            print(f"   • Email: {self.email}")
            sb.cdp.type('//*[@id="sEmailAddress"]', self.email)
            sb.cdp.sleep(1)

            sb.cdp.type('//*[@id="sEmailAddress2"]', self.email)
            sb.cdp.sleep(1)

            # Submit the form using CDP
            print("🖱️ Submitting form (CDP Mode)...")
            sb.cdp.click('//*[@id="submitBtn"]')
            sb.cdp.sleep(3)

            # Step 4: Continue Page - Click continue using CDP
            print("🖱️ Continue Page: Clicking continue button (CDP Mode)...")
            try:
                sb.cdp.click('//*[@id="Continue"]')
            except Exception as e:
                pass
            try:
                sb.cdp.click("button", text="Continue")
            except Exception as e:
                pass
            try:
                sb.cdp.gui_press_key(["Enter"])
            except Exception as e:
                pass
            sb.cdp.sleep(3)
            print(f"🔗 After continue click: {sb.cdp.get_current_url()}")

            # Step 5: Wait for ticket information page to load
            if not self.wait_for_ticket_information_page(sb):
                print("⚠️  Still not on the correct page, but continuing with extraction...")

            # NEW: Explicitly wait for ticket information to appear
            print("⏳ Waiting for ticket information to load...")
            self.wait_for_ticket_container(sb)

            # Step 6: Get page source and extract ticket info using Python regex
            print("🎫 Extracting ticket information from page source...")
            self.extract_ticket_info_from_source(sb)

            # Step 7: Save results
            self.save_results_to_json()

            print("✅ Plead and Pay workflow completed successfully!")
        except Exception as e:
            print(f"❌ An error occurred: {e}")
            # Still try to extract whatever information we can
            try:
                print("🔄 Attempting to extract data despite errors...")
                self.extract_ticket_info_from_source(sb)
                self.save_results_to_json()
            except Exception as extract_error:
                print(f"❌ Error during extraction: {extract_error}")

        finally:
            print("🔚 Keeping browser open for 10 seconds...")
            sb.cdp.sleep(10)

    def is_ticket_information_page(self, sb):
        """Check if the current page is the ticket information page"""
        target_url = "https://transact2.dmv.ny.gov/pleadnpay/Pleainformation"

        try:
            current_url = sb.cdp.get_current_url()
            print(f"🔍 Current URL (CDP): {current_url}")
            return current_url == target_url

        except Exception as e:
            print(f"⚠️  Error checking URL: {e}")
            return False

    def wait_for_ticket_information_page(self, sb, timeout=10):
        """Wait for the ticket information page to load"""
        print(f"⏳ Waiting for ticket information page to load (timeout: {timeout}s)...")

        target_url = "https://transact2.dmv.ny.gov/pleadnpay/Pleainformation"

        for i in range(timeout):
            try:
                current_url = sb.cdp.get_current_url()
                print(f"   Attempt {i+1}: {current_url}")

                if current_url == target_url:
                    print("✅ Successfully reached ticket information page!")
                    return True

                sb.cdp.sleep(1)

            except Exception as e:
                print(f"   Error checking URL: {e}")
                sb.cdp.sleep(1)

        print(f"❌ Failed to reach ticket information page within {timeout} seconds")
        return False

    def wait_for_ticket_container(self, sb, timeout=15):
        """Explicitly wait for ticket containers to appear on the page"""
        print("⏳ Waiting for ticket containers to load...")
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                # Try to find at least one ticket container
                container_count = sb.cdp.execute_script(
                    'return document.querySelectorAll(".ml-0.ml-md-4.mb-4").length'
                )

                if container_count > 0:
                    print(f"✅ Found {container_count} ticket containers")
                    return True

                # Also try the list-unstyled elements as a fallback
                list_count = sb.cdp.execute_script(
                    'return document.querySelectorAll("ul.list-unstyled").length'
                )

                if list_count > 0:
                    print(f"✅ Found {list_count} ticket lists")
                    return True

                print("   Still waiting for ticket containers...")
                sb.cdp.sleep(1)

            except Exception as e:
                print(f"⚠️  Error while waiting: {e}")
                sb.cdp.sleep(1)

        print("❌ Timed out waiting for ticket containers")
        return False

    def extract_ticket_info_from_source(self, sb):
            """Extract ticket information from page source using regex"""
            print("🔍 Getting page source...")
            try:
                page_source = sb.cdp.get_page_source()
                print(f"✅ Page source obtained ({len(page_source)} characters)")
            except Exception as e:
                print(f"❌ Failed to get page source: {e}")
                return

            debug_file = os.path.join(self.results_dir, f'debug_page_{self.session_id}.html')
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(page_source)
            print(f"🐛 Debug HTML saved to {debug_file}")

            # MODIFIED: This is the main change. We now look for each <ul>...<fieldset> block directly.
            # This correctly identifies each ticket as a self-contained unit.
            ticket_blocks = re.findall(
                r'(<ul class="list-unstyled">.*?</ul>.*?<fieldset>.*?</fieldset>)',
                page_source,
                re.DOTALL
            )

            print(f"🔍 Found {len(ticket_blocks)} ticket blocks")

            tickets = []

            for block in ticket_blocks:
                ticket = {}

                # --- Extract Details from UL ---
                ul_content_match = re.search(r'<ul class="list-unstyled">(.*?)</ul>', block, re.DOTALL)
                if not ul_content_match:
                    continue
                ul_content = ul_content_match.group(1)

                # Helper function to extract key-value pairs more reliably
                def get_value(key, content):
                    # MODIFIED: More robust regex to handle complex values and clean them up
                    pattern = rf'<strong>{key}:</strong>(.*?)(?:</li>|</ul>)'
                    match = re.search(pattern, content, re.DOTALL)
                    if match:
                        # Clean the value by removing all HTML tags and extra whitespace
                        value = re.sub(r'<.*?>', '', match.group(1)).strip()
                        return ' '.join(value.split()) # Normalize whitespace
                    return 'N/A'

                ticket['ticketNumber'] = get_value('Traffic Ticket Number', ul_content).split()[0]
                ticket['violationDescription'] = get_value('Violation Description', ul_content)
                ticket['violationDate'] = get_value('Violation Date', ul_content)
                ticket['hearingDateTime'] = get_value('Scheduled Hearing Date/Time', ul_content)
                ticket['hearingLocation'] = get_value('TVB Hearing Location', ul_content)
                points = get_value('Driver Violation Points', ul_content)
                ticket['points'] = points if points else '0' # Default to '0' if empty

                # --- Extract Plea Options from Fieldset ---
                fieldset_match = re.search(r'<fieldset>(.*?)</fieldset>', block, re.DOTALL)
                if fieldset_match:
                    fieldset_content = fieldset_match.group(1)
                    plea_options = []

                    # Find all radio inputs
                    input_pattern = r'<input[^>]*name="([^"]*)"[^>]*id="([^"]*)"[^>]*value="([^"]*)"[^>]*>'
                    input_matches = re.findall(input_pattern, fieldset_content)

                    for name, input_id, value in input_matches:
                        label_pattern = rf'<label[^>]*for="{input_id}"[^>]*>(.*?)</label>'
                        label_match = re.search(label_pattern, fieldset_content, re.DOTALL)
                        if label_match:
                            # Clean label text
                            label_text = re.sub(r'<.*?>', '', label_match.group(1)).strip()
                            plea_options.append({
                                'id': input_id,
                                'name': name,
                                'value': value,
                                'label': label_text
                            })
                    ticket['pleaOptions'] = plea_options

                # Only add valid tickets
                if 'ticketNumber' in ticket and ticket['ticketNumber'] != 'N/A':
                    tickets.append(ticket)
                    print(f"✅ Extracted ticket: {ticket['ticketNumber']}")
                else:
                    print("⚠️ Skipping block - no ticket number found")

            ticket_info = {
                "session_id": self.session_id,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "Success" if tickets else "No Tickets Found",
                "tickets": tickets
            }

            self.scraped_data.append(ticket_info)
            self._display_ticket_info(tickets)

            return ticket_info

    def _display_ticket_info(self, tickets):

        """Display extracted ticket information"""
        if not tickets:
            print("❌ No tickets extracted")
            return

        print("\n" + "="*60)
        print("📊 TICKET EXTRACTION RESULTS")
        print("="*60)

        for i, ticket in enumerate(tickets, 1):
            print(f"\n🎫 TICKET #{i}: {ticket.get('ticketNumber', 'N/A')}")
        if not tickets:
            print("❌ No tickets extracted")
            return

        print("\n" + "="*60)
        print("📊 TICKET EXTRACTION RESULTS")
        print("="*60)

        for i, ticket in enumerate(tickets, 1):
            print(f"\n🎫 TICKET #{i}: {ticket.get('ticketNumber', 'N/A')}")
            print(f"   • Violation: {ticket.get('violationDescription', 'N/A')}")
            print(f"   • Date: {ticket.get('violationDate', 'N/A')}")
            print(f"   • Hearing: {ticket.get('hearingDateTime', 'N/A')}")
            print(f"   • Location: {ticket.get('hearingLocation', 'N/A')}")
            print(f"   • Points: {ticket.get('points', 'N/A')}")

            if 'pleaOptions' in ticket:
                print(f"   ⚖️  Plea Options:")
                for j, option in enumerate(ticket['pleaOptions'], 1):
                    print(f"      {j}. {option['label']} (value: {option['value']})")

        print("="*60 + "\n")


if __name__ == "__main__":
    # Read all rows from CSV (skip header)
    with open('l_and_v_list.csv', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    if len(lines) <= 1:
        print("No data found in l_and_v_list.csv")
    else:
        for row in lines[1:]:
            client_id, ticket_id = row.strip().split(',')
            print(f"\n🔄 Processing Client ID={client_id}, Ticket ID={ticket_id}")

            # Create scraper instance
            scraper = PleadAndPayScraperSB(client_id=client_id, ticket_id=ticket_id)

            # Generate random email if not provided
            if not scraper.email:
                scraper.email = scraper.generate_random_email()

            # Run the workflow for this row
            scraper.run_plead_and_pay_workflow()