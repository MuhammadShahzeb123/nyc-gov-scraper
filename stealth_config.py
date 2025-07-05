# Stealth Configuration for NYC Parking Ticket Scraper
"""
Advanced stealth configuration to maximize undetection and avoid captchas
"""

# Mouse movement settings
MOUSE_MOVEMENTS = {
    'enabled': True,
    'min_movements': 2,
    'max_movements': 5,
    'max_offset_x': 100,
    'max_offset_y': 50,
    'movement_delay_min': 0.1,
    'movement_delay_max': 0.3
}

# Typing behavior settings
TYPING_BEHAVIOR = {
    'enabled': True,
    'char_delay_min': 0.05,
    'char_delay_max': 0.15,
    'mistake_probability': 0.1,  # 10% chance of making a "mistake"
    'pre_type_delay_min': 0.5,
    'pre_type_delay_max': 1.0
}

# Browser history settings
BROWSER_HISTORY = {
    'enabled': True,
    'sites': [
        "https://www.google.com",
        "https://www.wikipedia.org",
        "https://www.news.google.com",
        "https://www.weather.com",
        "https://www.cnn.com",
        "https://www.reddit.com"
    ],
    'visit_count': 2,  # Number of sites to visit
    'visit_duration_min': 2,
    'visit_duration_max': 4
}

# Delay settings (in seconds)
DELAYS = {
    'between_requests_min': 2,
    'between_requests_max': 8,
    'longer_break_frequency_min': 5,
    'longer_break_frequency_max': 10,
    'longer_break_duration_min': 10,
    'longer_break_duration_max': 20,
    'page_load_min': 2,
    'page_load_max': 4,
    'random_behavior_probability': 0.3  # 30% chance
}

# User agents for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0'
]

# Chrome options for maximum stealth
CHROME_OPTIONS = {
    'disable_automation': True,
    'disable_infobars': True,
    'disable_popup_blocking': True,
    'disable_notifications': True,
    'no_sandbox': True,
    'disable_dev_shm_usage': True,
    'disable_gpu': True,
    'disable_extensions': True,
    'start_maximized': True,
    'incognito': False,  # Set to False for better stealth
    'disable_browser_side_navigation': True,
    'disable_web_security': True,
    'disable_features_viz_display_compositor': True,
    'disable_ipc_flooding_protection': True,
    'window_size': '1920,1080'
}

# Stealth JavaScript scripts
STEALTH_SCRIPTS = [
    # Remove webdriver property
    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})",

    # Mock plugins
    """
    Object.defineProperty(navigator, 'plugins', {
        get: () => [1, 2, 3, 4, 5]
    });
    """,

    # Mock languages
    """
    Object.defineProperty(navigator, 'languages', {
        get: () => ['en-US', 'en']
    });
    """,

    # Mock permissions
    """
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
        parameters.name === 'notifications' ?
            Promise.resolve({ state: Notification.permission }) :
            originalQuery(parameters)
    );
    """,

    # Hide automation indicators
    """
    Object.defineProperty(navigator, 'webdriver', {
        get: () => false,
    });
    """,

    # Mock chrome runtime
    """
    window.chrome = {
        runtime: {}
    };
    """,

    # Override image loading to make it more realistic
    """
    const originalImageSrc = Object.getOwnPropertyDescriptor(Image.prototype, 'src');
    Object.defineProperty(Image.prototype, 'src', {
        get: function() {
            return originalImageSrc.get.call(this);
        },
        set: function(value) {
            const result = originalImageSrc.set.call(this, value);
            this.dispatchEvent(new Event('load'));
            return result;
        }
    });
    """
]

# Scrolling behavior
SCROLLING = {
    'enabled': True,
    'min_scroll': 100,
    'max_scroll': 500,
    'scroll_back_probability': 0.3,  # 30% chance to scroll back
    'scroll_delay_min': 0.5,
    'scroll_delay_max': 1.0
}
