"""
Alternative Proxy Authentication Methods for SeleniumBase
This provides multiple ways to handle proxy authentication without popups
"""

from seleniumbase import SB
from proxy_config import proxy_rotator
from proxy_auth_extension import ProxyAuthExtension
import time
import os

def test_proxy_method_1_sb_native():
    """Method 1: SeleniumBase native proxy parameter"""
    print("🧪 Method 1: SeleniumBase native proxy parameter")

    proxy_string = proxy_rotator.get_seleniumbase_proxy_with_fallback(use_random=True)
    print(f"Proxy string: {proxy_string}")

    with SB(uc=True, headless=False, proxy=proxy_string) as sb:
        print("Browser opened with SB native proxy")
        sb.open("https://httpbin.org/ip")
        time.sleep(5)
        try:
            content = sb.get_text("body")
            print(f"✅ Success: {content}")
        except Exception as e:
            print(f"❌ Error: {e}")

def test_proxy_method_2_chrome_args():
    """Method 2: Chrome arguments with proxy server"""
    print("🧪 Method 2: Chrome arguments with proxy server")

    proxy_data = proxy_rotator.parse_proxy_string(proxy_rotator.get_random_proxy())
    if not proxy_data:
        print("❌ No proxy data")
        return

    # Chrome args method
    chrome_args = [
        f"--proxy-server=http://{proxy_data['ip']}:{proxy_data['port']}",
        "--no-proxy-server",
        "--disable-web-security",
        "--disable-features=VizDisplayCompositor"
    ]

    print(f"Chrome args: {chrome_args}")

    with SB(uc=True, headless=False, chromium_arg=",".join(chrome_args)) as sb:
        print("Browser opened with Chrome args")
        # Manually set proxy auth via CDP
        sb.execute_cdp_cmd("Network.enable", {})
        sb.execute_cdp_cmd("Network.setUserAgentOverride", {
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

        sb.open("https://httpbin.org/ip")
        time.sleep(5)
        try:
            content = sb.get_text("body")
            print(f"✅ Success: {content}")
        except Exception as e:
            print(f"❌ Error: {e}")

def test_proxy_method_3_extension():
    """Method 3: Chrome extension for proxy authentication"""
    print("🧪 Method 3: Chrome extension for proxy authentication")

    proxy_data = proxy_rotator.parse_proxy_string(proxy_rotator.get_random_proxy())
    if not proxy_data:
        print("❌ No proxy data")
        return

    # Create extension
    extension = ProxyAuthExtension()
    extension_dir = extension.create_extension(proxy_data['username'], proxy_data['password'])

    chrome_args = [
        f"--proxy-server=http://{proxy_data['ip']}:{proxy_data['port']}",
        f"--load-extension={extension_dir}",
        "--disable-web-security"
    ]

    print(f"Extension dir: {extension_dir}")

    with SB(uc=True, headless=False, chromium_arg=",".join(chrome_args)) as sb:
        print("Browser opened with Chrome extension")
        sb.open("https://httpbin.org/ip")
        time.sleep(5)
        try:
            content = sb.get_text("body")
            print(f"✅ Success: {content}")
        except Exception as e:
            print(f"❌ Error: {e}")

    # Cleanup
    extension.cleanup()

def test_proxy_method_4_requests_session():
    """Method 4: Create authenticated proxy session with requests"""
    print("🧪 Method 4: Use requests session for proxy validation first")

    import requests

    proxy_data = proxy_rotator.parse_proxy_string(proxy_rotator.get_random_proxy())
    if not proxy_data:
        print("❌ No proxy data")
        return

    # Test proxy with requests first
    proxy_url = f"http://{proxy_data['username']}:{proxy_data['password']}@{proxy_data['ip']}:{proxy_data['port']}"
    proxies = {
        'http': proxy_url,
        'https': proxy_url
    }

    try:
        response = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=10)
        print(f"✅ Requests test successful: {response.text}")

        # If requests works, use the proxy with SeleniumBase
        proxy_string = f"{proxy_data['username']}:{proxy_data['password']}@{proxy_data['ip']}:{proxy_data['port']}"

        with SB(uc=True, headless=False, proxy=proxy_string) as sb:
            print("Browser opened after requests validation")
            sb.open("https://httpbin.org/ip")
            time.sleep(5)
            try:
                content = sb.get_text("body")
                print(f"✅ SeleniumBase success: {content}")
            except Exception as e:
                print(f"❌ SeleniumBase error: {e}")

    except Exception as e:
        print(f"❌ Requests test failed: {e}")

def test_proxy_method_5_manual_auth():
    """Method 5: Manual proxy authentication handling"""
    print("🧪 Method 5: Manual proxy authentication handling")

    proxy_data = proxy_rotator.parse_proxy_string(proxy_rotator.get_random_proxy())
    if not proxy_data:
        print("❌ No proxy data")
        return

    # Create a more robust proxy configuration
    proxy_config = {
        'host': proxy_data['ip'],
        'port': int(proxy_data['port']),
        'username': proxy_data['username'],
        'password': proxy_data['password']
    }

    print(f"Proxy config: {proxy_config}")

    # Use chrome options to disable auth dialog
    chrome_args = [
        f"--proxy-server=http://{proxy_config['host']}:{proxy_config['port']}",
        "--disable-background-timer-throttling",
        "--disable-backgrounding-occluded-windows",
        "--disable-renderer-backgrounding",
        "--disable-field-trial-config",
        "--disable-ipc-flooding-protection",
        "--password-store=basic",
        "--use-mock-keychain"
    ]

    with SB(uc=True, headless=False, chromium_arg=",".join(chrome_args)) as sb:
        print("Browser opened with manual auth handling")

        # Try to handle authentication via CDP
        try:
            sb.execute_cdp_cmd("Network.enable", {})
            sb.execute_cdp_cmd("Runtime.enable", {})

            # Set up authentication handler
            auth_script = f"""
            chrome.webRequest.onAuthRequired.addListener(
                function(details) {{
                    return {{
                        authCredentials: {{
                            username: '{proxy_config['username']}',
                            password: '{proxy_config['password']}'
                        }}
                    }};
                }},
                {{urls: ["<all_urls>"]}},
                ['blocking']
            );
            """

            sb.execute_script(auth_script)

        except Exception as e:
            print(f"CDP setup warning: {e}")

        sb.open("https://httpbin.org/ip")
        time.sleep(5)
        try:
            content = sb.get_text("body")
            print(f"✅ Manual auth success: {content}")
        except Exception as e:
            print(f"❌ Manual auth error: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("TESTING ALL PROXY AUTHENTICATION METHODS")
    print("=" * 60)

    methods = [
        test_proxy_method_1_sb_native,
        test_proxy_method_2_chrome_args,
        test_proxy_method_3_extension,
        test_proxy_method_4_requests_session,
        test_proxy_method_5_manual_auth
    ]

    for i, method in enumerate(methods, 1):
        print(f"\n{'='*20} TEST {i} {'='*20}")
        try:
            method()
        except Exception as e:
            print(f"❌ Method {i} failed: {e}")
        print("="*50)

    print("\n✅ All method tests completed!")
    print("❗ Check which method worked without authentication popups!")
