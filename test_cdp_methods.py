#!/usr/bin/env python3
"""Test script to check available CDP methods in SeleniumBase"""

import sys
from seleniumbase import SB

def test_cdp_methods():
    print("Testing SeleniumBase CDP methods...")

    try:
        with SB(uc=True, headless=True) as sb:
            sb.activate_cdp_mode('about:blank')

            # Get all CDP methods
            cdp_methods = [method for method in dir(sb.cdp) if not method.startswith('_')]

            print(f"\nTotal CDP methods available: {len(cdp_methods)}")

            # Filter wait methods
            wait_methods = [m for m in cdp_methods if 'wait' in m.lower()]
            print(f"\nWait methods ({len(wait_methods)}):")
            for method in sorted(wait_methods):
                print(f"  - {method}")

            # Filter network methods
            network_methods = [m for m in cdp_methods if 'network' in m.lower()]
            print(f"\nNetwork methods ({len(network_methods)}):")
            for method in sorted(network_methods):
                print(f"  - {method}")

            # Check specifically for wait_for_network_idle
            if hasattr(sb.cdp, 'wait_for_network_idle'):
                print("\n✅ wait_for_network_idle is available!")
                # Try to get method signature
                import inspect
                try:
                    sig = inspect.signature(sb.cdp.wait_for_network_idle)
                    print(f"   Signature: wait_for_network_idle{sig}")
                except:
                    print("   (Could not get signature)")
            else:
                print("\n❌ wait_for_network_idle is NOT available")

                # Look for alternatives
                alternatives = [m for m in cdp_methods if any(word in m.lower() for word in ['idle', 'load', 'complete', 'ready'])]
                if alternatives:
                    print("   Possible alternatives:")
                    for alt in sorted(alternatives):
                        print(f"     - {alt}")

    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    success = test_cdp_methods()
    sys.exit(0 if success else 1)
