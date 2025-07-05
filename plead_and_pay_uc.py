import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import re
import json
import os

class PleadAndPayBot:
    def __init__(self, client_id, ticket_id, email):
        self.client_id = client_id
        self.ticket_id = ticket_id
        self.email = email
        self.scraped_data = []
        self.session_id = f"session_{int(time.time())}"

        # Ensure results directory exists
        if not os.path.exists('results'):
            os.makedirs('results')

        # Create Chrome options for stealth
        options = uc.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-notifications")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--start-maximized")

        # Optional: Set a custom user agent
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')

        # Launch undetected Chrome
        self.driver = uc.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 20)

    def get_page_source(self):
        return self.driver.page_source
    def reload_page(self):
        self.driver.refresh()

    def reload_page_again_and_again(self):
        if "ERR" in self.get_page_source():
            self.reload_page()
            time.sleep(2)
        if "ERR" in self.get_page_source():
            self.reload_page_again_and_again()
            time.sleep(2)
        time.sleep(2)  # Wait for the page to reload
        if self.driver.current_url == "https://transact2.dmv.ny.gov/pleadnpay/":
            self.run()


    def extract_ticket_info_with_regex(self, ticket_number):
        """Extract ticket information using regex pattern"""
        print("Extracting ticket information using regex...")
        page_source = self.get_page_source()

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

        self.scraped_data.append(ticket_info)
        return ticket_info

    def save_results_to_json(self):
        """Save scraped data to JSON file"""
        if self.scraped_data:
            filename = f"results/plead_pay_tickets_{self.session_id}.json"
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.scraped_data, f, indent=2, ensure_ascii=False)
                print(f"✅ Results saved to {filename}")
            except Exception as e:
                print(f"❌ Error saving results: {e}")
        else:
            print("No data to save.")

    def run(self):
        try:
            self.driver.get("https://transact2.dmv.ny.gov/pleadnpay/")

            # Initial Page
            self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="DMVForm"]/div[1]/div/fieldset/div/div[1]/label'))).click()
            self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="btn-dmv-submit-div"]/input'))).click()
            self.reload_page_again_and_again()

            # Second Page
            self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="DMVForm"]/div[1]/div/fieldset/div/div[1]/label'))).click()
            time.sleep(1)  # Wait for the checkbox to be clickable
            try:
                self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="DMVForm"]/div[6]/div/fieldset[1]/div/div[1]/label'))).click()
            except Exception as e:
                pass
            self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="TypeOfEnterInfoY"]'))).click()
            self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="sClientID"]'))).send_keys(self.client_id)
            self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="ssearchTxt"]'))).send_keys(self.ticket_id)
            self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="sEmailAddress"]'))).send_keys(self.email)
            self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="sEmailAddress2"]'))).send_keys(self.email)
            time.sleep(3)  # Wait for the input fields to be filled
            self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="submitBtn"]'))).click()
            time.sleep(2)  # Wait for the form to submit
            self.reload_page_again_and_again()


            # Continue Page
            self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="Continue"]'))).click()
            time.sleep(2)  # Wait for the page to load
            self.reload_page_again_and_again()            # Extract ticket information using regex
            self.extract_ticket_info_with_regex(self.ticket_id)

            # Save results to JSON
            self.save_results_to_json()

        except Exception as e:
            print(f"❌ An error occurred: {e}")
            # Still try to extract whatever information we can
            try:
                self.extract_ticket_info_with_regex(self.ticket_id)
                self.save_results_to_json()
            except Exception as extract_error:
                print(f"❌ Error during extraction: {extract_error}")
        finally:
            time.sleep(10)  # Keep browser open for a while
            self.driver.quit()

if __name__ == "__main__":
    # Replace with your actual data
    CLIENT_ID = "597872595"
    TICKET_ID = "B255005941"  # You need to provide a ticket ID
    r = random.randint(100, 1000)  # Random number for testing
    japanese_names = ["tonie", "satoshi", "yuki", "haruto", "sakura"]
    sites = ["gmail.com", "yahoo.com", "hotmail.com"]
    EMAIL = f"{random.choice(japanese_names)}{r}@{random.choice(sites)}"

    print(f"🚀 Starting automation with:")
    print(f"📧 Email: {EMAIL}")
    print(f"🎫 Ticket ID: {TICKET_ID}")
    print(f"🆔 Client ID: {CLIENT_ID}")

    bot = PleadAndPayBot(CLIENT_ID, TICKET_ID, EMAIL)
    bot.run()
