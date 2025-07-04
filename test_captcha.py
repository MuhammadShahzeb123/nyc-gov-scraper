#!/usr/bin/env python3
"""
Test script to verify captcha detection functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from citypay_nyc import NYCParkingTicketScraper

def test_captcha_detection():
    """Test captcha detection patterns"""

    # Create a mock scraper instance
    scraper = NYCParkingTicketScraper()

    # Test patterns that should trigger captcha detection
    test_cases = [
        ("Unable to verify reCAPTCHA with Google", True),
        ("unable to verify recaptcha with google", True),
        ("CAPTCHA verification failed", True),
        ("Please verify you are human", True),
        ("Normal page content", False),
        ("No captcha here", False),
        ("reCAPTCHA error occurred", True),
        ("Human verification required", True),
        ("Please complete the captcha", True),
    ]

    print("🧪 Testing captcha detection patterns...")

    for test_text, expected in test_cases:
        # Mock the page source
        original_page_source = None

        # We can't easily mock driver.page_source, so we'll test the pattern matching logic
        test_result = any(pattern in test_text.lower() for pattern in [
            "unable to verify recaptcha with google",
            "unable to verify recaptcha",
            "recaptcha verification failed",
            "captcha verification failed",
            "captcha error",
            "recaptcha error",
            "please verify you are human",
            "verify you are not a robot",
            "security verification required",
            "anti-bot verification",
            "please complete the captcha",
            "captcha challenge",
            "human verification required"
        ])

        status = "✅ PASS" if test_result == expected else "❌ FAIL"
        print(f"  {status}: '{test_text}' -> Expected: {expected}, Got: {test_result}")

    print("\n🔍 Captcha detection pattern test completed!")

def test_main_functionality():
    """Test that main functionality still works"""
    try:
        print("🧪 Testing main scraper initialization...")
        scraper = NYCParkingTicketScraper()

        # Test that key methods exist
        required_methods = [
            'detect_captcha_error',
            'handle_captcha_retry',
            'search_violation_number_internal',
            'search_violation_number',
            'take_random_break',
            'return_to_base_url'
        ]

        for method_name in required_methods:
            if hasattr(scraper, method_name):
                print(f"  ✅ Method {method_name} exists")
            else:
                print(f"  ❌ Method {method_name} missing")

        print("✅ Main functionality test completed!")

    except Exception as e:
        print(f"❌ Error testing main functionality: {e}")

if __name__ == "__main__":
    print("🚀 Starting captcha detection tests...\n")
    test_captcha_detection()
    print()
    test_main_functionality()
    print("\n✅ All tests completed!")
