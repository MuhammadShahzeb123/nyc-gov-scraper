# NYC Parking Ticket Scraper Configuration

# Website settings
SITE_URL = "https://a836-citypay.nyc.gov/citypay/Parking?stage=procurement"
VIOLATION_INPUT_XPATH = '//*[@id="violation-number"]'
SEARCH_BUTTON_XPATH = '//*[@id="by-violation-form"]/div[3]/button'
TICKET_ROW_XPATH = '//tr[starts-with(@id, "ticket-")]'

# Timing settings (in seconds)
PAGE_LOAD_TIMEOUT = 30
SEARCH_DELAY = 1
RESULT_WAIT_TIME = 2

# File settings
VIOLATION_NUMBERS_FILE = "v_num.txt"
OUTPUT_JSON_FILE = "nyc_parking_tickets.json"
BACKUP_INTERVAL = 10  # Save backup every N records

# Browser settings
HEADLESS_MODE = False  # Set to True to run browser in background
