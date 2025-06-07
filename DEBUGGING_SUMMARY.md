# X Mention Monitor - Complete Debugging & Output Summary 🔍

This document provides a comprehensive overview of all outputs, debugging information, and troubleshooting details for the X Account Mention Analyzer.

## 📋 Script Overview

The X Mention Monitor efficiently tracks mentions of `@satyvm acc` on X (Twitter) while preserving your limited API credits (60/month for free tier).

### Key Features
- **API Credit Conservation**: Maximum 5 calls per session
- **Smart Filtering**: Only processes relevant mentions
- **Comprehensive Logging**: Every action is logged
- **Persistent Tracking**: Remembers last processed tweet
- **Error Recovery**: Handles rate limits and failures gracefully

## 📁 Generated Files & Their Contents

### 1. `x_monitor.log` - Execution Log
**Purpose**: Complete execution history with timestamps

**Sample Content**:
```
2025-06-08 02:42:19,075 - INFO - 📊 API Usage loaded - Total calls this month: 2
2025-06-08 02:42:19,075 - INFO - 📖 Last seen tweet ID: 1931101178504663103
2025-06-08 02:42:19,075 - INFO - 🚀 Starting X Mention Monitor
2025-06-08 02:42:19,075 - INFO - 🎯 Monitoring for: '@satyvm acc'
2025-06-08 02:42:19,075 - INFO - 📊 API calls this session: 0/5
2025-06-08 02:42:19,075 - INFO - 🔐 Authenticating with X API...
2025-06-08 02:42:19,391 - INFO - 🔥 API CALL: get_me (Cost: 1) - Session: 1/5, Total: 3
2025-06-08 02:42:19,393 - INFO - ✅ Successfully authenticated as @satyvm
```

**Log Levels**:
- `INFO`: Normal operations
- `WARNING`: Rate limits, API limits reached
- `ERROR`: Authentication failures, API errors

### 2. `api_usage.json` - API Credit Tracking
**Purpose**: Track API usage to stay within monthly limits

**Sample Content**:
```json
{
  "total_calls": 3,
  "daily_calls": {
    "2025-06-07": 3
  },
  "last_reset": "2025-06-07T21:06:09.013447+00:00"
}
```

**Fields Explained**:
- `total_calls`: Total API calls this month
- `daily_calls`: Breakdown by date
- `last_reset`: When tracking was last reset

### 3. `last_seen_id.txt` - Tweet Tracking
**Purpose**: Prevent reprocessing old mentions

**Sample Content**:
```
1931101178504663103
```

This stores the ID of the most recently processed tweet.

### 4. `account_info_output.txt` - Account Information
**Purpose**: Complete record of all detected account information

**Sample Content**:
```
--- 2025-06-07T21:12:19.394314+00:00 ---

============================================================
🎯 NEW MENTION DETECTED!
============================================================
👤 Username: @testuser123
📛 Display Name: Test User
📝 Bio: This is a test user account for debugging
📍 Location: Test City, Test State
👥 Followers: 150
➡️  Following: 200
📊 Tweets: 500
❤️  Listed: 5
🔗 Profile URL: https://twitter.com/testuser123
🖼️  Profile Image: https://example.com/avatar.jpg
💬 Mention Text: Hey @satyvm acc can you help me with this?
⏰ Posted: 2025-06-07 21:12:19.393413+00:00
🔢 Tweet ID: 1234567890123456789
============================================================
```

Each entry includes timestamp and complete user information.

## 🎮 Running Modes

### 1. Production Mode
```bash
python run.py
```
- Makes real API calls
- Processes actual mentions
- Uses API credits

### 2. Test Mode
```bash
python run.py --test
```
- No API calls made
- Uses mock data
- Safe for testing

### 3. Debug Mode
```bash
python run.py --debug
```
- Verbose logging
- Full error tracebacks
- Detailed execution info

### 4. Combined Mode
```bash
python run.py --test --debug
```
- Test mode + verbose logging
- Perfect for development

## 📊 Console Output Examples

### Successful Run (Test Mode)
```
🤖 X Account Mention Analyzer
==================================================
🔍 Running pre-flight checks...
📊 API Usage: 3/60 calls used this month (57 remaining)
✅ All checks passed!

🧪 Running in TEST MODE - No real API calls will be made
🔍 Running in DEBUG MODE - Verbose logging enabled
🚀 Starting X mention monitor...

🤖 X Account Mention Analyzer
🔍 Efficiently monitoring for '@satyvm acc' mentions
💳 Optimized for minimal API credit usage
🧪 RUNNING IN TEST MODE - No real API calls
🔍 DEBUG MODE ENABLED - Verbose logging

============================================================
🎯 NEW MENTION DETECTED!
============================================================
👤 Username: @testuser123
📛 Display Name: Test User
📝 Bio: This is a test user account for debugging
📍 Location: Test City, Test State
👥 Followers: 150
➡️  Following: 200
📊 Tweets: 500
❤️  Listed: 5
🔗 Profile URL: https://twitter.com/testuser123
🖼️  Profile Image: https://example.com/avatar.jpg
💬 Mention Text: Hey @satyvm acc can you help me with this?
⏰ Posted: 2025-06-07 21:12:19.393413+00:00
🔢 Tweet ID: 1234567890123456789
============================================================

==================================================
📊 SESSION SUMMARY
==================================================
🔥 API calls made this session: 1
📈 Total API calls this month: 3
💳 Estimated credits remaining: ~57
==================================================

✅ Monitor completed successfully!
```

