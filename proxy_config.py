"""
Proxy configuration for NYC Government Scrapers
Rotating proxy system with authentication
"""

import random
import time
from proxy_auth_extension import ProxyAuthExtension

# Manual rotating proxies list - Cleaned and validated
ROTATING_PROXIES = [
    "156.237.27.135:5533:skhszrmm:euk5hl55raao",
    "45.56.179.33:9237:skhszrmm:euk5hl55raao",
    "72.1.181.16:5410:skhszrmm:euk5hl55raao",
    "156.237.33.182:5586:skhszrmm:euk5hl55raao",
    "156.237.21.93:5489:skhszrmm:euk5hl55raao",
    "156.237.31.141:5536:skhszrmm:euk5hl55raao",
    "45.196.61.192:6230:skhszrmm:euk5hl55raao",
    "45.56.180.76:8310:skhszrmm:euk5hl55raao",
    "45.196.32.95:5727:skhszrmm:euk5hl55raao",
    "192.46.187.201:6779:skhszrmm:euk5hl55raao",
    "216.98.254.170:6480:skhszrmm:euk5hl55raao",
    "156.237.37.204:5606:skhszrmm:euk5hl55raao",
    "46.203.161.90:5587:skhszrmm:euk5hl55raao",
    "192.46.187.197:6775:skhszrmm:euk5hl55raao",
    "156.237.37.202:5604:skhszrmm:euk5hl55raao",
    "45.56.183.12:8334:skhszrmm:euk5hl55raao",
    "72.46.138.197:6423:skhszrmm:euk5hl55raao",
    "46.203.29.46:6533:skhszrmm:euk5hl55raao",
    "154.194.24.105:5715:skhszrmm:euk5hl55raao"
]

