#!/usr/bin/env python3
"""
Health check seguro - sem shell injection
AURORA CORE TIER-0
"""

import sys
import urllib.request
import ssl


def main():
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    
    try:
        req = urllib.request.Request(
            'http://localhost:8081/health/live',
            headers={'User-Agent': 'Aurora-HealthCheck/1.0'}
        )
        with urllib.request.urlopen(req, timeout=2.0, context=context) as response:
            if response.status == 200:
                sys.exit(0)
            else:
                sys.exit(1)
    except Exception as e:
        print(f"Health check failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

