#!/usr/bin/env python3
"""
Main entry point for GEHC PHTC Test Application.

This module allows the package to be executed as a module:
    python -m gehc_phtc_test
"""

import sys
import asyncio
from gehc_phtc_test.src.main import main

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nApplication terminated by user")
        sys.exit(130)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)