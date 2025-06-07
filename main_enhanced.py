#!/usr/bin/env python3
"""
Enhanced X Account Mention Analyzer with Comprehensive Profile Analysis
====================================================================

Advanced Twitter/X mention monitoring system with deep profile intelligence,
content behavior analysis, risk assessment, and business intelligence.

Features:
- Smart mention detection (direct mentions and reply targeting)
- Comprehensive profile analysis with 100+ data points
- API credit optimization for free tier accounts
- Real-time risk assessment and authenticity scoring
- Business intelligence and influence metrics
- Detailed logging and output tracking

Author: X Analysis Bot
Version: 2.0 Enhanced
"""

import tweepy
import time
import os
import json
import logging
import math
import re
from datetime import datetime, timezone
from collections import Counter
from dotenv import load_dotenv

# Import our enhanced analysis module
from enhanced_analysis import ComprehensiveAnalyzer

# Try to import textblob for sentiment analysis
try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False

# Load environment variables from .env file
load_dotenv()

# Setup detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('x_monitor_enhanced.log'),
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

# Search configuration
MENTION_TRIGGER = "@satyvm acc"
LAST_SEEN_ID_FILE = "last_seen_id.txt"
API_USAGE_FILE = "api_usage_enhanced.json"
MAX_API_CALLS_PER_SESSION = 10  # Increased for comprehensive analysis
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"
DEEP_ANALYSIS = os.getenv("DEEP_ANALYSIS", "false").lower() == "true"

