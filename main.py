import tweepy
import time
import os
import json
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Setup detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('x_monitor.log'),
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
API_USAGE_FILE = "api_usage.json"
MAX_API_CALLS_PER_SESSION = 5  # Conservative limit to preserve credits
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"

class APIUsageTracker:
    """Track API usage to stay within credit limits"""
    
    def __init__(self):
        self.usage_file = API_USAGE_FILE
        self.session_calls = 0
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
                    "last_reset": datetime.now(timezone.utc).isoformat()
                }
            logger.info(f"📊 API Usage loaded - Total calls this month: {self.usage_data.get('total_calls', 0)}")
        except Exception as e:
            logger.error(f"❌ Error loading API usage data: {e}")
            self.usage_data = {"total_calls": 0, "daily_calls": {}}
    
    def record_api_call(self, endpoint_name, cost=1):
        """Record an API call"""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        self.session_calls += cost
        self.usage_data["total_calls"] = self.usage_data.get("total_calls", 0) + cost
        
        if today not in self.usage_data["daily_calls"]:
            self.usage_data["daily_calls"][today] = 0
        self.usage_data["daily_calls"][today] += cost
        
        logger.info(f"🔥 API CALL: {endpoint_name} (Cost: {cost}) - Session: {self.session_calls}/{MAX_API_CALLS_PER_SESSION}, Total: {self.usage_data['total_calls']}")
        
        self.save_usage_data()
        
        if self.session_calls >= MAX_API_CALLS_PER_SESSION:
            logger.warning(f"⚠️  Session API limit reached ({MAX_API_CALLS_PER_SESSION}). Stopping to preserve credits.")
            return False
        return True
    
    def save_usage_data(self):
        """Save usage data to file"""
        try:
            with open(self.usage_file, 'w') as f:
                json.dump(self.usage_data, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Error saving API usage data: {e}")
    
    def can_make_call(self):
        """Check if we can make another API call"""
        return self.session_calls < MAX_API_CALLS_PER_SESSION

class XMentionMonitor:
    """Efficient X/Twitter mention monitor with minimal API usage"""
    
    def __init__(self):
        self.api_tracker = APIUsageTracker()
        self.client = None
        self.last_seen_id = self.read_last_seen_id()
        
    def authenticate(self):
        """Authenticate with X API"""
        logger.info("🔐 Authenticating with X API...")
        
        if not all([BEARER_TOKEN, API_KEY, API_KEY_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, YOUR_USER_ID]):
            logger.error("❌ Missing API credentials. Check your .env file.")
            logger.error("Required variables: BEARER_TOKEN, API_KEY, API_KEY_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, YOUR_USER_ID")
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
            
            # Test authentication with minimal API call
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
        """Fetch new mentions efficiently"""
        if TEST_MODE:
            return self.get_test_mentions()
        
        if not self.api_tracker.can_make_call():
            logger.warning("⚠️  Cannot fetch mentions - API call limit reached")
            return []
        
        try:
            logger.info(f"🔍 Fetching mentions for user ID: {YOUR_USER_ID}")
            logger.info(f"🔍 Looking for trigger phrase: '{MENTION_TRIGGER}'")
            logger.info(f"🔍 Since tweet ID: {self.last_seen_id}")
            
            # Fetch mentions with optimized parameters
            params = {
                'id': YOUR_USER_ID,
                'tweet_fields': ['created_at', 'author_id', 'public_metrics', 'in_reply_to_user_id', 'referenced_tweets'],
                'expansions': ['author_id', 'in_reply_to_user_id', 'referenced_tweets.id.author_id'],
                'user_fields': ['username', 'name', 'description', 'location', 'public_metrics', 'profile_image_url'],
                'max_results': 5  # Reduced to save credits
            }
            
            if self.last_seen_id:
                params['since_id'] = self.last_seen_id
            
            mentions = self.client.get_users_mentions(**params)
            
            # Record API call but don't stop on rate limit during this call
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
                    # Check if this is a reply to someone else's tweet
                    if hasattr(mention, 'in_reply_to_user_id') and mention.in_reply_to_user_id:
                        logger.info(f"🔄 Found reply mention - Original tweet author ID: {mention.in_reply_to_user_id}")
                        logger.info(f"📝 Reply from user ID: {mention.author_id}")
                    else:
                        logger.info(f"🎯 Found direct mention from user ID: {mention.author_id}")
                    relevant_mentions.append((mention, mentions.includes))
                else:
                    logger.info(f"⏭️  Mention doesn't contain trigger phrase")
            
            return relevant_mentions
            
        except tweepy.TooManyRequests as e:
            logger.error(f"❌ Rate limit exceeded: {e}")
            logger.info("💤 Implementing exponential backoff...")
            wait_time = 60  # Start with 1 minute
            logger.info(f"⏰ Waiting {wait_time} seconds before retry...")
            time.sleep(wait_time)
            return []
        except tweepy.Forbidden as e:
            logger.error(f"❌ Access forbidden: {e}")
            logger.error("🔑 Check if your API keys have the correct permissions")
            return []
        except tweepy.Unauthorized as e:
            logger.error(f"❌ Unauthorized: {e}")
            logger.error("🔑 Check your API credentials")
            return []
        except Exception as e:
            logger.error(f"❌ Error fetching mentions: {e}")
            logger.error(f"❌ Error type: {type(e).__name__}")
            if DEBUG_MODE:
                import traceback
                logger.error(f"❌ Full traceback: {traceback.format_exc()}")
            return []
    
    def get_test_mentions(self):
        """Generate test mentions for testing without API calls"""
        logger.info("🧪 TEST MODE: Generating mock mentions")
        
        # Create mock mention and user data
        class MockMention:
            def __init__(self, is_reply=False):
                self.id = "1234567890123456789"
                if is_reply:
                    self.text = "I agree! @satyvm acc what do you think about this?"
                    self.author_id = "987654321098765432"  # Replier
                    self.in_reply_to_user_id = "555666777888999000"  # Original tweet author
                else:
                    self.text = "Hey @satyvm acc can you help me with this?"
                    self.author_id = "987654321098765432"
                    self.in_reply_to_user_id = None
                self.created_at = datetime.now(timezone.utc)
        
        class MockUser:
            def __init__(self, user_type="replier"):
                if user_type == "original":
                    self.id = "555666777888999000"
                    self.username = "original_poster"
                    self.name = "Original Tweet Author"
                    self.description = "I posted the original tweet that got a reply with @satyvm mention"
                    self.location = "Original City, State"
                    self.profile_image_url = "https://example.com/original_avatar.jpg"
                    self.public_metrics = {
                        'followers_count': 1250,
                        'following_count': 300,
                        'tweet_count': 1500,
                        'listed_count': 25
                    }
                else:  # replier
                    self.id = "987654321098765432"
                    self.username = "testuser123"
                    self.name = "Test Replier"
                    self.description = "This is a test user account who replied to a tweet"
                    self.location = "Test City, Test State"
                    self.profile_image_url = "https://example.com/avatar.jpg"
                    self.public_metrics = {
                        'followers_count': 150,
                        'following_count': 200,
                        'tweet_count': 500,
                        'listed_count': 5
                    }
        
        # Create both direct mention and reply mention for testing
        mock_mention = MockMention(is_reply=True)  # Test reply scenario
        mock_replier = MockUser("replier")
        mock_original_author = MockUser("original")
        mock_includes = {'users': [mock_replier, mock_original_author]}
        
        logger.info("🧪 Generated 1 test reply mention containing trigger phrase")
        return [(mock_mention, mock_includes)]
    
    def display_account_info(self, mention, includes):
        """Display detailed account information"""
        try:
            # Determine which user to show info for
            target_user_id = mention.author_id  # Default to mention author
            mention_type = "Direct mention"
            
            # If this is a reply to someone else's tweet, show the original tweet author's info
            if hasattr(mention, 'in_reply_to_user_id') and mention.in_reply_to_user_id:
                target_user_id = mention.in_reply_to_user_id
                mention_type = "Reply to original tweet author"
                logger.info(f"🔄 Reply detected - showing original tweet author info (ID: {target_user_id})")
            else:
                logger.info(f"💬 Direct mention - showing mention author info (ID: {target_user_id})")
            
            # Find the target user in includes
            author = None
            if includes and 'users' in includes:
                for user in includes['users']:
                    if hasattr(user, 'id') and str(user.id) == str(target_user_id):
                        author = user
                        break
            
            if not author:
                logger.error(f"❌ Could not find user information for target user ID: {target_user_id}")
                logger.error(f"❌ Available user IDs in response: {[getattr(u, 'id', 'no-id') for u in includes.get('users', [])] if includes else 'No includes'}")
                if DEBUG_MODE:
                    logger.debug(f"Available users in includes: {includes}")
                return
            
            # Display comprehensive account info
            output = []
            output.append("\n" + "="*60)
            output.append("🎯 NEW MENTION DETECTED!")
            output.append("="*60)
            output.append(f"📋 Type: {mention_type}")
            if mention_type.startswith("Reply"):
                output.append(f"👥 Replier: User ID {mention.author_id}")
                output.append(f"📄 Showing: Original tweet author details")
            output.append(f"👤 Username: @{getattr(author, 'username', 'N/A')}")
            output.append(f"📛 Display Name: {getattr(author, 'name', 'N/A')}")
            output.append(f"📝 Bio: {getattr(author, 'description', None) or 'No bio available'}")
            output.append(f"📍 Location: {getattr(author, 'location', None) or 'Not specified'}")
            
            if hasattr(author, 'public_metrics'):
                metrics = author.public_metrics
                output.append(f"👥 Followers: {metrics.get('followers_count', 'N/A'):,}")
                output.append(f"➡️  Following: {metrics.get('following_count', 'N/A'):,}")
                output.append(f"📊 Tweets: {metrics.get('tweet_count', 'N/A'):,}")
                output.append(f"❤️  Listed: {metrics.get('listed_count', 'N/A'):,}")
            
            output.append(f"🔗 Profile URL: https://twitter.com/{getattr(author, 'username', 'unknown')}")
            output.append(f"🖼️  Profile Image: {getattr(author, 'profile_image_url', 'N/A')}")
            output.append(f"💬 Mention Text: {mention.text}")
            output.append(f"⏰ Posted: {mention.created_at}")
            output.append(f"🔢 Tweet ID: {mention.id}")
            output.append("="*60 + "\n")
            
            # Print all output
            for line in output:
                print(line)
            
            # Also save to file for debugging
            with open('account_info_output.txt', 'a', encoding='utf-8') as f:
                f.write(f"\n--- {datetime.now(timezone.utc).isoformat()} ---\n")
                for line in output:
                    f.write(line + "\n")
                f.write("\n")
            
            # Log the detection
            logger.info(f"✅ Successfully displayed info for @{getattr(author, 'username', 'unknown')}")
            
        except Exception as e:
            logger.error(f"❌ Error displaying account info: {e}")
            if DEBUG_MODE:
                import traceback
                logger.error(f"❌ Full traceback: {traceback.format_exc()}")
    
    def run_monitor(self):
        """Main monitoring loop"""
        logger.info("🚀 Starting X Mention Monitor")
        logger.info(f"🎯 Monitoring for: '{MENTION_TRIGGER}'")
        logger.info(f"📊 API calls this session: {self.api_tracker.session_calls}/{MAX_API_CALLS_PER_SESSION}")
        
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
                if not self.api_tracker.can_make_call():
                    logger.warning("⚠️  API call limit reached. Stopping processing.")
                    break
                
                logger.info(f"📱 Processing mention from user ID: {mention.author_id}")
                self.display_account_info(mention, includes)
            
            logger.info("✅ Monitoring session completed successfully")
            
        except KeyboardInterrupt:
            logger.info("🛑 Monitoring stopped by user")
        except Exception as e:
            logger.error(f"❌ Unexpected error in monitor: {e}")
        finally:
            # Display session summary
            print("\n" + "="*50)
            print("📊 SESSION SUMMARY")
            print("="*50)
            print(f"🔥 API calls made this session: {self.api_tracker.session_calls}")
            print(f"📈 Total API calls this month: {self.api_tracker.usage_data.get('total_calls', 0)}")
            print(f"💳 Estimated credits remaining: ~{60 - self.api_tracker.usage_data.get('total_calls', 0)}")
            print("="*50)

def main():
    """Main entry point"""
    print("🤖 X Account Mention Analyzer")
    print("🔍 Efficiently monitoring for '@satyvm acc' mentions")
    print("💳 Optimized for minimal API credit usage")
    
    if TEST_MODE:
        print("🧪 RUNNING IN TEST MODE - No real API calls")
    if DEBUG_MODE:
        print("🔍 DEBUG MODE ENABLED - Verbose logging")
    print()
    
    monitor = XMentionMonitor()
    monitor.run_monitor()

if __name__ == "__main__":
    main()