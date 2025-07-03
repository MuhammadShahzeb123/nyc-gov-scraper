# NYC Parking Ticket Scraper

A robust web scraping tool to extract parking ticket information from the NYC government website using Selenium and undetected-chromedriver.

## Features

- **Automated Ticket Lookup**: Processes violation numbers from `v_num.txt` file
- **Stealth Browsing**: Uses undetected-chromedriver to avoid detection
- **Data Extraction**: Extracts comprehensive ticket information including:
  - Ticket ID
  - Violation Number
  - License Plate
  - Violation Type
  - Date
  - Liability Amount
  - Paid Amount
  - Amount Due
  - Payment Amount
  - View Ticket Link

- **JSON Output**: Saves data in structured JSON format
- **Error Handling**: Robust error handling and recovery
- **Progress Tracking**: Shows progress and periodic backups
- **Test Mode**: Includes test script for single violation verification

## Requirements

- Python 3.7+
- Chrome browser installed
- Internet connection

## Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

2. Ensure Chrome browser is installed on your system.

## Usage

### Full Scraping (All Violation Numbers)

Run the main scraper to process all violation numbers:

```bash
python main.py
```

### Test Mode (Single Violation Number)

Test with just the first violation number:

```bash
python test_scraper.py
```

## Input File Format

The `v_num.txt` file should contain one violation number per line:

```
4045563933
9183673350
9183966020
...
```

## Output Format

The scraper generates JSON files with the following structure:

```json
[
  {
    "search_violation_number": "9164311661",
    "extracted_at": "2025-07-03T10:30:00.000000",
    "ticket_id": "2024572215497",
    "violation_number": "9164311661",
    "license_plate": "KZZ1916 NY PAS",
    "violation_type": "20A-No Parking (Non-COM)",
    "date": "11/05/2024",
    "liability_amount": "$99.08",
    "paid_amount": "$0.00",
    "amount_due": "$99.08",
    "payment_amount": "99.08",
    "view_ticket_link": "http://nycserv.nyc.gov/NYCServWeb/ShowImage?searchID=..."
  }
]
```

## Configuration

Modify `config.py` to adjust:
- Timeout settings
- File paths
- Backup intervals
- Browser settings

## Error Handling

The scraper includes comprehensive error handling:
- Network timeouts
- Missing elements
- Invalid violation numbers
- File I/O errors

Progress is saved periodically to prevent data loss.

## Best Practices

- Run during off-peak hours to reduce server load
- Monitor the scraping process for any issues
- Keep Chrome browser updated
- Respect the website's terms of service

## Files

- `main.py` - Main scraper script
- `test_scraper.py` - Test script for single violation
- `config.py` - Configuration settings
- `v_num.txt` - Input violation numbers
- `requirements.txt` - Python dependencies
- `nyc_parking_tickets.json` - Output data (generated)

## Legal Notice

This tool is for educational and legitimate research purposes only. Users are responsible for complying with the website's terms of service and applicable laws. Always respect rate limits and server resources.

## Troubleshooting

### Common Issues:

1. **Chrome driver issues**: Update Chrome browser and undetected-chromedriver
2. **Timeout errors**: Increase timeout values in config.py
3. **Element not found**: Website structure may have changed
4. **Network issues**: Check internet connection and website availability

### Debug Mode:

Set `HEADLESS_MODE = False` in config.py to see browser actions in real-time.

## Support

For issues or questions, review the error messages and ensure all requirements are met.
