#!/usr/bin/env python3
"""
Script para executar testes do AURORA CORE TIER-0
"""

import subprocess
import sys
import os

def main():
    """Run all tests"""
    print("🧪 AURORA CORE TIER-0 - TEST SUITE")
    print("=" * 50)
    
    # Change to aurora_core directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    aurora_core_dir = os.path.dirname(script_dir)
    os.chdir(aurora_core_dir)
    
    # Run pytest
    print("\n📋 Running pytest...")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
        capture_output=False
    )
    
    if result.returncode == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ Tests failed with code {result.returncode}")
    
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())