### No Mentions Found
```
🔍 Fetching mentions for user ID: 912363642154127361
🔍 Looking for trigger phrase: '@satyvm acc'
🔍 Since tweet ID: 1931101178504663103
📭 No new mentions found
🔚 No relevant mentions found. Monitoring complete.
```

### Rate Limit Encountered
```
❌ Rate limit exceeded: 429 Too Many Requests
💤 Implementing exponential backoff...
⏰ Waiting 60 seconds before retry...
```

## 🚨 Error Scenarios & Debugging

### 1. Authentication Errors
**Error**: `❌ Unauthorized: 401 Unauthorized`

**Debugging Steps**:
1. Check `.env` file exists
2. Verify all API credentials are correct
3. Ensure no extra spaces in credentials
4. Check API key permissions on X Developer Portal

**Log Entry**:
```
2025-06-08 02:42:19,075 - ERROR - ❌ Unauthorized: 401 Unauthorized
2025-06-08 02:42:19,075 - ERROR - 🔑 Check your API credentials
```

### 2. Rate Limit Issues
**Error**: `❌ Rate limit exceeded`

**Debugging Steps**:
1. Wait for rate limit reset (15 minutes)
2. Reduce `MAX_API_CALLS_PER_SESSION`
3. Run less frequently

**Log Entry**:
```
2025-06-08 02:36:09,606 - WARNING - Rate limit exceeded. Sleeping for 551 seconds.
```

### 3. Missing Dependencies
**Error**: `❌ Missing dependency: No module named 'tweepy'`

**Solution**:
```bash
uv sync
# or
pip install tweepy python-dotenv
```

### 4. No Mentions Found
**Output**: `📭 No new mentions found`

**Explanation**: This is normal - means no one mentioned you with the trigger phrase since last run.

## 🔧 Configuration Debugging

### Environment Variables Check
```bash
python run.py --status
```

This shows:
- Current API usage
- Remaining credits
- Configuration status

### Manual File Inspection
```bash
# Check API usage
cat api_usage.json

# Check last processed tweet
cat last_seen_id.txt

# Check recent logs
tail -20 x_monitor.log

# Check found accounts
cat account_info_output.txt
```

## 📈 API Usage Optimization

### Current Strategy
- **Authentication**: 1 API call per session
- **Fetch mentions**: 1 API call per session
- **Total per session**: 2 API calls maximum
- **Session limit**: 5 API calls (safety buffer)

### Monthly Planning
With 60 credits/month:
- **Conservative**: 20 sessions/month (40 credits)
- **Normal**: 25 sessions/month (50 credits)
- **Aggressive**: 30 sessions/month (60 credits)

### Recommended Schedule
```bash
# Every 6 hours = 4 times/day = 120 times/month = too many
# Every 12 hours = 2 times/day = 60 times/month = maximum safe
# Every 24 hours = 1 time/day = 30 times/month = very safe

# Recommended: 2-3 times per day
0 8,16 * * * cd /path/to/x-analysis-bot && python run.py
```

## 🔍 Troubleshooting Checklist

### Pre-flight Checks
- [ ] Dependencies installed (`uv sync`)
- [ ] `.env` file exists with all credentials
- [ ] API keys have correct permissions
- [ ] Not hitting rate limits

### During Execution
- [ ] Authentication successful
- [ ] API usage within limits
- [ ] Mentions being fetched
- [ ] Filtering working correctly

### Post-execution
- [ ] Files updated correctly
- [ ] API usage tracked
- [ ] Account info saved
- [ ] Logs written

## 🧪 Testing Workflow

### 1. Initial Setup Test
```bash
python run.py --test --debug
```
Should show mock mention detection.

### 2. Authentication Test
```bash
python run.py --debug
```
Should authenticate successfully (uses 1 API call).

### 3. Production Test
```bash
python run.py
```
Full production run.

### 4. Status Check
```bash
python run.py --status
```
Show current API usage.

## 📱 Production Deployment

### Recommended Cron Schedule
```bash
# Edit crontab
crontab -e

# Add this line for twice daily monitoring
0 9,21 * * * cd /path/to/x-analysis-bot && python run.py >> cron.log 2>&1
```

### Monitoring Commands
```bash
# Check if script is working
tail -f x_monitor.log

# Check API usage
python run.py --status

# View recent account detections
tail -20 account_info_output.txt
```

## 🎯 Success Metrics

### Healthy Operation
- API usage stays under 60/month
- Regular successful authentications
- Mentions processed when they occur
- No repeated errors in logs

### Warning Signs
- API usage approaching 60
- Frequent rate limit errors
- Authentication failures
- Missing mention detections

## 💡 Optimization Tips

1. **Run 2-3 times per day** maximum
2. **Use test mode** for development
3. **Monitor API usage** regularly
4. **Check logs** for errors
5. **Backup important files** (`api_usage.json`, `last_seen_id.txt`)

---

**🚀 The script is now optimized for your 60 API credit limit and provides comprehensive debugging information for any issues that may arise!**