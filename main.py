import tweepy
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Your X API Credentials (loaded from .env file) ---
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
API_KEY = os.getenv("API_KEY")
API_KEY_SECRET = os.getenv("API_KEY_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

# The user ID of your X account (@satyvm)
YOUR_USER_ID = os.getenv("YOUR_SATYVM_USER_ID")

# The specific text to look for in the mention
MENTION_TRIGGER = "@satyvm acc"

# File to store the ID of the last processed tweet
LAST_SEEN_ID_FILE = "last_seen_id.txt"

def read_last_seen_id():
    """Reads the ID of the last seen tweet from a file."""
    if not os.path.exists(LAST_SEEN_ID_FILE):
        return None
    with open(LAST_SEEN_ID_FILE, "r") as f:
        last_seen_id = f.read().strip()
        return int(last_seen_id) if last_seen_id else None

def write_last_seen_id(tweet_id):
    """Writes the ID of the latest tweet to a file."""
    with open(LAST_SEEN_ID_FILE, "w") as f:
        f.write(str(tweet_id))

def main():
    """
    Checks for new mentions and displays account info
    for those containing the trigger phrase.
    """
    # Check if credentials are loaded
    if not all([BEARER_TOKEN, API_KEY, API_KEY_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, YOUR_USER_ID]):
        print("Error: One or more environment variables are not set.")
        print("Please check your .env file.")
        return

    try:
        # Authenticate with the X API v2
        client = tweepy.Client(
            bearer_token=BEARER_TOKEN,
            consumer_key=API_KEY,
            consumer_secret=API_KEY_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_TOKEN_SECRET
        )
        print("Successfully authenticated with X API.")
        print("Checking for new mentions...")

        last_seen_id = read_last_seen_id()

        # Fetch mentions since the last seen tweet
        mentions = client.get_users_mentions(
            id=YOUR_USER_ID,
            since_id=last_seen_id,
            tweet_fields=["created_at"],
            expansions=["author_id"]
        )

        # This counts as 1 API call

        if not mentions.data:
            print("No new mentions found containing the trigger phrase.")
            return

        new_last_seen_id = mentions.meta.get('newest_id')
        if new_last_seen_id:
            write_last_seen_id(new_last_seen_id)

        for mention in mentions.data:
            if MENTION_TRIGGER.lower() in mention.text.lower():
                author_id = mention.author_id

                # Fetch the profile of the user who mentioned you
                # This counts as a second API call per relevant mention
                user_info = client.get_user(
                    id=author_id,
                    user_fields=["profile_image_url", "public_metrics", "description", "location"]
                )

                if user_info.data:
                    user = user_info.data
                    print("\n" + "="*40)
                    print(f"✅ New mention found from: @{user.username}")
                    print(f"   Name: {user.name}")
                    print(f"   Bio: {user.description}")
                    print(f"   Location: {user.location}")
                    print(f"   Followers: {user.public_metrics.get('followers_count')}")
                    print(f"   Following: {user.public_metrics.get('following_count')}")
                    print(f"   Tweet count: {user.public_metrics.get('tweet_count')}")
                    print(f"   Profile URL: https://twitter.com/{user.username}")
                    print("="*40 + "\n")

    except tweepy.errors.TweepyException as e:
        print(f"An error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
