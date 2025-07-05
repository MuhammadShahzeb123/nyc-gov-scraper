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

    def reload_page_again_and_again(self, sb):
        """Reload page if errors are found"""
        if "ERR" in sb.get_page_source():
            sb.reload_page()
        if "ERR" in sb.get_page_source():
            self.reload_page_again_and_again(sb)


    def extract_ticket_info_with_regex(self, sb, ticket_number):
        """Extract ticket information using regex pattern"""
        print("🔍 Extracting ticket information using regex...")
        page_source = sb.get_page_source()

        # Regex pattern to match ticket information in <ul> tags
        pattern = r'<ul class="list-unstyled">(.*?)</ul>'
        ul_matches = re.findall(pattern, page_source, re.IGNORECASE | re.DOTALL)

        ticket_info = {
            "ticket_number": ticket_number,
            "session_id": self.session_id,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "Not Found",
            "details": {}
        }

        if ul_matches:
            # Process all matches to get all ticket information
            all_details = {}
            for ul_content in ul_matches:
                # Extract list items
                li_pattern = r'<li>(.*?)</li>'
                li_matches = re.findall(li_pattern, ul_content, re.IGNORECASE | re.DOTALL)

                for item in li_matches:
                    # Clean up the item content and remove HTML tags
                    item_text = re.sub(r'<.*?>', '', item).strip()
                    # Remove extra whitespace and newlines
                    item_text = re.sub(r'\s+', ' ', item_text)

                    if ':' in item_text:
                        key, value = item_text.split(':', 1)
                        all_details[key.strip()] = value.strip()

            if all_details:
                ticket_info["status"] = "Found"
                ticket_info["details"] = all_details
                print(f"✓ Ticket info extracted for {ticket_number}")
                print(f"📋 Details: {json.dumps(all_details, indent=2)}")
            else:
                print(f"✗ No ticket information found for {ticket_number}")
        else:
            print(f"✗ No <ul> elements found for {ticket_number}")
            # Save debug info
            debug_file = os.path.join(self.results_dir, f'debug_page_source_{self.session_id}.html')
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(page_source)
            print(f"🐛 Debug: Page source saved to {debug_file}")

        self.scraped_data.append(ticket_info)
        return ticket_info

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
            extension_dir="extensions" if os.path.exists("extensions") else None
        ) as sb:
            self._run_automation_steps(sb)

    def _run_automation_steps(self, sb):
        """Execute the automation steps with JavaScript for speed"""
        try:
            print("🌐 Chrome started successfully!")

            # Step 1: Open the plead and pay page
            print("📋 Opening DMV Plead and Pay page...")
            sb.open("https://transact2.dmv.ny.gov/pleadnpay/")
            print(f"🔗 Current URL: {sb.get_current_url()}")

            # Step 2: Initial Page - Click radio button and submit using JavaScript
            print("🖱️ Initial Page: Clicking radio button and submit (JavaScript)...")
            # Use JavaScript to click instantly
            sb.execute_script('document.querySelector(\'#DMVForm div:nth-child(1) div fieldset div div:nth-child(1) label\').click();')
            sb.execute_script('document.querySelector(\'#btn-dmv-submit-div input\').click();')
            print(f"🔗 After initial submit: {sb.get_current_url()}")
            self.reload_page_again_and_again(sb)

            # Step 3: Second Page - Fill out the form with JavaScript for speed
            print("📝 Second Page: Filling out form (JavaScript)...")

            # JavaScript to click radio buttons and fill fields instantly
            js_script = f"""
            try {{
                // Click first radio button
                document.querySelector('#DMVForm div:nth-child(1) div fieldset div div:nth-child(1) label').click();
                
                // Try optional radio buttons
                try {{
                    document.querySelector('#DMVForm div:nth-child(6) div fieldset:nth-child(1) div div:nth-child(1) label').click();
                }} catch(e) {{ console.log('Optional click 1 failed'); }}
                
                try {{
                    document.querySelector('#TypeOfEnterInfoY').click();
                }} catch(e) {{ console.log('Optional click 2 failed'); }}
                
                // Fill form fields instantly
                document.querySelector('#sClientID').value = '{self.client_id}';
                document.querySelector('#ssearchTxt').value = '{self.ticket_id}';
                document.querySelector('#sEmailAddress').value = '{self.email}';
                document.querySelector('#sEmailAddress2').value = '{self.email}';
                
                // Trigger change events
                document.querySelector('#sClientID').dispatchEvent(new Event('change'));
                document.querySelector('#ssearchTxt').dispatchEvent(new Event('change'));
                document.querySelector('#sEmailAddress').dispatchEvent(new Event('change'));
                document.querySelector('#sEmailAddress2').dispatchEvent(new Event('change'));
                
                console.log('Form filled successfully');
            }} catch(e) {{
                console.log('Error in form filling:', e);
            }}
            """
            
            print(f"⚡ Executing super-fast JavaScript form filling...")
            sb.execute_script(js_script)
            
            # Submit the form with JavaScript
            print("🖱️ Submitting form (JavaScript)...")
            sb.execute_script('document.querySelector(\'#submitBtn\').click();')
            time.sleep(3)
            self.reload_page_again_and_again(sb)

            # Check if we need to retry
            self.current_url = sb.get_current_url()
            if "EnterNyInfo" not in self.current_url or "VerifyInfo" not in self.current_url:
                print("🔄 Retrying workflow...")
                self.run_plead_and_pay_workflow()
                return
            # Step 4: Continue Page - Click continue
            print("🖱️ Continue Page: Clicking continue button...")
            sb.click('//*[@id="Continue"]')
            time.sleep(3)
            self.reload_page_again_and_again(sb)

            # Check if we need to retry again
            if "EnterNyInfo" not in self.current_url or "VerifyInfo" not in self.current_url:
                print("🔄 Retrying workflow...")
                self.run_plead_and_pay_workflow()
                return

            # Step 5: Extract ticket information
            print("🔍 Extracting ticket information...")
            self.extract_ticket_info_with_regex(sb, self.ticket_id)

            # Step 6: Save results
            self.save_results_to_json()

            print("✅ Plead and Pay workflow completed successfully!")

        except Exception as e:
            print(f"❌ An error occurred: {e}")
            # Still try to extract whatever information we can
            try:
                print("🔄 Attempting to extract data despite errors...")
                self.extract_ticket_info_with_regex(sb, self.ticket_id)
                self.save_results_to_json()
            except Exception as extract_error:
                print(f"❌ Error during extraction: {extract_error}")

        finally:
            print("🔚 Keeping browser open for 10 seconds...")
            time.sleep(10)

if __name__ == "__main__":
    # Configuration
    CLIENT_ID = "597872595"
    TICKET_ID = "B255005941"

    # Create scraper instance
    scraper = PleadAndPayScraperSB(client_id=CLIENT_ID, ticket_id=TICKET_ID)

    # Generate random email if not provided
    if not scraper.email:
        scraper.email = scraper.generate_random_email()

    # Run the workflow
    scraper.run_plead_and_pay_workflow()
