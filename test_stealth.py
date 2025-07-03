#!/usr/bin/env python3
"""
Test script for the stealth NYC parking ticket scraper
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    try:
        print("Testing imports...")

        import undetected_chromedriver as uc
        print("✓ undetected_chromedriver imported successfully")

        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.action_chains import ActionChains
        from selenium.webdriver.common.keys import Keys
        print("✓ Selenium modules imported successfully")

        import stealth_config
        print("✓ Stealth configuration imported successfully")

        print("✅ All imports successful!")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_config():
    """Test if configuration is properly loaded"""
    try:
        print("\nTesting configuration...")

        from stealth_config import USER_AGENTS, DELAYS, MOUSE_MOVEMENTS

        print(f"✓ Found {len(USER_AGENTS)} user agents")
        print(f"✓ Delay settings: {DELAYS['between_requests_min']}-{DELAYS['between_requests_max']}s")
        print(f"✓ Mouse movements: {'enabled' if MOUSE_MOVEMENTS['enabled'] else 'disabled'}")

        print("✅ Configuration loaded successfully!")
        return True

    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_violation_file():
    """Test if violation numbers file exists"""
    try:
        print("\nTesting violation numbers file...")

        if os.path.exists('v_num.txt'):
            with open('v_num.txt', 'r') as f:
                lines = [line.strip() for line in f if line.strip()]
            print(f"✓ Found {len(lines)} violation numbers in v_num.txt")
            if len(lines) > 0:
                print(f"✓ First violation number: {lines[0]}")
            return True
        else:
            print("⚠️ v_num.txt not found - you'll need to create this file with violation numbers")
            return False

    except Exception as e:
        print(f"❌ File error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 NYC Parking Ticket Scraper - Stealth Version Test")
    print("=" * 60)

    tests_passed = 0
    total_tests = 3

    if test_imports():
        tests_passed += 1

    if test_config():
        tests_passed += 1

    if test_violation_file():
        tests_passed += 1

    print("\n" + "=" * 60)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")

    if tests_passed == total_tests:
        print("🎉 All tests passed! Your scraper is ready to use.")
        print("\n💡 To run the scraper:")
        print("   python main.py")
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
        print("\n💡 Common fixes:")
        print("   - Install requirements: pip install -r requirements.txt")
        print("   - Create v_num.txt with violation numbers (one per line)")

    print("\n🛡️ Stealth Features Enabled:")
    print("   • Browser profile persistence (no incognito)")
    print("   • Human-like mouse movements")
    print("   • Realistic typing patterns")
    print("   • Browser history simulation")
    print("   • Random delays and behavior")
    print("   • Advanced JavaScript stealth")

if __name__ == "__main__":
    main()
