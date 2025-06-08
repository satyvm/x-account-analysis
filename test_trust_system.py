#!/usr/bin/env python3
"""
Trust System Test Script
========================

Test script to verify the trusted accounts validation system works correctly.
This script tests all components of the trust validation without requiring
a full mention monitoring session.

Usage:
    python test_trust_system.py

Author: X Analysis Bot
Version: 1.0
"""

import tweepy
import os
import sys
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

# Add trust_system to path
sys.path.append(str(Path(__file__).parent / "trust_system"))

try:
    from trust_system.trusted_accounts import TrustedAccountValidator
    from trust_system.trust_integration import TrustIntegratedAnalyzer
    from enhanced_analysis import ComprehensiveAnalyzer
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all required modules are in the trust_system directory")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test configuration
TEST_USER_IDS = [
    "912363642154127361",  # @satyvm (should have some trusted followers)
    "555666777888999000",  # Mock user ID for testing
]

TEST_USERNAMES = [
    "satyvm",
    "solana",
    "JupiterExchange"
]

class TrustSystemTester:
    """Comprehensive tester for the trust validation system"""
    
    def __init__(self):
        self.client = None
        self.trust_validator = None
        self.test_results = {
            'github_fetch': False,
            'account_parsing': False,
            'username_resolution': False,
            'trust_validation': False,
            'integration_test': False
        }
    
    def setup_api_client(self):
        """Setup Twitter API client"""
        try:
            print("🔐 Setting up Twitter API client...")
            
            bearer_token = os.getenv("BEARER_TOKEN")
            api_key = os.getenv("API_KEY")
            api_key_secret = os.getenv("API_KEY_SECRET")
            access_token = os.getenv("ACCESS_TOKEN")
            access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")
            
            if not all([bearer_token, api_key, api_key_secret, access_token, access_token_secret]):
                print("❌ Missing API credentials in .env file")
                return False
            
            self.client = tweepy.Client(
                bearer_token=bearer_token,
                consumer_key=api_key,
                consumer_secret=api_key_secret,
                access_token=access_token,
                access_token_secret=access_token_secret,
                wait_on_rate_limit=True
            )
            
            # Test authentication
            me = self.client.get_me()
            print(f"✅ Authenticated as @{me.data.username}")
            return True
            
        except Exception as e:
            print(f"❌ API setup failed: {e}")
            return False
    
    def test_github_fetch(self):
        """Test fetching trusted accounts from GitHub"""
        try:
            print("\n" + "="*60)
            print("🔍 TEST 1: GitHub Trust List Fetch")
            print("="*60)
            
            self.trust_validator = TrustedAccountValidator(self.client)
            
            if self.trust_validator.load_trusted_accounts():
                account_count = len(self.trust_validator.trusted_accounts)
                print(f"✅ Successfully loaded {account_count} trusted accounts")
                
                # Show sample accounts
                sample_accounts = self.trust_validator.trusted_accounts[:10]
                print(f"📋 Sample accounts: {', '.join(sample_accounts)}")
                
                # Show categories
                categories = self.trust_validator._categorize_all_accounts()
                print(f"📊 Categories found: {dict(categories)}")
                
                self.test_results['github_fetch'] = True
                self.test_results['account_parsing'] = True
                return True
            else:
                print("❌ Failed to load trusted accounts")
                return False
                
        except Exception as e:
            print(f"❌ GitHub fetch test failed: {e}")
            return False
    
    def test_username_resolution(self):
        """Test resolving usernames to user IDs"""
        try:
            print("\n" + "="*60)
            print("🔄 TEST 2: Username to ID Resolution")
            print("="*60)
            
            if not self.trust_validator:
                print("❌ Trust validator not initialized")
                return False
            
            # Test with first 10 accounts to save API calls
            test_accounts = self.trust_validator.trusted_accounts[:10]
            original_accounts = self.trust_validator.trusted_accounts.copy()
            self.trust_validator.trusted_accounts = test_accounts
            
            print(f"🔍 Testing resolution for {len(test_accounts)} accounts...")
            
            if self.trust_validator.resolve_usernames_to_ids(max_batch_size=10):
                resolved_count = len(self.trust_validator.trusted_user_ids)
                success_rate = (resolved_count / len(test_accounts)) * 100
                
                print(f"✅ Resolved {resolved_count}/{len(test_accounts)} accounts ({success_rate:.1f}%)")
                
                # Show sample resolutions
                sample_resolutions = list(self.trust_validator.trusted_user_ids.items())[:5]
                for username, user_id in sample_resolutions:
                    print(f"   └─ @{username} → {user_id}")
                
                # Restore original accounts list but keep resolved IDs
                self.trust_validator.trusted_accounts = original_accounts
                
                self.test_results['username_resolution'] = True
                return True
            else:
                print("❌ Username resolution failed")
                return False
                
        except Exception as e:
            print(f"❌ Username resolution test failed: {e}")
            return False
    
    def test_trust_validation(self):
        """Test trust validation for known accounts"""
        try:
            print("\n" + "="*60)
            print("🔒 TEST 3: Trust Validation")
            print("="*60)
            
            if not self.trust_validator or not self.trust_validator.trusted_user_ids:
                print("❌ Trust validator not properly initialized")
                return False
            
            # Test with @satyvm account
            test_user_id = "912363642154127361"  # @satyvm
            print(f"🔍 Testing trust validation for user ID: {test_user_id}")
            
            # Set a lower API limit for testing
            original_limit = self.trust_validator.max_api_calls
            self.trust_validator.max_api_calls = 10
            
            validation_result = self.trust_validator.check_trusted_followers(
                test_user_id, 
                min_trusted_followers=1  # Lower threshold for testing
            )
            
            # Restore original limit
            self.trust_validator.max_api_calls = original_limit
            
            if validation_result and not validation_result.get('validation_details', {}).get('error'):
                trusted_count = validation_result.get('trusted_follower_count', 0)
                is_validated = validation_result.get('is_validated', False)
                trust_score = validation_result.get('trust_score', {})
                
                print(f"✅ Trust validation completed:")
                print(f"   └─ Trusted followers: {trusted_count}")
                print(f"   └─ Validated: {'✅ Yes' if is_validated else '❌ No'}")
                print(f"   └─ Trust level: {trust_score.get('trust_level', 'Unknown')}")
                print(f"   └─ Trust score: {trust_score.get('overall_score', 0)}/100")
                
                # Show found trusted followers
                trusted_followers = validation_result.get('trusted_followers', [])
                if trusted_followers:
                    print(f"   └─ Found followers:")
                    for follower in trusted_followers[:3]:
                        print(f"      • @{follower['username']} ({follower['category']})")
                
                api_calls_used = validation_result.get('api_calls_used', 0)
                print(f"   └─ API calls used: {api_calls_used}")
                
                self.test_results['trust_validation'] = True
                return True
            else:
                error_msg = validation_result.get('validation_details', {}).get('error', 'Unknown error')
                print(f"❌ Trust validation failed: {error_msg}")
                return False
                
        except Exception as e:
            print(f"❌ Trust validation test failed: {e}")
            return False
    
    def test_integration(self):
        """Test integration with comprehensive analysis"""
        try:
            print("\n" + "="*60)
            print("🔬 TEST 4: Integration Test")
            print("="*60)
            
            # Create mock user for testing
            class MockUser:
                def __init__(self):
                    self.id = "912363642154127361"
                    self.username = "satyvm"
                    self.name = "satyam"
                    self.description = "dev, writer & building @fitfocus_app | satyam.btc @Stacks | satyvm.eth"
                    self.location = "Remote"
                    self.url = None
                    self.created_at = datetime(2017, 9, 1, tzinfo=timezone.utc)
                    self.verified = False
                    self.protected = False
                    self.public_metrics = {
                        'followers_count': 58,
                        'following_count': 87,
                        'tweet_count': 253,
                        'listed_count': 0
                    }
            
            # Initialize integrated analyzer
            base_analyzer = ComprehensiveAnalyzer()
            trust_analyzer = TrustIntegratedAnalyzer(self.client, base_analyzer)
            trust_analyzer.trust_validator = self.trust_validator
            trust_analyzer.trust_enabled = True
            trust_analyzer.max_trust_api_calls = 5  # Limit for testing
            
            mock_user = MockUser()
            print(f"🔍 Testing integrated analysis for @{mock_user.username}")
            
            # Perform trust-integrated analysis
            analysis_results = trust_analyzer.analyze_with_trust_validation(
                mock_user, 
                tweets_data=None, 
                force_trust_check=True
            )
            
            if analysis_results:
                print("✅ Integration test completed successfully")
                
                # Check if trust validation was included
                trust_validation = analysis_results.get('trust_validation')
                if trust_validation:
                    print("   └─ Trust validation: ✅ Included")
                    if trust_validation.get('is_validated'):
                        print(f"   └─ Result: ✅ Validated with {trust_validation.get('trusted_follower_count', 0)} trusted followers")
                    else:
                        print(f"   └─ Result: ❌ Not validated")
                else:
                    print("   └─ Trust validation: ❌ Not included")
                
                # Check overall scores
                overall_scores = analysis_results.get('overall_scores', {})
                if overall_scores:
                    print(f"   └─ Credibility score: {overall_scores.get('credibility_score', 0)}/100")
                    if overall_scores.get('trust_enhanced'):
                        print(f"   └─ Trust enhancement: ✅ Applied (+{overall_scores.get('trust_boost_applied', 0)})")
                
                self.test_results['integration_test'] = True
                return True
            else:
                print("❌ Integration test failed")
                return False
                
        except Exception as e:
            print(f"❌ Integration test failed: {e}")
            return False
    
    def test_format_display(self):
        """Test formatting and display functions"""
        try:
            print("\n" + "="*60)
            print("📋 TEST 5: Format and Display")
            print("="*60)
            
            # Create sample validation result
            sample_result = {
                'is_validated': True,
                'trusted_follower_count': 3,
                'min_required': 2,
                'validation_strength': 75,
                'trusted_followers': [
                    {'username': 'solana', 'category': 'Infrastructure'},
                    {'username': 'JupiterExchange', 'category': 'DeFi Protocol'},
                    {'username': 'aeyakovenko', 'category': 'Key Opinion Leader'}
                ],
                'trust_score': {
                    'overall_score': 85.5,
                    'trust_level': 'Highly Trusted'
                },
                'validation_details': {
                    'checked_accounts': 1000,
                    'api_calls_made': 5,
                    'follower_categories': {
                        'Infrastructure': 1,
                        'DeFi Protocol': 1,
                        'Key Opinion Leader': 1
                    }
                },
                'api_calls_used': 5
            }
            
            # Test formatting
            formatted_report = self.trust_validator.format_validation_report(
                sample_result, 
                "test_user"
            )
            
            print("✅ Sample validation report:")
            print(formatted_report)
            
            return True
            
        except Exception as e:
            print(f"❌ Format display test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all trust system tests"""
        print("🚀 Starting Trust System Comprehensive Test Suite")
        print("=" * 80)
        
        # Setup
        if not self.setup_api_client():
            print("❌ Test suite failed - could not setup API client")
            return False
        
        # Run tests
        tests = [
            ("GitHub Fetch & Parsing", self.test_github_fetch),
            ("Username Resolution", self.test_username_resolution),
            ("Trust Validation", self.test_trust_validation),
            ("Integration", self.test_integration),
            ("Format & Display", self.test_format_display),
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed_tests += 1
                else:
                    print(f"❌ {test_name} test failed")
            except Exception as e:
                print(f"❌ {test_name} test crashed: {e}")
        
        # Final summary
        print("\n" + "="*80)
        print("📊 TEST SUITE SUMMARY")
        print("="*80)
        print(f"✅ Passed: {passed_tests}/{total_tests} tests")
        print(f"❌ Failed: {total_tests - passed_tests}/{total_tests} tests")
        
        # Detailed results
        print("\n📋 Detailed Results:")
        for component, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   └─ {component.replace('_', ' ').title()}: {status}")
        
        # System status
        if self.trust_validator:
            system_status = self.trust_validator.get_system_status()
            print(f"\n🔒 Trust System Status:")
            print(f"   └─ Accounts loaded: {system_status.get('trusted_accounts_loaded', 0)}")
            print(f"   └─ IDs resolved: {system_status.get('user_ids_resolved', 0)}")
            print(f"   └─ API calls made: {system_status.get('api_calls_made', 0)}")
            print(f"   └─ System ready: {'✅' if system_status.get('system_ready') else '❌'}")
        
        success_rate = (passed_tests / total_tests) * 100
        if success_rate >= 80:
            print(f"\n🎉 Trust system is working correctly! ({success_rate:.1f}% success rate)")
            return True
        else:
            print(f"\n⚠️ Trust system has issues. ({success_rate:.1f}% success rate)")
            return False

def main():
    """Run the trust system test suite"""
    print("🔒 Trust System Test Suite")
    print("=" * 50)
    print("This script will test all components of the trusted account validation system.")
    print("Make sure you have valid Twitter API credentials in your .env file.")
    print()
    
    # Check for required files
    required_files = [
        ".env",
        "enhanced_analysis.py",
        "trust_system/trusted_accounts.py",
        "trust_system/trust_integration.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file_path in missing_files:
            print(f"   └─ {file_path}")
        print("\nPlease ensure all required files are present before running tests.")
        return
    
    # Run tests
    tester = TrustSystemTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🚀 Trust system is ready for production use!")
        print("You can now enable TRUST_VALIDATION=true in your .env file.")
    else:
        print("\n🔧 Trust system needs attention before production use.")
        print("Check the error messages above and fix any issues.")

if __name__ == "__main__":
    main()