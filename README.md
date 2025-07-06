# NYC Traffic Violation Scrapers

This project contains a set of Python scripts designed to scrape information about traffic and parking violations from various NYC government websites.

## Description

The scripts automate the process of retrieving details about traffic summons, parking tickets, and processing them through the "Plead and Pay" portal. They use web scraping libraries like `seleniumbase` and `undetected-chromedriver` to navigate the websites and extract the required information.

## Features

- Scrapes NYC DMV web summons.
- Scrapes NYC parking ticket data from CityPay.
- Automates the "Plead and Pay" workflow.
- Uses `seleniumbase` and `undetected-chromedriver` for robust scraping.
- Implements stealth techniques to avoid bot detection.
- Saves scraped data to JSON files in the `results` directory.

## Scripts

### `dmb_ny_sb.py`

- **Purpose:** Scrapes web summons from the [NYC DMV Web Summons](https://process.dmv.ny.gov/WebSummons/) website.
- **Input:** Reads client IDs and ticket IDs from `l_and_v_list.csv`.
- **Output:** Saves the scraped ticket data as a JSON file in the `results` directory.

### `citypay_nyc.py`

- **Purpose:** Scrapes parking ticket information from the [NYC CityPay](https://a836-citypay.nyc.gov/citypay/Parking) portal.
- **Input:** Reads violation numbers from `v_num.txt`.
- **Output:** Saves the scraped ticket data as a JSON file in the `results` directory.
- **Note:** This script includes advanced stealth mechanisms to mimic human behavior and avoid detection.

### `plead_and_pay_sb_clean.py`

- **Purpose:** Automates the workflow on the [DMV Plead and Pay](https://transact2.dmv.ny.gov/pleadnpay/) website.
- **Input:** Reads client IDs and ticket IDs from `l_and_v_list.csv`.
- **Output:** Extracts ticket information and saves it as a JSON file in the `results` directory.

## Setup

1. **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd nyc_gov
    ```

2. **Install dependencies:**
    The required Python packages are listed in `requirements.txt`.

    ```bash
    pip install -r requirements.txt
    ```

3. **Input Files:**
    - Create a `l_and_v_list.csv` file with `ticket_id,client_id` columns for `dmb_ny_sb.py` and `plead_and_pay_sb_clean.py`.

        ```csv
        ticket_id,client_id
        1234567890,CLIENT1
        0987654321,CLIENT2
        ```

    - Create a `v_num.txt` file with a list of violation numbers (one per line) for `citypay_nyc.py`.

        ```text
        1111111111
        2222222222
        ```

## Usage

To run the scrapers, execute the Python scripts directly from your terminal:

- **DMV Web Summons Scraper:**

    ```bash
    python dmb_ny_sb.py
    ```

- **CityPay Parking Ticket Scraper:**

    ```bash
    python citypay_nyc.py
    ```

- **Plead and Pay Scraper:**

    ```bash
    python plead_and_pay_sb_clean.py
    ```

Scraped data will be saved in the `results` directory.

## Dependencies

- `seleniumbase`
- `undetected-chromedriver`
- `selenium`
