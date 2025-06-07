#!/usr/bin/env python3
"""
X Account Mention Analyzer - Runner Script
==========================================

Convenient script to run the X mention monitor with various options.

Usage:
    python run.py                    # Normal mode
    python run.py --test            # Test mode (no API calls)
    python run.py --debug           # Debug mode (verbose logging)
    python run.py --test --debug    # Test + debug mode
    python run.py --help            # Show this help
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

def setup_environment(test_mode=False, debug_mode=False):
    """Setup environment variables for the run"""
    env = os.environ.copy()
    
    if test_mode:
        env['TEST_MODE'] = 'true'
        print("🧪 Running in TEST MODE - No real API calls will be made")
    else:
        env['TEST_MODE'] = 'false'
    
    if debug_mode:
        env['DEBUG_MODE'] = 'true'
        print("🔍 Running in DEBUG MODE - Verbose logging enabled")
    else:
        env['DEBUG_MODE'] = 'false'
    
    return env

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import tweepy
        import dotenv
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("📦 Install dependencies with: uv sync")
        print("📦 Or with pip: pip install tweepy python-dotenv")
        return False

def check_env_file():
    """Check if .env file exists and has required variables"""
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found!")
        print("📝 Create .env file with your X API credentials")
        return False
    
    # Read and check for required variables
    required_vars = [
        'BEARER_TOKEN',
        'API_KEY', 
        'API_KEY_SECRET',
        'ACCESS_TOKEN',
        'ACCESS_TOKEN_SECRET',
        'YOUR_SATYVM_USER_ID'
    ]
    
    with open('.env', 'r') as f:
        content = f.read()
    
    missing_vars = []
    for var in required_vars:
        if var not in content or f'{var}=""' in content:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing or empty variables in .env: {', '.join(missing_vars)}")
        return False
    
    return True

def show_usage_info():
    """Show API usage information"""
    usage_file = Path('api_usage.json')
    if usage_file.exists():
        import json
        try:
            with open(usage_file, 'r') as f:
                usage_data = json.load(f)
            total_calls = usage_data.get('total_calls', 0)
            remaining = 60 - total_calls
            print(f"📊 API Usage: {total_calls}/60 calls used this month ({remaining} remaining)")
        except Exception:
            pass

def main():
    parser = argparse.ArgumentParser(
        description='X Account Mention Analyzer - Monitor mentions efficiently',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py                    # Normal monitoring
  python run.py --test            # Test with mock data
  python run.py --debug           # Verbose logging
  python run.py --test --debug    # Test + debug mode
  python run.py --status          # Show current API usage
        """
    )
    
    parser.add_argument('--test', action='store_true',
                       help='Run in test mode (no real API calls)')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode (verbose logging)')
    parser.add_argument('--status', action='store_true',
                       help='Show API usage status and exit')
    
    args = parser.parse_args()
    
    print("🤖 X Account Mention Analyzer")
    print("=" * 50)
    
    # Show status and exit if requested
    if args.status:
        show_usage_info()
        return
    
    # Pre-flight checks
    print("🔍 Running pre-flight checks...")
    
    if not check_dependencies():
        return 1
    
    if not check_env_file():
        return 1
    
    show_usage_info()
    print("✅ All checks passed!\n")
    
    # Setup environment
    env = setup_environment(args.test, args.debug)
    
    # Run the main script
    try:
        print("🚀 Starting X mention monitor...\n")
        
        # Use uv if available, otherwise fall back to python
        try:
            result = subprocess.run(['uv', 'run', 'python', 'main.py'], 
                                  env=env, check=True)
        except FileNotFoundError:
            # uv not found, use regular python
            result = subprocess.run([sys.executable, 'main.py'], 
                                  env=env, check=True)
        
        print("\n✅ Monitor completed successfully!")
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Monitor failed with exit code: {e.returncode}")
        return e.returncode
    except KeyboardInterrupt:
        print("\n🛑 Monitor stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())