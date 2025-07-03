# NYC Parking Ticket Scraper - Maximum Stealth Version

## 🚀 Features

This enhanced version includes advanced anti-detection measures to avoid captchas:

### 🎯 Maximum Undetection Features:
- ✅ **NO Incognito Mode** - Uses persistent browser profile for better stealth
- ✅ **Human-like Mouse Movements** - Random mouse movements and scrolling
- ✅ **Realistic Typing Patterns** - Variable typing speeds with occasional "mistakes"
- ✅ **Browser History Simulation** - Visits real websites before scraping
- ✅ **Dynamic User Agent Rotation** - Multiple realistic user agents
- ✅ **Advanced JavaScript Stealth** - Removes automation indicators
- ✅ **Random Delays** - Human-like pauses between actions
- ✅ **Configurable Behavior** - All settings customizable in `stealth_config.py`

## 📦 Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

2. Make sure you have Chrome installed on your system.

## 🔧 Configuration

Edit `stealth_config.py` to customize the behavior:

- **Mouse Movements**: Enable/disable and adjust mouse movement patterns
- **Typing Behavior**: Control typing speed and mistake probability
- **Browser History**: Configure which sites to visit and how long
- **Delays**: Set timing between requests and breaks
- **User Agents**: Add/remove user agent strings

## 📝 Usage

1. Add your violation numbers to `v_num.txt` (one per line)
2. Run the scraper:
```bash
python main.py
```

## 🛡️ Anti-Captcha Features

### What Makes This Stealth:

1. **Persistent Browser Profile**: Creates and uses a real Chrome profile instead of incognito
2. **Pre-browsing Activity**: Visits legitimate websites before hitting the target
3. **Human-like Interactions**:
   - Random mouse movements
   - Variable typing speeds
   - Realistic scrolling patterns
   - Occasional "mistakes" and corrections
4. **Timing Randomization**:
   - Random delays between requests (2-8 seconds)
   - Longer breaks every 5-10 requests (10-20 seconds)
   - Human-like page load waiting times
5. **JavaScript Stealth**: Removes webdriver detection properties
6. **Realistic Browser Fingerprint**: Proper plugins, languages, and permissions

## 📊 Output

- Primary output: `nyc_parking_tickets.json`
- Backup files: `nyc_parking_tickets_backup_X.json` (every 10 records)
- Console logs show progress and human-like behavior simulation

## ⚠️ Important Notes

- **Slower but Stealthier**: This version is intentionally slower to mimic human behavior
- **Profile Persistence**: The browser profile is saved in `chrome_profile/` directory
- **Respectful Scraping**: Built-in delays to avoid overwhelming the server
- **Error Handling**: Continues processing even if individual violations fail

## 🎛️ Customization

### Quick Stealth Adjustments:

```python
# In stealth_config.py

# Make it faster (less stealthy)
DELAYS = {
    'between_requests_min': 1,
    'between_requests_max': 3,
    # ... other settings
}

# Make it more human-like (slower but stealthier)
DELAYS = {
    'between_requests_min': 5,
    'between_requests_max': 15,
    # ... other settings
}
```

## 🚫 If You Still Get Captchas

1. **Increase delays** in `stealth_config.py`
2. **Enable more mouse movements**
3. **Add more browser history sites**
4. **Run during off-peak hours**
5. **Use a VPN or different IP** (not included in this script)

## 💡 Pro Tips

- Run during business hours for more human-like patterns
- Don't run too many violation numbers at once
- Clear the `chrome_profile/` folder occasionally to reset fingerprint
- Monitor console output to see stealth behaviors in action

---

**Note**: This scraper is designed for educational purposes and legitimate use cases. Always respect website terms of service and rate limits.