class APIUsageTracker:
    """Enhanced API usage tracking with detailed monitoring"""
    
    def __init__(self):
        self.usage_file = API_USAGE_FILE
        self.session_calls = 0
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
                    "last_reset": datetime.now(timezone.utc).isoformat(),
                    "sessions": []
                }
            logger.info(f"📊 API Usage loaded - Total calls this month: {self.usage_data.get('total_calls', 0)}")
        except Exception as e:
            logger.error(f"❌ Error loading API usage data: {e}")
            self.usage_data = {"total_calls": 0, "daily_calls": {}, "endpoint_usage": {}}
    
    def record_api_call(self, endpoint_name, cost=1):
        """Record an API call with detailed tracking"""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        timestamp = datetime.now(timezone.utc).isoformat()
        
        self.session_calls += cost
        self.usage_data["total_calls"] = self.usage_data.get("total_calls", 0) + cost
        
        # Daily tracking
        if today not in self.usage_data["daily_calls"]:
            self.usage_data["daily_calls"][today] = 0
        self.usage_data["daily_calls"][today] += cost
        
        # Endpoint tracking
        if endpoint_name not in self.usage_data["endpoint_usage"]:
            self.usage_data["endpoint_usage"][endpoint_name] = 0
        self.usage_data["endpoint_usage"][endpoint_name] += cost
        
        # Session details
        call_detail = {
            "endpoint": endpoint_name,
            "cost": cost,
            "timestamp": timestamp,
            "session_total": self.session_calls
        }
        self.session_details.append(call_detail)
        
        logger.info(f"🔥 API CALL: {endpoint_name} (Cost: {cost}) - Session: {self.session_calls}/{MAX_API_CALLS_PER_SESSION}, Total: {self.usage_data['total_calls']}")
        
        self.save_usage_data()
        
        if self.session_calls >= MAX_API_CALLS_PER_SESSION:
            logger.warning(f"⚠️  Session API limit reached ({MAX_API_CALLS_PER_SESSION}). Consider increasing limit for comprehensive analysis.")
            return False
        return True
    
    def save_usage_data(self):
        """Save usage data to file"""
        try:
            # Add current session to sessions log
            if self.session_details:
                session_summary = {
                    "start_time": self.session_details[0]["timestamp"],
                    "end_time": self.session_details[-1]["timestamp"],
                    "total_calls": self.session_calls,
                    "calls": self.session_details.copy()
                }
                
                if "sessions" not in self.usage_data:
                    self.usage_data["sessions"] = []
                self.usage_data["sessions"].append(session_summary)
                
                # Keep only last 50 sessions
                self.usage_data["sessions"] = self.usage_data["sessions"][-50:]
            
            with open(self.usage_file, 'w') as f:
                json.dump(self.usage_data, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Error saving API usage data: {e}")
    
    def can_make_call(self):
        """Check if we can make another API call"""
        return self.session_calls < MAX_API_CALLS_PER_SESSION
    
    def get_usage_summary(self):
        """Get detailed usage summary"""
        remaining = 60 - self.usage_data.get('total_calls', 0)
        return {
            'session_calls': self.session_calls,
            'total_calls': self.usage_data.get('total_calls', 0),
            'remaining_credits': max(remaining, 0),
            'endpoint_breakdown': self.usage_data.get('endpoint_usage', {}),
            'efficiency_rating': self._calculate_efficiency_rating()
        }
    
    def _calculate_efficiency_rating(self):
        """Calculate API usage efficiency rating"""
        total_calls = self.usage_data.get('total_calls', 0)
        if total_calls == 0:
            return "Perfect"
        elif total_calls <= 30:
            return "Excellent"
        elif total_calls <= 45:
            return "Good"
        elif total_calls <= 55:
            return "Fair"
        else:
            return "Poor"

class EnhancedXMentionMonitor:
    """Enhanced X/Twitter mention monitor with comprehensive analysis"""
    
    def __init__(self):
        self.api_tracker = APIUsageTracker()
        self.analyzer = ComprehensiveAnalyzer()
        self.client = None
        self.last_seen_id = self.read_last_seen_id()
        
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
                self.api_tracker.record_api_call("get_me", 1)
                logger.info(f"✅ Successfully authenticated as @{me.data.username}")
                return True
            else:
                logger.warning("⚠️  Cannot authenticate - API call limit reached")
                return False
                
        except Exception as e:
            logger.error(f"❌ Authentication failed: {e}")
            return False
    
    def read_last_seen_id(self):
        """Read the ID of the last processed tweet"""
        try:
            if os.path.exists(LAST_SEEN_ID_FILE):
                with open(LAST_SEEN_ID_FILE, 'r') as f:
                    last_id = f.read().strip()
                    if last_id:
                        logger.info(f"📖 Last seen tweet ID: {last_id}")
                        return int(last_id)
            logger.info("📖 No previous tweet ID found - will fetch recent mentions")
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
        """Fetch new mentions with comprehensive user data"""
        if TEST_MODE:
            return self.get_test_mentions()
        
        if not self.api_tracker.can_make_call():
            logger.warning("⚠️  Cannot fetch mentions - API call limit reached")
            return []
        
        try:
            logger.info(f"🔍 Fetching mentions for user ID: {YOUR_USER_ID}")
            
            # Enhanced API call with comprehensive user fields
            params = {
                'id': YOUR_USER_ID,
                'tweet_fields': [
                    'created_at', 'author_id', 'public_metrics', 
                    'in_reply_to_user_id', 'referenced_tweets',
                    'text', 'entities', 'context_annotations',
                    'conversation_id', 'reply_settings'
                ],
                'expansions': [
                    'author_id', 'in_reply_to_user_id', 
                    'referenced_tweets.id.author_id'
                ],
                'user_fields': [
                    'username', 'name', 'description', 'location', 'url',
                    'public_metrics', 'profile_image_url', 'created_at',
                    'verified', 'verified_type', 'protected', 'profile_banner_url'
                ],
                'max_results': 10
            }
            
            if self.last_seen_id:
                params['since_id'] = self.last_seen_id
            
            mentions = self.client.get_users_mentions(**params)
            
            if not self.api_tracker.record_api_call("get_users_mentions", 1):
                logger.warning("⚠️  API limit reached after this call")
            
            if not mentions.data:
                logger.info("📭 No new mentions found")
                return []
            
            logger.info(f"📬 Found {len(mentions.data)} new mentions")
            
            # Update last seen ID
            newest_id = mentions.meta.get('newest_id')
            if newest_id:
                self.write_last_seen_id(newest_id)
            
            # Filter mentions containing trigger phrase
            relevant_mentions = []
            for mention in mentions.data:
                logger.info(f"📝 Processing mention: '{mention.text[:100]}...'")
                if MENTION_TRIGGER.lower() in mention.text.lower():
                    if hasattr(mention, 'in_reply_to_user_id') and mention.in_reply_to_user_id:
                        logger.info(f"🔄 Found reply mention - Original tweet author ID: {mention.in_reply_to_user_id}")
                    else:
                        logger.info(f"🎯 Found direct mention from user ID: {mention.author_id}")
                    relevant_mentions.append((mention, mentions.includes))
                else:
                    logger.info(f"⏭️  Mention doesn't contain trigger phrase")
            
            return relevant_mentions
            
        except tweepy.TooManyRequests as e:
            logger.error(f"❌ Rate limit exceeded: {e}")
            wait_time = 60
            logger.info(f"⏰ Waiting {wait_time} seconds before retry...")
            time.sleep(wait_time)
            return []
        except Exception as e:
            logger.error(f"❌ Error fetching mentions: {e}")
            return []
    
    def get_test_mentions(self):
        """Generate comprehensive test mentions for testing"""
        logger.info("🧪 TEST MODE: Generating comprehensive mock mentions")
        
        class MockMention:
            def __init__(self, is_reply=True):
                self.id = "1234567890123456789"
                if is_reply:
                    self.text = "Great insights on blockchain security! @satyvm acc what's your take on this new DeFi protocol?"
                    self.author_id = "987654321098765432"
                    self.in_reply_to_user_id = "555666777888999000"
                else:
                    self.text = "Hey @satyvm acc can you analyze this crypto project?"
                    self.author_id = "987654321098765432"
                    self.in_reply_to_user_id = None
                self.created_at = datetime.now(timezone.utc)
        
        class MockUser:
            def __init__(self, user_type="comprehensive"):
                if user_type == "comprehensive":
                    self.id = "555666777888999000"
                    self.username = "blockchaindev_sarah"
                    self.name = "Sarah Chen | Blockchain Security Expert"
                    self.description = "🔐 Senior Security Researcher @CertiK | Smart Contract Auditor | DeFi Security Specialist | Speaker | Building safer Web3 | Views are my own | sarah.eth"
                    self.location = "San Francisco, CA"
                    self.url = "https://sarahchen.dev"
                    self.profile_image_url = "https://example.com/sarah_avatar.jpg"
                    self.profile_banner_url = "https://example.com/sarah_banner.jpg"
                    self.created_at = datetime(2019, 8, 15, tzinfo=timezone.utc)
                    self.verified = True
                    self.verified_type = "blue"
                    self.protected = False
                    self.public_metrics = {
                        'followers_count': 28750,
                        'following_count': 1247,
                        'tweet_count': 4830,
                        'listed_count': 423,
                        'like_count': 15673
                    }
                else:
                    self.id = "987654321098765432"
                    self.username = "testuser123"
                    self.name = "Test Replier"
                    self.description = "Just a test account for development"
                    self.location = "Test City"
                    self.url = None
                    self.created_at = datetime(2022, 1, 1, tzinfo=timezone.utc)
                    self.verified = False
                    self.protected = False
                    self.public_metrics = {
                        'followers_count': 150,
                        'following_count': 200,
                        'tweet_count': 500,
                        'listed_count': 5
                    }
        
        mock_mention = MockMention(is_reply=True)
        mock_replier = MockUser("replier")
        mock_target = MockUser("comprehensive")
        mock_includes = {'users': [mock_replier, mock_target]}
        
        logger.info("🧪 Generated comprehensive test data for analysis")
        return [(mock_mention, mock_includes)]
    
    def fetch_user_tweets(self, user_id):
        """Fetch recent tweets for content analysis"""
        if not self.api_tracker.can_make_call():
            logger.warning("⚠️  Cannot fetch tweets - API call limit reached")
            return None
        
        try:
            tweets = self.client.get_users_tweets(
                id=user_id,
                max_results=50,
                tweet_fields=[
                    'created_at', 'public_metrics', 'in_reply_to_user_id', 
                    'text', 'entities', 'context_annotations', 'referenced_tweets'
                ],
                exclude=['retweets']
            )
            
            self.api_tracker.record_api_call("get_users_tweets", 1)
            return tweets
            
        except Exception as e:
            logger.error(f"❌ Error fetching user tweets: {e}")
            return None
    
    def display_account_info(self, mention, includes):
        """Display enhanced account information with comprehensive analysis"""
        try:
            # Determine which user to analyze
            target_user_id = mention.author_id
            mention_type = "Direct mention"
            
            if hasattr(mention, 'in_reply_to_user_id') and mention.in_reply_to_user_id:
                target_user_id = mention.in_reply_to_user_id
                mention_type = "Reply to original tweet author"
                logger.info(f"🔄 Reply detected - analyzing original tweet author (ID: {target_user_id})")
            else:
                logger.info(f"💬 Direct mention - analyzing mention author (ID: {target_user_id})")
            
            # Find the target user
            target_user = None
            if includes and 'users' in includes:
                for user in includes['users']:
                    if hasattr(user, 'id') and str(user.id) == str(target_user_id):
                        target_user = user
                        break
            
            if not target_user:
                logger.error(f"❌ Could not find user information for target user ID: {target_user_id}")
                return
            
            # Display basic account info
            self._display_basic_info(target_user, mention, mention_type)
            
            # Perform comprehensive analysis if enabled
            if DEEP_ANALYSIS and self.api_tracker.can_make_call():
                logger.info("🔬 Starting comprehensive profile analysis...")
                self._perform_comprehensive_analysis(target_user)
            elif DEEP_ANALYSIS:
                logger.warning("⚠️ Comprehensive analysis requested but API limit reached")
            
        except Exception as e:
            logger.error(f"❌ Error displaying account info: {e}")
            if DEBUG_MODE:
                import traceback
                logger.error(f"❌ Full traceback: {traceback.format_exc()}")
    
    def _display_basic_info(self, user, mention, mention_type):
        """Display basic account information"""
        output = []
        output.append("\n" + "="*80)
        output.append("🎯 NEW MENTION DETECTED!")
        output.append("="*80)
        output.append(f"📋 Type: {mention_type}")
        
        if mention_type.startswith("Reply"):
            output.append(f"👥 Replier: User ID {mention.author_id}")
            output.append(f"📄 Showing: Original tweet author details")
        
        output.append(f"👤 Username: @{getattr(user, 'username', 'N/A')}")
        output.append(f"📛 Display Name: {getattr(user, 'name', 'N/A')}")
        output.append(f"📝 Bio: {getattr(user, 'description', None) or 'No bio available'}")
        output.append(f"📍 Location: {getattr(user, 'location', None) or 'Not specified'}")
        
        if hasattr(user, 'public_metrics'):
            metrics = user.public_metrics
            output.append(f"👥 Followers: {metrics.get('followers_count', 'N/A'):,}")
            output.append(f"➡️  Following: {metrics.get('following_count', 'N/A'):,}")
            output.append(f"📊 Tweets: {metrics.get('tweet_count', 'N/A'):,}")
            output.append(f"❤️  Listed: {metrics.get('listed_count', 'N/A'):,}")
        
        # Enhanced profile indicators
        if getattr(user, 'verified', False):
            verification_type = getattr(user, 'verified_type', 'verified')
            output.append(f"✅ Verification: {verification_type.title()}")
        
        if hasattr(user, 'created_at') and user.created_at:
            age_days = (datetime.now(timezone.utc) - user.created_at.replace(tzinfo=timezone.utc)).days
            age_years = age_days // 365
            output.append(f"📅 Account Age: {age_years} years ({age_days:,} days)")
        
        output.append(f"🔗 Profile URL: https://twitter.com/{getattr(user, 'username', 'unknown')}")
        output.append(f"🖼️  Profile Image: {getattr(user, 'profile_image_url', 'N/A')}")
        output.append(f"💬 Mention Text: {mention.text}")
        output.append(f"⏰ Posted: {mention.created_at}")
        output.append(f"🔢 Tweet ID: {mention.id}")
        output.append("="*80 + "\n")
        
        # Print and save output
        for line in output:
            print(line)
        
        self._save_basic_info(output, user)
        logger.info(f"✅ Successfully displayed basic info for @{getattr(user, 'username', 'unknown')}")
    
    def _perform_comprehensive_analysis(self, user):
        """Perform and display comprehensive analysis"""
        try:
            # Fetch user tweets for content analysis
            tweets_data = None
            if self.api_tracker.can_make_call():
                tweets_data = self.fetch_user_tweets(user.id)
            
            # Perform comprehensive analysis
            analysis_results = self.analyzer.analyze_comprehensive_profile(user, tweets_data)
            
            # Display formatted results
            formatted_analysis = self.analyzer.format_comprehensive_analysis(analysis_results)
            print(formatted_analysis)
            
            # Save to file
            self.analyzer.save_analysis_to_file(analysis_results, "comprehensive_analysis_output.txt")
            
            # Save detailed JSON for debugging
            if DEBUG_MODE:
                json_filename = f"analysis_debug_{user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(json_filename, 'w', encoding='utf-8') as f:
                    json.dump(analysis_results, f, indent=2, default=str)
                logger.info(f"🐛 Debug JSON saved: {json_filename}")
            
            logger.info(f"✅ Comprehensive analysis completed for @{user.username}")
            
        except Exception as e:
            logger.error(f"❌ Error in comprehensive analysis: {e}")
            if DEBUG_MODE:
                import traceback
                logger.error(f"❌ Full traceback: {traceback.format_exc()}")
    
    def _save_basic_info(self, output, user):
        """Save basic account information to file"""
        try:
            with open('account_info_output.txt', 'a', encoding='utf-8') as f:
                f.write(f"\n--- {datetime.now(timezone.utc).isoformat()} ---\n")
                for line in output:
                    f.write(line + "\n")
                f.write("\n")
        except Exception as e:
            logger.error(f"❌ Error saving basic info: {e}")
    
    def run_monitor(self):
        """Main monitoring loop with enhanced features"""
        logger.info("🚀 Starting Enhanced X Mention Monitor")
        logger.info(f"🎯 Monitoring for: '{MENTION_TRIGGER}'")
        logger.info(f"📊 API calls this session: {self.api_tracker.session_calls}/{MAX_API_CALLS_PER_SESSION}")
        
        if DEEP_ANALYSIS:
            logger.info("🔬 Comprehensive analysis enabled - will perform detailed profile analysis")
        
        try:
            # Authenticate
            if not self.authenticate():
                return
            
            # Fetch and process mentions
            mentions = self.fetch_mentions()
            
            if not mentions:
                logger.info("🔚 No relevant mentions found. Monitoring complete.")
                return
            
            # Process each relevant mention
            for mention, includes in mentions:
                if not self.api_tracker.can_make_call() and DEEP_ANALYSIS:
                    logger.warning("⚠️  API call limit reached. Skipping comprehensive analysis for remaining mentions.")
                
                logger.info(f"📱 Processing mention from user ID: {mention.author_id}")
                self.display_account_info(mention, includes)
                
                # Add delay between mentions to respect rate limits
                if len(mentions) > 1:
                    time.sleep(1)
            
            logger.info("✅ Enhanced monitoring session completed successfully")
            
        except KeyboardInterrupt:
            logger.info("🛑 Monitoring stopped by user")
        except Exception as e:
            logger.error(f"❌ Unexpected error in monitor: {e}")
        finally:
            # Display enhanced session summary
            self._display_session_summary()
    
    def _display_session_summary(self):
        """Display detailed session summary"""
        usage_summary = self.api_tracker.get_usage_summary()
        
        print("\n" + "="*70)
        print("📊 ENHANCED SESSION SUMMARY")
        print("="*70)
        print(f"🔥 API calls made this session: {usage_summary['session_calls']}")
        print(f"📈 Total API calls this month: {usage_summary['total_calls']}")
        print(f"💳 Estimated credits remaining: ~{usage_summary['remaining_credits']}")
        print(f"⚡ Usage efficiency: {usage_summary['efficiency_rating']}")
        
        if usage_summary['endpoint_breakdown']:
            print("\n📋 Endpoint Usage Breakdown:")
            for endpoint, count in usage_summary['endpoint_breakdown'].items():
                print(f"   └─ {endpoint}: {count} calls")
        
        # Performance metrics
        if DEEP_ANALYSIS and self.api_tracker.session_calls > 2:
            analysis_calls = self.api_tracker.session_calls - 2  # Subtract auth and mentions calls
            print(f"\n🔬 Analysis Performance:")
            print(f"   └─ Enhanced analysis calls: {analysis_calls}")
            print(f"   └─ Analysis depth: {'Deep' if analysis_calls > 1 else 'Basic'}")
        
        print("="*70)

def main():
    """Enhanced main entry point"""
    print("🤖 Enhanced X Account Mention Analyzer v2.0")
    print("🔍 Advanced monitoring with comprehensive profile analysis")
    print("💳 Optimized for API credit conservation")
    
    if TEST_MODE:
        print("🧪 RUNNING IN TEST MODE - No real API calls")
    if DEBUG_MODE:
        print("🔍 DEBUG MODE ENABLED - Verbose logging")
    if DEEP_ANALYSIS:
        print("🔬 COMPREHENSIVE ANALYSIS ENABLED - Deep profile intelligence")
        if not TEXTBLOB_AVAILABLE:
            print("⚠️ TextBlob not available - sentiment analysis will be limited")
    
    print(f"📊 Session limit: {MAX_API_CALLS_PER_SESSION} API calls")
    print()
    
    monitor = EnhancedXMentionMonitor()
    monitor.run_monitor()

if __name__ == "__main__":
    main()