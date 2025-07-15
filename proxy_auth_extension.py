"""
Chrome Extension Generator for Proxy Authentication
This creates a Chrome extension that automatically handles proxy authentication
to prevent authentication popup dialogs.
"""

import os
import json
import zipfile
from tempfile import TemporaryDirectory

class ProxyAuthExtension:
    """Creates a Chrome extension for automatic proxy authentication"""

    def __init__(self):
        self.extension_dir = None

    def create_extension(self, username, password, temp_dir=None):
        """Create a Chrome extension for proxy authentication"""

        if temp_dir is None:
            temp_dir = os.path.join(os.getcwd(), "temp_proxy_extension")

        # Create directory if it doesn't exist
        os.makedirs(temp_dir, exist_ok=True)

        # Manifest file
        manifest = {
            "manifest_version": 2,
            "name": "Proxy Auth Extension",
            "version": "1.0",
            "description": "Automatic proxy authentication",
            "permissions": [
                "webRequest",
                "webRequestBlocking",
                "<all_urls>",
                "proxy"
            ],
            "background": {
                "scripts": ["background.js"],
                "persistent": True
            }
        }

        # Background script
        background_js = f"""
chrome.webRequest.onAuthRequired.addListener(
    function(details) {{
        return {{
            authCredentials: {{
                username: "{username}",
                password: "{password}"
            }}
        }};
    }},
    {{ urls: ["<all_urls>"] }},
    ['blocking']
);

console.log("Proxy Auth Extension loaded with credentials");
"""

        # Write files
        manifest_path = os.path.join(temp_dir, "manifest.json")
        background_path = os.path.join(temp_dir, "background.js")

        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)

        with open(background_path, 'w') as f:
            f.write(background_js)

        self.extension_dir = temp_dir
        print(f"✅ Proxy auth extension created in: {temp_dir}")
        return temp_dir

    def get_chrome_args_with_extension(self, proxy_ip, proxy_port, username, password):
        """Get Chrome arguments with proxy auth extension"""
        extension_dir = self.create_extension(username, password)

        return [
            f"--proxy-server=http://{proxy_ip}:{proxy_port}",
            f"--load-extension={extension_dir}",
            "--disable-extensions-except=" + extension_dir,
            "--disable-web-security",
            "--disable-features=VizDisplayCompositor",
            "--no-sandbox",
            "--disable-dev-shm-usage"
        ]

    def cleanup(self):
        """Clean up temporary extension files"""
        if self.extension_dir and os.path.exists(self.extension_dir):
            import shutil
            shutil.rmtree(self.extension_dir)
            print(f"🧹 Cleaned up extension directory: {self.extension_dir}")

def create_proxy_auth_extension_for_seleniumbase(proxy_data):
    """Helper function to create extension for SeleniumBase"""
    if not proxy_data:
        return None

    extension = ProxyAuthExtension()
    extension_dir = extension.create_extension(
        proxy_data['username'],
        proxy_data['password']
    )
    return extension_dir

if __name__ == "__main__":
    # Test the extension creation
    extension = ProxyAuthExtension()
    test_dir = extension.create_extension("testuser", "testpass")
    print(f"Test extension created in: {test_dir}")

    # Test Chrome args
    args = extension.get_chrome_args_with_extension("127.0.0.1", "8080", "user", "pass")
    print(f"Chrome args: {args}")

    # Cleanup
    extension.cleanup()
