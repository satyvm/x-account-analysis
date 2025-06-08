#!/usr/bin/env python3
"""
Trust-Enabled X Account Mention Analyzer
=======================================

Advanced Twitter/X mention monitoring system with comprehensive profile analysis
and trusted account cross-check validation using the Solana ecosystem trust list.

Features:
- Smart mention detection (direct mentions and reply targeting)
- Comprehensive profile analysis with 100+ data points
- Trusted account validation using GitHub trust list
- API credit optimization for free tier accounts
- Real-time risk assessment and authenticity scoring
- Business intelligence and influence metrics
- Detailed logging and output tracking

Trust Validation:
- Fetches trusted accounts from: https://github.com/devsyrem/turst-list/blob/main/list
- Validates if accounts are followed by 2+ trusted Solana ecosystem accounts
- Provides trust scoring and credibility enhancement

Author: X Analysis Bot
Version: 3.0 Trust-Enabled
"""

import tweepy
import time
import os
import json
import logging
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

# Add trust_system to path
sys.path.append(str(Path(__file__).parent / "trust_system"))

# Import our modules
from enhanced_analysis import ComprehensiveAnalyzer
from trust_system.trusted_accounts import TrustedAccountValidator
from trust_system.trust_integration import TrustIntegratedAnalyzer

# Load environment variables
load_dotenv()

