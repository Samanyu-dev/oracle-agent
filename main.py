#!/usr/bin/env python3
"""
Proxy entry point for Oracle Agent.
Allows running from project root without cd-ing into src/.
"""

import sys
import os

# Add src/ to path so all imports work
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

# Delegate to actual main
from main import main

if __name__ == '__main__':
    main()
