import html
from seleniumbase import SB
import re
import os
import json
import random
import time
from proxy_config import proxy_rotator  # Import proxy rotation system

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
        sites = ["gmail.com"]
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

    def _reload_again_and_again(self, sb):
        self.page = sb.cdp.get_page_source()
        if "ERR" in self.page:
            sb.cdp.refresh()
            sb.cdp.sleep(2)
        if "ERR" in self.page:
            self._reload_again_and_again(sb)



    def run_plead_and_pay_workflow(self):
        """Execute the complete plead and pay workflow using SeleniumBase"""

        print("🚀 Starting Plead and Pay Automation...")
        print(f"📧 Email: {self.email}")
        print(f"🎫 Ticket ID: {self.ticket_id}")
        print(f"🆔 Client ID: {self.client_id}")

        # Get proxy configuration for SeleniumBase with validation
        proxy_string = proxy_rotator.get_seleniumbase_proxy_with_fallback(use_random=True)
        if proxy_string:
            print(f"🌐 Using rotating proxy: {proxy_string}")
        else:
            print("🌐 Using direct connection (no proxy)")

        # Use SeleniumBase with clean configuration
        with SB(
            uc=True,
            headless=False,
            proxy=proxy_string,  # SeleniumBase authenticated proxy format (or None for direct)
            # Add extensions directory if it exists
            #extension_dir="extensions" if os.path.exists("extensions") else None
        ) as sb:
            self._run_automation_steps(sb)

    def throttle(self, sb, offline=False, latency=100, download_throughput=420 * 1024 / 8, upload_throughput=250 * 1024 / 8):
        # Convert kbps to bytes/sec
        sb.execute_cdp_cmd("Network.enable", {})
        sb.execute_cdp_cmd("Network.emulateNetworkConditions", {
            "offline": offline,
            "latency": latency,  # ms
            "downloadThroughput": download_throughput,
            "uploadThroughput": upload_throughput,
            "connectionType": "cellular3g"
        })



    def _run_automation_steps(self, sb):
        """Execute the automation steps using CDP Mode for stealth"""
        # Define base URL for restart checks
        BASE_URL = "https://transact2.dmv.ny.gov/pleadnpay/"
        max_retries = 3
        current_retry = 0
        success = False

        # Helper function to check if we're back at base URL
        def is_at_base_url():
            current_url = sb.cdp.get_current_url()
            return current_url == BASE_URL or current_url == BASE_URL.strip('/')

        while current_retry < max_retries and not success:
            try:
                print(f"\n🔄 Attempt #{current_retry + 1} of {max_retries}")
                print("🌐 Chrome started successfully!")

                # Step 1: Open initial page
                print("📋 Opening DMV Plead and Pay page with CDP Mode...")
                sb.activate_cdp_mode(BASE_URL)
                # self.throttle(sb)
                sb.cdp.sleep(10)
                self._reload_again_and_again(sb)
                print(f"🔗 Current URL: {sb.cdp.get_current_url()}")

                # Step 2: Initial Page - Click radio button and submit
                print("🖱️ Initial Page: Clicking radio button and submit (CDP Mode)...")
                sb.cdp.wait_for_element_visible('//*[@id="DMVForm"]/div[1]/div/fieldset/div/div[1]/label', timeout=None)
                sb.cdp.click('//*[@id="DMVForm"]/div[1]/div/fieldset/div/div[1]/label', timeout=15)
                sb.cdp.wait_for_element_visible('//*[@id="btn-dmv-submit-div"]/input', timeout=60000)
                sb.cdp.sleep(0.5)
                sb.cdp.click('//*[@id="btn-dmv-submit-div"]/input')
                sb.cdp.sleep(2)
                print(f"🔗 After initial submit: {sb.cdp.get_current_url()}")

                # Check if we're back at base URL
                if is_at_base_url():
                    print("⚠️ Unexpectedly returned to base URL after Step 2. Restarting...")
                    current_retry += 1
                    continue

                # Step 3: Second Page - Fill out form
                print("📝 Second Page: Filling out form (CDP Mode)...")
                self._reload_again_and_again(sb)
                sb.cdp.wait_for_element_visible('//*[@id="DMVForm"]/div[1]/div/fieldset/div/div[1]/label', timeout=None)
                sb.cdp.click('//*[@id="DMVForm"]/div[1]/div/fieldset/div/div[1]/label')
                sb.cdp.sleep(0.5)
                sb.cdp.scroll_into_view('//*[@id="TypeOfSearchTicket"]')
                sb.cdp.click('//*[@id="TypeOfSearchTicket"]')
                sb.cdp.click('//*[@id="DMVForm"]/div[6]/div/fieldset[1]/div/div[1]/label')
                sb.cdp.sleep(0.5)

                # Fill form fields
                print(f"   • Client ID: {self.client_id}")
                sb.cdp.type('//*[@id="sClientID"]', self.client_id)
                sb.cdp.sleep(1)
                print(f"   • Email: {self.email}")
                sb.cdp.type('//*[@id="sEmailAddress"]', self.email)
                sb.cdp.sleep(0.2)
                # can we add delay in typing?

                sb.cdp.type('//*[@id="sEmailAddress2"]', self.email)
                sb.cdp.sleep(0.2)

                print(f"   • Ticket ID: {self.ticket_id}")
                sb.cdp.type('//*[@id="ssearchTxt"]', self.ticket_id, timeout=60000)
                sb.cdp.sleep(0.5)


                # Submit form
                print("🖱️ Submitting form (CDP Mode)...")
                # sb.cdp.click_if_visible('//*[@id="submitBtn"]', timeout=None)
                sb.cdp.scroll_to_bottom()
                # sb.cdp.scroll_into_view('//*[@id="submitBtn"]')
                sb.cdp.wait_for_element_visible('/html/body/div[1]/div[5]/form/div[8]/input[2]', timeout=None)
                try:
                    sb.cdp.click("/html/body/div[1]/div[5]/form/div[8]/input[2]")

                except Exception:
                    try:
                        sb.cdp.press_keys('\t', timeout=None)
                    except Exception:
                        try:
                            sb.cdp.click_if_visible('/html/body/div[1]/div[5]/form/div[8]/input[2]', timeout=None)
                        except Exception as e:
                            sb.cdp.gui_click_element('/html/body/div[1]/div[5]/form/div[8]/input[2]', timeout=None)

                sb.cdp.sleep(3)
                self._reload_again_and_again(sb)

                # Check if we're back at base URL
                if is_at_base_url():
                    print("⚠️ Unexpectedly returned to base URL after form submit. Restarting...")
                    current_retry += 1
                    continue

                # Step 4: Continue Page
                sb.cdp.wait_for_element_visible('/html/body/div[1]/div[5]/form/div[3]/input[2]', timeout=None)
                print("🖱️ Continue Page: Clicking continue button (CDP Mode)...")
                sb.cdp.sleep(2)
                sb.cdp.scroll_into_view('/html/body/div[1]/div[5]/form/div[3]/input[2]')
                sb.cdp.click("/html/body/div[1]/div[5]/form/div[3]/input[2]")
                sb.cdp.sleep(3)
                print(f"🔗 After continue click: {sb.cdp.get_current_url()}")

                # Check if we're back at base URL
                if is_at_base_url():
                    print("⚠️ Unexpectedly returned to base URL after continue click. Restarting...")
                    current_retry += 1
                    continue

                # Step 5: Wait for ticket information
                if not self.wait_for_ticket_information_page(sb):
                    print("⚠️  Still not on correct page, but continuing...")

                # Step 6: Extract ticket info
                print("⏳ Waiting for ticket information to load...")
                self.wait_for_ticket_container(sb)
                print("🎫 Extracting ticket information from page source...")
                self.extract_ticket_info_from_source(sb)

                # Step 7: Save results
                self.save_results_to_json()
                print("✅ Plead and Pay workflow completed successfully!")
                success = True

            except Exception as e:
                print(f"❌ An error occurred: {e}")
                # Check if we're back at base URL during exception
                if is_at_base_url():
                    print("⚠️ Error occurred and returned to base URL. Restarting...")
                    current_retry += 1
                else:
                    # Attempt extraction even with errors
                    try:
                        print("🔄 Attempting to extract data despite errors...")
                        self.extract_ticket_info_from_source(sb)
                        self.save_results_to_json()
                        success = True  # Consider this attempt successful
                    except Exception as extract_error:
                        print(f"❌ Error during extraction: {extract_error}")
                        current_retry += 1




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
            ticket_id, client_id = row.strip().split(',')
            print(f"\n🔄 Processing Client ID={client_id}, Ticket ID={ticket_id}")

            # Create scraper instance
            scraper = PleadAndPayScraperSB(client_id=client_id, ticket_id=ticket_id)

            # Generate random email if not provided
            if not scraper.email:
                scraper.email = scraper.generate_random_email()

            # Run the workflow for this row
            scraper.run_plead_and_pay_workflow()