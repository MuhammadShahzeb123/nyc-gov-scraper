"""
Real Browser Test for Proxy Authentication
This test actually opens a SeleniumBase browser with proxy to verify no authentication popups appear
"""

from seleniumbase import SB
from proxy_config import proxy_rotator
import time

def test_real_browser_with_proxy():
    """Test actual browser with proxy to see if authentication popups appear"""
    print("🧪 Testing REAL BROWSER with proxy authentication...")

    # Get proxy configuration
    proxy_string = proxy_rotator.get_seleniumbase_proxy_with_fallback(use_random=True)
    if not proxy_string:
        print("❌ No proxy available for testing")
        return

    print(f"🌐 Testing with proxy: {proxy_string}")

    try:
        # Open SeleniumBase with proxy
        with SB(
            uc=True,
            headless=False,  # Keep visible to see if popups appear
            proxy=proxy_string,
            slow=2  # Slow down for observation
        ) as sb:
            print("🚀 Browser opened successfully with proxy")

            # Try to navigate to a test website
            print("📋 Navigating to test website...")
            sb.open("https://httpbin.org/ip")  # This will show our IP

            # Wait to see if any authentication popups appear
            print("⏳ Waiting 10 seconds to observe for authentication popups...")
            time.sleep(10)

            # Try to get the page content
            try:
                page_text = sb.get_text("body")
                print("✅ Successfully loaded page content:")
                print(page_text[:200] + "..." if len(page_text) > 200 else page_text)
            except Exception as e:
                print(f"❌ Error getting page content: {e}")

            # Try another website
            print("📋 Testing with another website...")
            sb.open("https://api.ipify.org?format=json")
            time.sleep(5)

            try:
                page_text = sb.get_text("body")
                print("✅ Successfully loaded second page:")
                print(page_text)
            except Exception as e:
                print(f"❌ Error getting second page: {e}")

    except Exception as e:
        print(f"❌ Browser test failed: {e}")

def test_browser_with_chrome_extension():
    """Test browser with Chrome extension method for proxy authentication"""
    print("🧪 Testing BROWSER with Chrome Extension proxy authentication...")

    # Get Chrome args with extension
    chrome_args, extension = proxy_rotator.get_chrome_args_with_extension(use_random=True)
    if not chrome_args:
        print("❌ Failed to create Chrome extension")
        return

    print(f"🔧 Chrome args: {chrome_args}")

    try:
        # Open SeleniumBase with Chrome extension
        with SB(
            uc=True,
            headless=False,
            chromium_arg=",".join(chrome_args),
            slow=2
        ) as sb:
            print("🚀 Browser opened with Chrome extension for proxy auth")

            # Navigate to test website
            print("📋 Testing with Chrome extension...")
            sb.open("https://httpbin.org/ip")

            print("⏳ Waiting 10 seconds to check for authentication popups...")
            time.sleep(10)

            try:
                page_text = sb.get_text("body")
                print("✅ Chrome extension test - page loaded:")
                print(page_text[:200] + "..." if len(page_text) > 200 else page_text)
            except Exception as e:
                print(f"❌ Chrome extension test failed: {e}")

        # Cleanup extension
        if extension:
            extension.cleanup()

    except Exception as e:
        print(f"❌ Chrome extension browser test failed: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("REAL BROWSER PROXY AUTHENTICATION TEST")
    print("=" * 60)

    # Test 1: Standard SeleniumBase proxy method
    test_real_browser_with_proxy()

    print("\n" + "=" * 60)

    # Test 2: Chrome extension method
    test_browser_with_chrome_extension()

    print("=" * 60)
    print("✅ Real browser testing completed")
    print("❗ Did you see any authentication popup dialogs? If yes, we need to fix this!")