class ProxyRotator:
    """Handles proxy rotation for NYC Government Scrapers"""

    def __init__(self):
        # Filter out empty or invalid proxies
        self.proxy_list = [proxy.strip() for proxy in ROTATING_PROXIES if proxy.strip()]
        self.current_proxy_index = 0
        self.last_rotation_time = 0
        self.rotation_interval = 300  # 5 minutes between rotations
        print(f"✅ ProxyRotator initialized with {len(self.proxy_list)} valid proxies")

    def get_random_proxy(self):
        """Get a random proxy from the list"""
        return random.choice(self.proxy_list)

    def get_next_proxy(self):
        """Get the next proxy in rotation"""
        proxy = self.proxy_list[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxy_list)
        return proxy

    def should_rotate_proxy(self):
        """Check if it's time to rotate proxy"""
        current_time = time.time()
        if current_time - self.last_rotation_time > self.rotation_interval:
            self.last_rotation_time = current_time
            return True
        return False

    def parse_proxy_string(self, proxy_string):
        """Parse proxy string format: IP:PORT:USERNAME:PASSWORD"""
        if not proxy_string or not proxy_string.strip():
            return None

        parts = proxy_string.strip().split(':')
        if len(parts) == 4:
            ip, port, username, password = parts
            return {
                'ip': ip.strip(),
                'port': port.strip(),
                'username': username.strip(),
                'password': password.strip(),
                'proxy_url': f"http://{username.strip()}:{password.strip()}@{ip.strip()}:{port.strip()}"
            }
        return None

    def get_proxy_for_seleniumbase(self, use_random=True):
        """Get proxy configuration for SeleniumBase SB() - Returns proxy string"""
        if use_random:
            proxy_string = self.get_random_proxy()
        else:
            proxy_string = self.get_next_proxy()

        proxy_data = self.parse_proxy_string(proxy_string)
        if proxy_data:
            print(f"🔄 Using proxy: {proxy_data['ip']}:{proxy_data['port']} (User: {proxy_data['username']})")
            # Return SeleniumBase format: USERNAME:PASSWORD@IP:PORT
            return f"{proxy_data['username']}:{proxy_data['password']}@{proxy_data['ip']}:{proxy_data['port']}"
        return None

    def get_proxy_for_seleniumbase_with_validation(self, use_random=True):
        """Get validated proxy configuration for SeleniumBase with better error handling"""
        max_attempts = 3
        for attempt in range(max_attempts):
            if use_random:
                proxy_string = self.get_random_proxy()
            else:
                proxy_string = self.get_next_proxy()

            proxy_data = self.parse_proxy_string(proxy_string)
            if proxy_data:
                print(f"🔄 Attempt {attempt + 1}: Using proxy {proxy_data['ip']}:{proxy_data['port']}")
                # Return SeleniumBase format: USERNAME:PASSWORD@IP:PORT
                proxy_formatted = f"{proxy_data['username']}:{proxy_data['password']}@{proxy_data['ip']}:{proxy_data['port']}"
                print(f"✅ Proxy formatted for SeleniumBase: {proxy_formatted}")
                return proxy_formatted
            else:
                print(f"❌ Invalid proxy string: {proxy_string}")

        print("⚠️ Failed to get valid proxy after 3 attempts")
        return None

    def get_proxy_chrome_args(self, use_random=True):
        """Get proxy arguments for Chrome options (Alternative method)"""
        if use_random:
            proxy_string = self.get_random_proxy()
        else:
            proxy_string = self.get_next_proxy()

        proxy_data = self.parse_proxy_string(proxy_string)
        if proxy_data:
            print(f"🔄 Chrome proxy: {proxy_data['ip']}:{proxy_data['port']}")
            return [
                f"--proxy-server=http://{proxy_data['ip']}:{proxy_data['port']}",
                f"--proxy-auth={proxy_data['username']}:{proxy_data['password']}",
                "--disable-extensions",
                "--disable-plugins",
                "--disable-images",
                "--disable-javascript",
                "--no-sandbox"
            ]
        return []

    def get_chrome_args_with_extension(self, use_random=True):
        """Get Chrome args with proxy auth extension to prevent authentication popups"""
        if use_random:
            proxy_string = self.get_random_proxy()
        else:
            proxy_string = self.get_next_proxy()

        proxy_data = self.parse_proxy_string(proxy_string)
        if proxy_data:
            print(f"🔄 Creating proxy auth extension for: {proxy_data['ip']}:{proxy_data['port']}")

            extension = ProxyAuthExtension()
            chrome_args = extension.get_chrome_args_with_extension(
                proxy_data['ip'],
                proxy_data['port'],
                proxy_data['username'],
                proxy_data['password']
            )
            return chrome_args, extension
        return [], None

    def get_seleniumbase_proxy_with_fallback(self, use_random=True):
        """Get proxy with fallback options to prevent authentication popups"""
        proxy_formatted = self.get_proxy_for_seleniumbase_with_validation(use_random)
        if proxy_formatted:
            return proxy_formatted

        # Fallback: try without proxy
        print("⚠️ Using direct connection (no proxy) as fallback")
        return None

# Global proxy rotator instance
proxy_rotator = ProxyRotator()

def get_current_proxy():
    """Get current proxy for logging/debugging"""
    return proxy_rotator.get_random_proxy()

def test_proxy_configuration():
    """Test the proxy configuration"""
    print("🧪 Testing proxy configuration...")
    rotator = ProxyRotator()

    # Test validated proxy
    proxy_str = rotator.get_proxy_for_seleniumbase_with_validation(use_random=True)
    print(f"✅ Validated proxy string: {proxy_str}")

    # Test fallback method
    proxy_str = rotator.get_seleniumbase_proxy_with_fallback(use_random=True)
    print(f"✅ Fallback proxy string: {proxy_str}")

    # Test sequential proxy
    proxy_str = rotator.get_proxy_for_seleniumbase(use_random=False)
    print(f"✅ Sequential proxy string: {proxy_str}")

    # Test Chrome args (alternative method)
    chrome_args = rotator.get_proxy_chrome_args(use_random=True)
    print(f"✅ Chrome args: {chrome_args}")

    # Test Chrome args with extension
    chrome_args_ext, _ = rotator.get_chrome_args_with_extension(use_random=True)
    print(f"✅ Chrome args with extension: {chrome_args_ext}")

    print("✅ Proxy configuration test completed")
    print(f"📊 Total valid proxies available: {len(rotator.proxy_list)}")

if __name__ == "__main__":
    test_proxy_configuration()