# Setup comprehensive logging
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    handlers=[
        logging.FileHandler('trust_enabled_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- Configuration ---
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
API_KEY = os.getenv("API_KEY")
API_KEY_SECRET = os.getenv("API_KEY_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
YOUR_USER_ID = os.getenv("YOUR_SATYVM_USER_ID")

# Search and analysis configuration
MENTION_TRIGGER = "@satyvm acc"
LAST_SEEN_ID_FILE = "last_seen_id.txt"
API_USAGE_FILE = "api_usage_trust_enabled.json"
MAX_API_CALLS_PER_SESSION = 15  # Increased for trust validation
MIN_TRUSTED_FOLLOWERS = 2  # Minimum trusted followers for validation

# Feature flags
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"
DEEP_ANALYSIS = os.getenv("DEEP_ANALYSIS", "true").lower() == "true"
TRUST_VALIDATION = os.getenv("TRUST_VALIDATION", "true").lower() == "true"

class TrustEnabledAPITracker:
    """Enhanced API usage tracker with trust validation support"""
    
    def __init__(self):
        self.usage_file = API_USAGE_FILE
        self.session_calls = 0
        self.trust_calls = 0
        self.analysis_calls = 0
        self.session_details = []
        self.load_usage_data()
    
    def load_usage_data(self):
        """Load existing API usage data"""
        try:
            if os.path.exists(self.usage_file):
                with open(self.usage_file, 'r') as f:
                    self.usage_data = json.load(f)
            else:
                self.usage_data = {
                    "total_calls": 0,
                    "daily_calls": {},
                    "endpoint_usage": {},
                    "trust_calls": 0,
                    "analysis_calls": 0,
                    "last_reset": datetime.now(timezone.utc).isoformat(),
                    "sessions": []
                }
            logger.info(f"📊 API Usage loaded - Total: {self.usage_data.get('total_calls', 0)}, Trust: {self.usage_data.get('trust_calls', 0)}")
        except Exception as e:
            logger.error(f"❌ Error loading API usage data: {e}")
            self.usage_data = {"total_calls": 0, "trust_calls": 0, "analysis_calls": 0}
    
    def record_api_call(self, endpoint_name, cost=1, call_type="general"):
        """Record API call with categorization"""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        timestamp = datetime.now(timezone.utc).isoformat()
        
        self.session_calls += cost
        self.usage_data["total_calls"] = self.usage_data.get("total_calls", 0) + cost
        
        # Track by type
        if call_type == "trust":
            self.trust_calls += cost
            self.usage_data["trust_calls"] = self.usage_data.get("trust_calls", 0) + cost
        elif call_type == "analysis":
            self.analysis_calls += cost
            self.usage_data["analysis_calls"] = self.usage_data.get("analysis_calls", 0) + cost
        
        # Daily and endpoint tracking
        if today not in self.usage_data["daily_calls"]:
            self.usage_data["daily_calls"][today] = 0
        self.usage_data["daily_calls"][today] += cost
        
        if endpoint_name not in self.usage_data["endpoint_usage"]:
            self.usage_data["endpoint_usage"][endpoint_name] = 0
        self.usage_data["endpoint_usage"][endpoint_name] += cost
        
        # Session details
        call_detail = {
            "endpoint": endpoint_name,
            "cost": cost,
            "type": call_type,
            "timestamp": timestamp,
            "session_total": self.session_calls
        }
        self.session_details.append(call_detail)
        
        logger.info(f"🔥 API CALL: {endpoint_name} ({call_type}) - Cost: {cost} - Session: {self.session_calls}/{MAX_API_CALLS_PER_SESSION}")
        
        self.save_usage_data()
        return self.session_calls < MAX_API_CALLS_PER_SESSION
    
    def save_usage_data(self):
        """Save enhanced usage data"""
        try:
            if self.session_details:
                session_summary = {
                    "start_time": self.session_details[0]["timestamp"],
                    "end_time": self.session_details[-1]["timestamp"],
                    "total_calls": self.session_calls,
                    "trust_calls": self.trust_calls,
                    "analysis_calls": self.analysis_calls,
                    "calls": self.session_details.copy()
                }
                
                if "sessions" not in self.usage_data:
                    self.usage_data["sessions"] = []
                self.usage_data["sessions"].append(session_summary)
                self.usage_data["sessions"] = self.usage_data["sessions"][-50:]
            
            with open(self.usage_file, 'w') as f:
                json.dump(self.usage_data, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Error saving API usage data: {e}")
    
    def can_make_call(self):
        """Check if we can make another API call"""
        return self.session_calls < MAX_API_CALLS_PER_SESSION
    
    def get_detailed_summary(self):
        """Get comprehensive usage summary"""
        remaining = 60 - self.usage_data.get('total_calls', 0)
        return {
            'session_calls': self.session_calls,
            'trust_calls_session': self.trust_calls,
            'analysis_calls_session': self.analysis_calls,
            'total_calls': self.usage_data.get('total_calls', 0),
            'total_trust_calls': self.usage_data.get('trust_calls', 0),
            'total_analysis_calls': self.usage_data.get('analysis_calls', 0),
            'remaining_credits': max(remaining, 0),
            'endpoint_breakdown': self.usage_data.get('endpoint_usage', {}),
            'efficiency_rating': self._calculate_efficiency()
        }
    
    def _calculate_efficiency(self):
        """Calculate API usage efficiency"""
        total = self.usage_data.get('total_calls', 0)
        if total <= 20: return "Excellent"
        elif total <= 35: return "Very Good"
        elif total <= 50: return "Good"
        elif total <= 55: return "Fair"
        else: return "Poor"

class TrustEnabledMentionMonitor:
    """Advanced mention monitor with integrated trust validation"""
    
    def __init__(self):
        self.api_tracker = TrustEnabledAPITracker()
        self.client = None
        self.base_analyzer = ComprehensiveAnalyzer()
        self.trust_analyzer = None
        self.last_seen_id = self.read_last_seen_id()
        
    def initialize_system(self):
        """Initialize the complete trust-enabled system"""
        try:
            logger.info("🚀 Initializing Trust-Enabled X Mention Monitor")
            
            # Authenticate with Twitter API
            if not self.authenticate():
                return False
            
            # Initialize base analyzer
            logger.info("🔬 Initializing comprehensive analyzer...")
            
            # Initialize trust system if enabled
            if TRUST_VALIDATION:
                logger.info("🔒 Initializing trust validation system...")
                self.trust_analyzer = TrustIntegratedAnalyzer(self.client, self.base_analyzer)
                
                # Set trust parameters
                self.trust_analyzer.min_trusted_followers = MIN_TRUSTED_FOLLOWERS
                self.trust_analyzer.max_trust_api_calls = 8  # Reserve API calls for trust
                
                if self.trust_analyzer.initialize_trust_system():
                    logger.info("✅ Trust validation system ready")
                else:
                    logger.warning("⚠️ Trust validation system failed - continuing without trust")
                    self.trust_analyzer = None
            else:
                logger.info("ℹ️ Trust validation disabled")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ System initialization failed: {e}")
            return False
    
    def authenticate(self):
        """Authenticate with X API"""
        logger.info("🔐 Authenticating with X API...")
        
        if not all([BEARER_TOKEN, API_KEY, API_KEY_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, YOUR_USER_ID]):
            logger.error("❌ Missing API credentials. Check your .env file.")
            return False
        
        try:
            self.client = tweepy.Client(
                bearer_token=BEARER_TOKEN,
                consumer_key=API_KEY,
                consumer_secret=API_KEY_SECRET,
                access_token=ACCESS_TOKEN,
                access_token_secret=ACCESS_TOKEN_SECRET,
                wait_on_rate_limit=True
            )
            
            if self.api_tracker.can_make_call():
                me = self.client.get_me()
                self.api_tracker.record_api_call("get_me", 1, "general")
                logger.info(f"✅ Successfully authenticated as @{me.data.username}")
                return True
            else:
                logger.warning("⚠️ Cannot authenticate - API call limit reached")
                return False
                
        except Exception as e:
            logger.error(f"❌ Authentication failed: {e}")
            return False
    
    def read_last_seen_id(self):
        """Read the last processed tweet ID"""
        try:
            if os.path.exists(LAST_SEEN_ID_FILE):
                with open(LAST_SEEN_ID_FILE, 'r') as f:
                    last_id = f.read().strip()
                    if last_id:
                        logger.info(f"📖 Last seen tweet ID: {last_id}")
                        return int(last_id)
            logger.info("📖 No previous tweet ID found")
            return None
        except Exception as e:
            logger.error(f"❌ Error reading last seen ID: {e}")
            return None
    
    def write_last_seen_id(self, tweet_id):
        """Save the latest processed tweet ID"""
        try:
            with open(LAST_SEEN_ID_FILE, 'w') as f:
                f.write(str(tweet_id))
            logger.info(f"💾 Saved last seen tweet ID: {tweet_id}")
        except Exception as e:
            logger.error(f"❌ Error saving last seen ID: {e}")
    
    def fetch_mentions(self):
        """Fetch new mentions with comprehensive data"""
        if TEST_MODE:
            return self.get_test_mentions()
        
        if not self.api_tracker.can_make_call():
            logger.warning("⚠️ Cannot fetch mentions - API call limit reached")
            return []
        
        try:
            logger.info(f"🔍 Fetching mentions for user ID: {YOUR_USER_ID}")
            
            params = {
                'id': YOUR_USER_ID,
                'tweet_fields': [
                    'created_at', 'author_id', 'public_metrics', 
                    'in_reply_to_user_id', 'referenced_tweets',
                    'text', 'entities', 'context_annotations'
                ],
                'expansions': [
                    'author_id', 'in_reply_to_user_id', 
                    'referenced_tweets.id.author_id'
                ],
                'user_fields': [
                    'username', 'name', 'description', 'location', 'url',
                    'public_metrics', 'profile_image_url', 'created_at',
                    'verified', 'verified_type', 'protected'
                ],
                'max_results': 10
            }
            
            if self.last_seen_id:
                params['since_id'] = self.last_seen_id
            
            mentions = self.client.get_users_mentions(**params)
            self.api_tracker.record_api_call("get_users_mentions", 1, "general")
            
            if not mentions.data:
                logger.info("📭 No new mentions found")
                return []
            
            logger.info(f"📬 Found {len(mentions.data)} new mentions")
            
            # Update last seen ID
            if mentions.meta.get('newest_id'):
                self.write_last_seen_id(mentions.meta['newest_id'])
            
            # Filter relevant mentions
            relevant_mentions = []
            for mention in mentions.data:
                if MENTION_TRIGGER.lower() in mention.text.lower():
                    relevant_mentions.append((mention, mentions.includes))
                    
                    if hasattr(mention, 'in_reply_to_user_id') and mention.in_reply_to_user_id:
                        logger.info(f"🔄 Reply mention found - target: {mention.in_reply_to_user_id}")
                    else:
                        logger.info(f"🎯 Direct mention found - from: {mention.author_id}")
            
            return relevant_mentions
            
        except Exception as e:
            logger.error(f"❌ Error fetching mentions: {e}")
            return []
    
    def get_test_mentions(self):
        """Generate comprehensive test mentions"""
        logger.info("🧪 TEST MODE: Generating enhanced test data")
        
        class MockMention:
            def __init__(self):
                self.id = "1234567890123456789"
                self.text = "Impressive blockchain security research! @satyvm acc what's your analysis of this new DeFi protocol's smart contract architecture?"
                self.author_id = "987654321098765432"
                self.in_reply_to_user_id = "555666777888999000"
                self.created_at = datetime.now(timezone.utc)
        
        class MockUser:
            def __init__(self, user_type="target"):
                if user_type == "target":
                    self.id = "555666777888999000"
                    self.username = "defi_security_expert"
                    self.name = "Alex Chen | DeFi Security Researcher"
                    self.description = "🔐 Lead Security Researcher @trailofbits | Smart Contract Auditor | DeFi Protocol Advisor | Previously @consensys | Building safer Web3 | alex.eth"
                    self.location = "San Francisco, CA"
                    self.url = "https://alexchen.security"
                    self.profile_image_url = "https://example.com/alex_avatar.jpg"
                    self.created_at = datetime(2018, 11, 20, tzinfo=timezone.utc)
                    self.verified = True
                    self.verified_type = "blue"
                    self.protected = False
                    self.public_metrics = {
                        'followers_count': 15420,
                        'following_count': 892,
                        'tweet_count': 3247,
                        'listed_count': 189
                    }
                else:
                    self.id = "987654321098765432"
                    self.username = "crypto_enthusiast"
                    self.name = "Crypto Enthusiast"
                    self.description = "Web3 builder and DeFi researcher"
                    self.location = "Remote"
                    self.created_at = datetime(2021, 5, 1, tzinfo=timezone.utc)
                    self.verified = False
                    self.protected = False
                    self.public_metrics = {
                        'followers_count': 823,
                        'following_count': 1240,
                        'tweet_count': 1456,
                        'listed_count': 12
                    }
        
        mock_mention = MockMention()
        mock_replier = MockUser("replier")
        mock_target = MockUser("target")
        mock_includes = {'users': [mock_replier, mock_target]}
        
        logger.info("🧪 Generated comprehensive test data with trust validation targets")
        return [(mock_mention, mock_includes)]
    
    def analyze_mention(self, mention, includes):
        """Perform comprehensive analysis with trust validation"""
        try:
            # Determine target user
            target_user_id = mention.author_id
            mention_type = "Direct mention"
            
            if hasattr(mention, 'in_reply_to_user_id') and mention.in_reply_to_user_id:
                target_user_id = mention.in_reply_to_user_id
                mention_type = "Reply to original tweet author"
            
            # Find target user in includes
            target_user = None
            if includes and 'users' in includes:
                for user in includes['users']:
                    if hasattr(user, 'id') and str(user.id) == str(target_user_id):
                        target_user = user
                        break
            
            if not target_user:
                logger.error(f"❌ Could not find target user: {target_user_id}")
                return
            
            logger.info(f"🔬 Analyzing @{target_user.username} ({mention_type})")
            
            # Display basic info first
            self._display_basic_info(target_user, mention, mention_type)
            
            # Perform enhanced analysis if enabled
            if DEEP_ANALYSIS and self.api_tracker.can_make_call():
                self._perform_enhanced_analysis(target_user)
            
        except Exception as e:
            logger.error(f"❌ Error analyzing mention: {e}")
            if DEBUG_MODE:
                logger.error(traceback.format_exc())
    
    def _display_basic_info(self, user, mention, mention_type):
        """Display basic account information"""
        try:
            output = []
            output.append("\n" + "="*90)
            output.append("🎯 NEW MENTION DETECTED!")
            output.append("="*90)
            output.append(f"📋 Type: {mention_type}")
            
            if mention_type.startswith("Reply"):
                output.append(f"👥 Replier: User ID {mention.author_id}")
                output.append(f"📄 Analyzing: Original tweet author")
            
            # Enhanced basic info
            output.append(f"👤 Username: @{getattr(user, 'username', 'N/A')}")
            output.append(f"📛 Display Name: {getattr(user, 'name', 'N/A')}")
            output.append(f"📝 Bio: {getattr(user, 'description', 'No bio')[:100]}{'...' if len(getattr(user, 'description', '')) > 100 else ''}")
            output.append(f"📍 Location: {getattr(user, 'location', 'Not specified')}")
            
            if hasattr(user, 'public_metrics'):
                metrics = user.public_metrics
                output.append(f"👥 Network: {metrics.get('followers_count', 0):,} followers / {metrics.get('following_count', 0):,} following")
                ratio = metrics.get('followers_count', 0) / max(metrics.get('following_count', 1), 1)
                output.append(f"📊 Ratio: {ratio:.2f} | Tweets: {metrics.get('tweet_count', 0):,}")
            
            if getattr(user, 'verified', False):
                output.append(f"✅ Verified: {getattr(user, 'verified_type', 'yes').title()}")
            
            if hasattr(user, 'created_at'):
                age = (datetime.now(timezone.utc) - user.created_at.replace(tzinfo=timezone.utc)).days
                output.append(f"📅 Account Age: {age:,} days ({age//365} years)")
            
            output.append(f"💬 Mention: {mention.text}")
            output.append(f"🔗 Profile: https://twitter.com/{getattr(user, 'username', 'unknown')}")
            output.append("="*90)
            
            # Print and save
            for line in output:
                print(line)
            
            self._save_to_file(output, 'enhanced_mentions_output.txt')
            
        except Exception as e:
            logger.error(f"❌ Error displaying basic info: {e}")
    
    def _perform_enhanced_analysis(self, user):
        """Perform comprehensive analysis with trust validation"""
        try:
            logger.info("🔬 Starting comprehensive analysis...")
            
            # Fetch tweets if API calls available
            tweets_data = None
            if self.api_tracker.can_make_call():
                tweets_data = self._fetch_user_tweets(user.id)
            
            # Perform analysis with or without trust validation
            if self.trust_analyzer and TRUST_VALIDATION:
                logger.info("🔒 Performing trust-integrated analysis...")
                analysis_results = self.trust_analyzer.analyze_with_trust_validation(
                    user, tweets_data, force_trust_check=True
                )
                
                # Format and display trust-enhanced results
                enhanced_report = self.trust_analyzer.format_enhanced_analysis_report(analysis_results)
                print(enhanced_report)
                
                # Save comprehensive results
                self.trust_analyzer.save_enhanced_analysis(analysis_results)
                
                # Track trust API calls
                trust_calls = analysis_results.get('trust_integration', {}).get('api_calls_used', 0)
                if trust_calls > 0:
                    self.api_tracker.trust_calls += trust_calls
                
            else:
                logger.info("📊 Performing standard comprehensive analysis...")
                analysis_results = self.base_analyzer.analyze_comprehensive_profile(user, tweets_data)
                
                # Format and display standard results
                standard_report = self.base_analyzer.format_comprehensive_analysis(analysis_results)
                print(standard_report)
                
                # Save results
                self.base_analyzer.save_analysis_to_file(analysis_results)
            
            logger.info(f"✅ Enhanced analysis completed for @{user.username}")
            
        except Exception as e:
            logger.error(f"❌ Error in enhanced analysis: {e}")
            if DEBUG_MODE:
                logger.error(traceback.format_exc())
    
    def _fetch_user_tweets(self, user_id):
        """Fetch user tweets for analysis"""
        try:
            if not self.api_tracker.can_make_call():
                return None
            
            tweets = self.client.get_users_tweets(
                id=user_id,
                max_results=50,
                tweet_fields=['created_at', 'public_metrics', 'text', 'entities'],
                exclude=['retweets']
            )
            
            self.api_tracker.record_api_call("get_users_tweets", 1, "analysis")
            return tweets
            
        except Exception as e:
            logger.error(f"❌ Error fetching tweets: {e}")
            return None
    
    def _save_to_file(self, content, filename):
        """Save content to file"""
        try:
            with open(filename, 'a', encoding='utf-8') as f:
                f.write(f"\n--- {datetime.now(timezone.utc).isoformat()} ---\n")
                for line in content:
                    f.write(line + "\n")
                f.write("\n")
        except Exception as e:
            logger.error(f"❌ Error saving to file: {e}")
    
    def run_monitoring_session(self):
        """Main monitoring session with trust validation"""
        try:
            logger.info("🚀 Starting Trust-Enabled Monitoring Session")
            logger.info(f"🎯 Trigger: '{MENTION_TRIGGER}'")
            logger.info(f"📊 Session limit: {MAX_API_CALLS_PER_SESSION} API calls")
            logger.info(f"🔒 Trust validation: {'✅ Enabled' if TRUST_VALIDATION else '❌ Disabled'}")
            
            # Fetch mentions
            mentions = self.fetch_mentions()
            
            if not mentions:
                logger.info("🔚 No relevant mentions found")
                return
            
            logger.info(f"📱 Processing {len(mentions)} mention(s)")
            
            # Process each mention
            for i, (mention, includes) in enumerate(mentions, 1):
                if not self.api_tracker.can_make_call():
                    logger.warning(f"⚠️ API limit reached - skipping remaining {len(mentions)-i+1} mentions")
                    break
                
                logger.info(f"📱 Processing mention {i}/{len(mentions)}")
                self.analyze_mention(mention, includes)
                
                # Small delay between mentions
                if i < len(mentions):
                    time.sleep(0.5)
            
            logger.info("✅ Monitoring session completed")
            
        except KeyboardInterrupt:
            logger.info("🛑 Monitoring stopped by user")
        except Exception as e:
            logger.error(f"❌ Error in monitoring session: {e}")
            if DEBUG_MODE:
                logger.error(traceback.format_exc())
        finally:
            self._display_session_summary()
    
    def _display_session_summary(self):
        """Display comprehensive session summary"""
        try:
            summary = self.api_tracker.get_detailed_summary()
            
            print("\n" + "="*80)
            print("📊 TRUST-ENABLED SESSION SUMMARY")
            print("="*80)
            print(f"🔥 Total API calls: {summary['session_calls']}")
            print(f"📈 Monthly total: {summary['total_calls']}/60")
            print(f"💳 Credits remaining: ~{summary['remaining_credits']}")
            print(f"⚡ Efficiency: {summary['efficiency_rating']}")
            
            print(f"\n🔒 TRUST VALIDATION:")
            print(f"   └─ Session calls: {summary['trust_calls_session']}")
            print(f"   └─ Total trust calls: {summary['total_trust_calls']}")
            
            print(f"\n🔬 ANALYSIS:")
            print(f"   └─ Session calls: {summary['analysis_calls_session']}")
            print(f"   └─ Total analysis calls: {summary['total_analysis_calls']}")
            
            if summary['endpoint_breakdown']:
                print(f"\n📋 ENDPOINT BREAKDOWN:")
                for endpoint, count in sorted(summary['endpoint_breakdown'].items()):
                    print(f"   └─ {endpoint}: {count} calls")
            
            # Trust system status
            if self.trust_analyzer:
                trust_status = self.trust_analyzer.get_trust_system_status()
                print(f"\n🔒 TRUST SYSTEM STATUS:")
                print(f"   └─ System ready: {'✅' if trust_status.get('system_ready') else '❌'}")
                print(f"   └─ Accounts loaded: {trust_status.get('trusted_accounts_loaded', 0)}")
                print(f"   └─ IDs resolved: {trust_status.get('user_ids_resolved', 0)}")
            
            print("="*80)
            
        except Exception as e:
            logger.error(f"❌ Error displaying session summary: {e}")

def main():
    """Trust-enabled main entry point"""
    print("🤖 Trust-Enabled X Account Mention Analyzer v3.0")
    print("🔍 Advanced monitoring with comprehensive analysis & trust validation")
    print("🔒 Solana ecosystem trust verification powered by GitHub trust list")
    print("💳 Optimized for API credit conservation")
    
    # Display configuration
    config_info = []
    if TEST_MODE:
        config_info.append("🧪 TEST MODE")
    if DEBUG_MODE:
        config_info.append("🔍 DEBUG MODE")
    if DEEP_ANALYSIS:
        config_info.append("🔬 DEEP ANALYSIS")
    if TRUST_VALIDATION:
        config_info.append("🔒 TRUST VALIDATION")
    
    if config_info:
        print(f"⚙️  Active modes: {' | '.join(config_info)}")
    
    print(f"📊 Session limit: {MAX_API_CALLS_PER_SESSION} API calls")
    print(f"🎯 Trust threshold: {MIN_TRUSTED_FOLLOWERS}+ trusted followers")
    print()
    
    # Initialize and run
    monitor = TrustEnabledMentionMonitor()
    
    if monitor.initialize_system():
        monitor.run_monitoring_session()
    else:
        logger.error("❌ System initialization failed")
        print("❌ Failed to initialize system - check logs for details")

if __name__ == "__main__":
    main()