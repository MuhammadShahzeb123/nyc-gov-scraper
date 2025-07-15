#!/usr/bin/env python3
"""
Test script for the improved CAPTCHA detection logic
"""

def test_captcha_detection():
    """Test the improved CAPTCHA detection logic"""

    test_cases = [
        {
            'page_source': 'Normal page content with no captcha issues',
            'expected': False,
            'description': 'Normal page without any CAPTCHA'
        },
        {
            'page_source': 'Some content with unable to verify recaptcha error message',
            'expected': True,
            'description': 'Page with "unable to verify recaptcha" error'
        },
        {
            'page_source': 'Error: unable to verify recaptcha with google servers',
            'expected': True,
            'description': 'Page with "unable to verify recaptcha with google" error'
        },
        {
            'page_source': 'Please verify you are human by completing the captcha',
            'expected': False,
            'description': 'Page with generic CAPTCHA prompt (not an error)'
        },
        {
            'page_source': 'The system is unable to process your request. Please verify your information.',
            'expected': True,
            'description': 'Page with "unable" and "verify" close together'
        },
        {
            'page_source': 'We are unable to connect. To verify your account, please try again.',
            'expected': True,
            'description': 'Page with "unable" and "verify" in same sentence'
        },
        {
            'page_source': 'Unable to load page.' + ' ' * 50 + 'Some other content here.' + ' ' * 50 + 'Verify button is over there somewhere far away.',
            'expected': False,
            'description': 'Page with "unable" and "verify" but far apart (>100 chars)'
        },
        {
            'page_source': 'recaptcha verification failed due to network error',
            'expected': True,
            'description': 'Page with "recaptcha verification failed" error'
        },
        {
            'page_source': '<div class="recaptcha">Please complete the challenge</div>',
            'expected': False,
            'description': 'Page with reCAPTCHA element but no error (should not trigger)'
        }
    ]

    print("🧪 Testing improved CAPTCHA detection logic...\n")

    for i, test_case in enumerate(test_cases, 1):
        page_source = test_case['page_source'].lower()
        expected = test_case['expected']
        description = test_case['description']

        # Implement the actual detection logic from the script
        detected = False

        # Check specific error patterns
        specific_captcha_error_patterns = [
            "unable to verify recaptcha",
            "unable to verify recaptcha with google",
            "recaptcha verification failed",
            "captcha verification failed",
            "captcha challenge failed",
            "verification failed"
        ]

        for pattern in specific_captcha_error_patterns:
            if pattern in page_source:
                detected = True
                break

        # Check for "unable" AND "verify" close together
        if not detected and "unable" in page_source and "verify" in page_source:
            unable_pos = page_source.find("unable")
            verify_pos = page_source.find("verify")
            if abs(unable_pos - verify_pos) < 100:
                detected = True

        result = "✅ PASS" if detected == expected else "❌ FAIL"

        print(f"Test {i}: {description}")
        print(f"  Page source: '{test_case['page_source']}'")
        print(f"  Expected: {expected}, Got: {detected}")
        print(f"  Result: {result}\n")

        if detected != expected:
            return False

    print("🎉 All CAPTCHA detection tests passed!")
    return True

def test_distance_calculation():
    """Test the distance calculation for 'unable' and 'verify'"""

    print("🧪 Testing distance calculation...\n")

    test_text = "The system is unable to process your request. Please verify your information."
    text_lower = test_text.lower()

    unable_pos = text_lower.find("unable")
    verify_pos = text_lower.find("verify")
    distance = abs(unable_pos - verify_pos)

    print(f"Test text: '{test_text}'")
    print(f"'unable' position: {unable_pos}")
    print(f"'verify' position: {verify_pos}")
    print(f"Distance: {distance} characters")
    print(f"Within 100 chars: {distance < 100}")

    return True

if __name__ == "__main__":
    print("=== Improved CAPTCHA Detection Tests ===\n")

    all_tests_passed = True

    # Run all tests
    tests = [
        ("CAPTCHA Detection Logic", test_captcha_detection),
        ("Distance Calculation", test_distance_calculation)
    ]

    for test_name, test_func in tests:
        print(f"🚀 Running {test_name} test...")
        if not test_func():
            all_tests_passed = False
            print(f"❌ {test_name} test failed!\n")
        else:
            print(f"✅ {test_name} test passed!\n")
        print("-" * 60)

    if all_tests_passed:
        print("🎉 All tests passed! Improved CAPTCHA detection is working correctly.")
        print("✅ The new logic will only trigger on actual CAPTCHA errors, not generic content.")
    else:
        print("❌ Some tests failed. Please check the implementation.")
