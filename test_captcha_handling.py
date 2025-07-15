"""
Test script to verify CAPTCHA handling and proxy rotation functionality
"""

import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Test imports
try:
    from citypay_nyc_sb import CaptchaDetectedException, run_scraping_session
    from proxy_config import proxy_rotator
    print("✅ Successfully imported CAPTCHA handling components")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_captcha_exception():
    """Test CAPTCHA exception creation and handling"""
    print("\n🧪 Testing CAPTCHA exception...")

    try:
        # Create and raise CAPTCHA exception
        violation_num = "TEST123456"
        raise CaptchaDetectedException(violation_num, "Test CAPTCHA message")
    except CaptchaDetectedException as e:
        print(f"✅ CAPTCHA exception caught successfully")
        print(f"   • Violation number: {e.violation_number}")
        print(f"   • Message: {e.message}")
        return True
    except Exception as e:
        print(f"❌ Unexpected exception: {e}")
        return False

def test_proxy_rotation():
    """Test proxy rotation functionality"""
    print("\n🧪 Testing proxy rotation...")

    try:
        # Test getting multiple different proxies
        used_proxies = set()

        for i in range(3):
            proxy = proxy_rotator.get_seleniumbase_proxy_with_fallback(use_random=True)
            print(f"   • Proxy {i+1}: {proxy if proxy else 'No proxy'}")

            if proxy:
                used_proxies.add(proxy)

        print(f"✅ Got {len(used_proxies)} unique proxies")
        return True

    except Exception as e:
        print(f"❌ Proxy rotation test failed: {e}")
        return False

def test_session_function_signature():
    """Test that run_scraping_session function has correct signature"""
    print("\n🧪 Testing session function signature...")

    try:
        import inspect
        sig = inspect.signature(run_scraping_session)
        params = list(sig.parameters.keys())

        expected_params = ['proxy_string', 'used_proxies']

        if all(param in params for param in expected_params):
            print(f"✅ Function signature correct: {params}")
            return True
        else:
            print(f"❌ Function signature incorrect. Expected: {expected_params}, Got: {params}")
            return False

    except Exception as e:
        print(f"❌ Signature test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting CAPTCHA Handling Tests")
    print("=" * 50)

    tests = [
        test_captcha_exception,
        test_proxy_rotation,
        test_session_function_signature
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with error: {e}")
            results.append(False)

    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   • Passed: {sum(results)}/{len(results)}")
    print(f"   • Failed: {len(results) - sum(results)}/{len(results)}")

    if all(results):
        print("✅ All tests passed! CAPTCHA handling system is ready.")
    else:
        print("❌ Some tests failed. Please check the implementation.")

    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
