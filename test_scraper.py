"""
Test script to verify the scraper works with a single violation number
"""

import sys
import os
from citypay_nyc import NYCParkingTicketScraper

def test_single_violation():
    """Test the scraper with just one violation number"""

    # Get the first violation number from the file
    try:
        with open('v_num.txt', 'r') as file:
            first_number = file.readline().strip()

        if not first_number:
            print("No violation numbers found in v_num.txt")
            return

        print(f"Testing with violation number: {first_number}")

    except FileNotFoundError:
        print("Error: v_num.txt file not found!")
        return

    scraper = None
    try:
        # Initialize scraper
        scraper = NYCParkingTicketScraper()

        # Override violation numbers with just the first one for testing
        scraper.violation_numbers = [first_number]

        # Navigate to site
        if not scraper.navigate_to_site():
            print("Failed to navigate to website")
            return

        # Search for the violation number
        if scraper.search_violation_number(first_number):
            tickets = scraper.extract_ticket_data(first_number)
            scraper.scraped_data.extend(tickets)

            # Save test results
            scraper.save_data_to_json('test_result.json')

            print(f"\n=== Test Results ===")
            print(f"Tickets found: {len(tickets)}")
            if tickets:
                print("Sample ticket data:")
                for ticket in tickets:
                    print(f"  - Ticket ID: {ticket.get('ticket_id', 'N/A')}")
                    print(f"  - Violation Number: {ticket.get('violation_number', 'N/A')}")
                    print(f"  - License Plate: {ticket.get('license_plate', 'N/A')}")
                    print(f"  - Amount Due: {ticket.get('amount_due', 'N/A')}")
                    print(f"  - Date: {ticket.get('date', 'N/A')}")
                    print("  ---")
        else:
            print("Failed to search for violation number")

    except Exception as e:
        print(f"Test failed with error: {str(e)}")

    finally:
        if scraper:
            scraper.close()

if __name__ == "__main__":
    print("=== NYC Parking Ticket Scraper - Test Mode ===")
    test_single_violation()
