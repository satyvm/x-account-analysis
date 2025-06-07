# X Account Mention Analyzer 🤖

An efficient Python script that monitors X (Twitter) mentions for specific trigger phrases and displays detailed account information. Designed specifically for **free tier X API accounts** with limited credits (60 per month).

## 🎯 What it Does

- Monitors your X account for mentions containing `@satyvm acc`
- Displays comprehensive account information for users who mention you
- **Minimizes API usage** to preserve your limited free tier credits
- Provides detailed logging and debugging information
- Saves all outputs to files for later review

## 📋 Prerequisites

- Python 3.12+
- X Developer Account with API access
- Free tier provides 60 API calls per month

## 🔧 Setup Instructions

### 1. Install Dependencies

```bash
# Navigate to the project directory
cd x-analysis-bot

# Install dependencies using uv
uv sync

# Or if you prefer pip
pip install tweepy python-dotenv
```

### 2. Configure API Credentials

The `.env` file contains your X API credentials. **Never share these publicly!**

```env
BEARER_TOKEN="your_bearer_token_here"
API_KEY="your_api_key_here"
API_KEY_SECRET="your_api_key_secret_here"
ACCESS_TOKEN="your_access_token_here"
ACCESS_TOKEN_SECRET="your_access_token_secret_here"
YOUR_SATYVM_USER_ID="your_user_id_here"
```

### 3. Get Your X API Credentials

1. Go to [X Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Create a new app or use existing one
3. Generate your API keys and tokens
4. Update the `.env` file with your credentials

## 🚀 Usage

### Basic Usage (Production)

```bash
# Run the monitor once
uv run python main.py

# Or with regular python
python main.py
```

### Test Mode (No API Calls)

```bash
# Set TEST_MODE=true in .env file, then run
uv run python main.py
```

### Debug Mode (Verbose Logging)

```bash
# Set DEBUG_MODE=true in .env file for detailed logs
uv run python main.py
```

## 📊 API Credit Management

The script is optimized for **minimal API usage**:

- **Maximum 5 API calls per session** (configurable)
- **Tracks total monthly usage** to stay within 60 credit limit
- **Intelligent rate limit handling** with exponential backoff
- **Comprehensive usage reporting** after each session

### API Call Breakdown
- Authentication: 1 call
- Fetch mentions: 1 call
- **Total per session: 2 calls** (if mentions found)

## 🎯 Features

### Smart Mention Detection
- Only processes mentions containing `@satyvm acc`
- Remembers last processed tweet to avoid duplicates
- Filters out irrelevant mentions to save API calls

### Comprehensive Account Info
- Username and display name
- Bio and location
- Follower/following counts
- Tweet count and engagement metrics
- Profile image URL
- Direct profile link

### Robust Error Handling
- Rate limit detection and handling
- Authentication error recovery
- Network error resilience
- Detailed error logging

## 📁 Generated Files

The script creates several files for tracking and debugging:

```
x-analysis-bot/
├── last_seen_id.txt       # Last processed tweet ID
├── api_usage.json         # API usage tracking
├── x_monitor.log          # Detailed execution logs
└── account_info_output.txt # All detected account info
```

### File Descriptions

- **`last_seen_id.txt`**: Prevents reprocessing old mentions
- **`api_usage.json`**: Tracks API calls to stay within limits
- **`x_monitor.log`**: Complete execution log with timestamps
- **`account_info_output.txt`**: All account information found

## 🔍 Sample Output

When a mention is detected:

```
============================================================
🎯 NEW MENTION DETECTED!
============================================================
👤 Username: @username123
📛 Display Name: John Doe
📝 Bio: Software developer and tech enthusiast
📍 Location: San Francisco, CA
👥 Followers: 1,234
➡️  Following: 567
📊 Tweets: 2,890
❤️  Listed: 12
🔗 Profile URL: https://twitter.com/username123
🖼️  Profile Image: https://pbs.twimg.com/profile_images/...
💬 Mention Text: Hey @satyvm acc can you help me with this issue?
⏰ Posted: 2025-06-07 21:30:45+00:00
🔢 Tweet ID: 1234567890123456789
============================================================
```

## 📊 Session Summary

After each run:

```
==================================================
📊 SESSION SUMMARY
==================================================
🔥 API calls made this session: 2
📈 Total API calls this month: 15
💳 Estimated credits remaining: ~45
==================================================
```

## 🛠️ Configuration Options

### Environment Variables

```env
# Required API credentials
BEARER_TOKEN="..."
API_KEY="..."
API_KEY_SECRET="..."
ACCESS_TOKEN="..."
ACCESS_TOKEN_SECRET="..."
YOUR_SATYVM_USER_ID="..."

# Optional settings
TEST_MODE="false"          # Enable test mode (no API calls)
DEBUG_MODE="false"         # Enable verbose logging
```

### Script Configuration

Edit `main.py` to modify:

```python
MENTION_TRIGGER = "@satyvm acc"           # Text to look for
MAX_API_CALLS_PER_SESSION = 5           # API call limit per run
```

## 🚨 Important Considerations

### Free Tier Limits
- **60 API calls per month** maximum
- **Rate limits**: 75 requests per 15-minute window
- **Tweet cap**: 25 tweets per 24 hours

### Best Practices
1. **Run periodically** rather than continuously
2. **Monitor API usage** regularly via logs
3. **Use test mode** for development
4. **Keep credentials secure** - never commit `.env` to git

### Troubleshooting

#### Rate Limit Errors
```
❌ Rate limit exceeded: 429 Too Many Requests
💤 Implementing exponential backoff...
⏰ Waiting 60 seconds before retry...
```
**Solution**: Wait and try again later

#### Authentication Errors
```
❌ Unauthorized: 401 Unauthorized
🔑 Check your API credentials
```
**Solution**: Verify your API keys in `.env`

#### No Mentions Found
```
📭 No new mentions found
```
**Solution**: Normal - no one mentioned you with the trigger phrase

## 📱 Running in Production

### Cron Job Setup (Linux/Mac)
```bash
# Run every hour
0 * * * * cd /path/to/x-analysis-bot && uv run python main.py

# Run every 6 hours (more conservative)
0 */6 * * * cd /path/to/x-analysis-bot && uv run python main.py
```

### Manual Monitoring
```bash
# Check when someone might have mentioned you
uv run python main.py
```

## 📈 Monitoring API Usage

### Check Current Usage
```bash
# View usage summary
cat api_usage.json

# View recent logs
tail -20 x_monitor.log
```

### Monthly Reset
The script automatically tracks monthly usage. On the 1st of each month, your API credits reset to 60.

## 🤝 Support

If you encounter issues:

1. **Check logs**: `x_monitor.log` contains detailed error information
2. **Verify credentials**: Ensure `.env` file has correct API keys
3. **Test mode**: Use `TEST_MODE=true` to test without API calls
4. **Debug mode**: Use `DEBUG_MODE=true` for verbose logging

## 📄 License

This project is for personal use. Ensure compliance with X API Terms of Service.

---

**💡 Pro Tip**: Run the script 2-3 times per day to stay well within your API limits while catching mentions promptly!