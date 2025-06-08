"""
Trusted Account Cross-Check Module
=================================

Validates account credibility by checking if they're followed by trusted 
accounts from the Solana ecosystem and broader crypto community.

This module fetches the trusted accounts list from:
https://github.com/devsyrem/turst-list/blob/main/list

Author: X Analysis Bot
Version: 1.0
"""

import tweepy
import json
import time
import logging
import re
import requests
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Set, Optional, Tuple, Any
from collections import Counter

logger = logging.getLogger(__name__)

class TrustedAccountValidator:
    """Validates account credibility using trusted account followers"""
    
    def __init__(self, api_client: tweepy.Client):
        self.client = api_client
        self.trust_list_url = "https://raw.githubusercontent.com/devsyrem/turst-list/main/list"
        self.cache_file = "trust_system/trust_cache.json"
        self.cache_duration = timedelta(hours=24)  # Cache for 24 hours
        self.trusted_accounts = []
        self.trusted_user_ids = {}  # username -> user_id mapping
        self.api_calls_made = 0
        self.max_api_calls = 50  # Limit for trust validation
        
        # Category definitions for trusted accounts
        self.category_patterns = {
            'DeFi Protocol': [
                'exchange', 'protocol', 'finance', 'lending', 'swap', 'dex', 
                'yield', 'jupiter', 'raydium', 'orca', 'kamino', 'meteora',
                'drift', 'solend', 'marinade', 'jito', 'saber', 'sunny'
            ],
            'NFT/Gaming': [
                'nft', 'mad', 'magic', 'bears', 'ape', 'fox', 'backpack', 
                'tensor', 'lifinity', 'degen', 'okay', 'famous', 'cets'
            ],
            'Infrastructure': [
                'solana', 'phantom', 'explorer', 'wallet', 'labs', 'network',
                'wormhole', 'helium', 'pyth', 'solflare', 'beach', 'fm'
            ],
            'Media/Community': [
                'media', 'wordcel', 'superteam', 'dao', 'community', 'stellar',
                'bunkr', 'candy', 'bridge', 'tourism', 'meme', 'truts'
            ],
            'Key Opinion Leader': [
                'aeyakovenko', 'rajgokal', 'vinnylingham', 'tonyguoga', 'austin_federa'
            ],
            'Gaming/Metaverse': [
                'staratlas', 'grape', 'star', 'atlas', 'gaming', 'metaverse'
            ]
        }
        
    def load_trusted_accounts(self) -> bool:
        """Load and parse trusted accounts from GitHub repository"""
        try:
            logger.info("🔍 Fetching trusted accounts list from GitHub...")
            response = requests.get(self.trust_list_url, timeout=30)
            response.raise_for_status()
            
            # Parse the Python list format
            content = response.text
            logger.debug(f"📄 Raw content length: {len(content)} characters")
            
            # Extract the list from the TRUSTED_ACCOUNTS variable
            start_idx = content.find('[')
            end_idx = content.rfind(']') + 1
            
            if start_idx == -1 or end_idx == -1:
                logger.error("❌ Could not find list brackets in trusted accounts file")
                return False
            
            list_content = content[start_idx:end_idx]
            logger.debug(f"📋 Extracted list content: {len(list_content)} characters")
            
            # Extract usernames using regex to handle comments and formatting
            usernames = re.findall(r'"([^"]+)"', list_content)
            
            # Clean and validate usernames
            self.trusted_accounts = []
            for username in usernames:
                clean_username = username.strip()
                if clean_username and len(clean_username) > 0:
                    self.trusted_accounts.append(clean_username)
            
            if not self.trusted_accounts:
                logger.error("❌ No valid usernames found in trusted accounts list")
                return False
            
            logger.info(f"✅ Loaded {len(self.trusted_accounts)} trusted accounts")
            
            # Log some sample accounts for verification
            sample_accounts = self.trusted_accounts[:5]
            logger.info(f"📋 Sample accounts: {', '.join(sample_accounts)}")
            
            # Categorize accounts for better understanding
            category_counts = self._categorize_all_accounts()
            logger.info(f"📊 Categories: {dict(category_counts)}")
            
            return True
            
        except requests.RequestException as e:
            logger.error(f"❌ Network error loading trusted accounts: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error loading trusted accounts: {e}")
            return False
    
    def _categorize_all_accounts(self) -> Counter:
        """Categorize all trusted accounts and return counts"""
        categories = Counter()
        for account in self.trusted_accounts:
            category = self._categorize_account(account)
            categories[category] += 1
        return categories
    
    def resolve_usernames_to_ids(self, max_batch_size: int = 100) -> bool:
        """Convert usernames to user IDs using Twitter API"""
        try:
            logger.info("🔄 Resolving trusted account usernames to user IDs...")
            
            # Check cache first
            cached_data = self._load_cache()
            if cached_data and self._is_cache_valid(cached_data):
                self.trusted_user_ids = cached_data.get('user_ids', {})
                logger.info(f"📦 Loaded {len(self.trusted_user_ids)} user IDs from cache")
                return len(self.trusted_user_ids) > 0
            
            # Process in batches to respect API limits
            resolved_ids = {}
            failed_usernames = []
            successful_batches = 0
            
            total_batches = (len(self.trusted_accounts) + max_batch_size - 1) // max_batch_size
            
            for i in range(0, len(self.trusted_accounts), max_batch_size):
                batch_num = (i // max_batch_size) + 1
                batch = self.trusted_accounts[i:i + max_batch_size]
                
                try:
                    logger.info(f"🔍 Processing batch {batch_num}/{total_batches} ({len(batch)} accounts)")
                    
                    # API call to get user IDs
                    users = self.client.get_users(
                        usernames=batch, 
                        user_fields=['id', 'username', 'name']
                    )
                    self.api_calls_made += 1
                    
                    if users.data:
                        for user in users.data:
                            resolved_ids[user.username.lower()] = str(user.id)
                        successful_batches += 1
                        logger.info(f"✅ Resolved {len(users.data)} accounts in batch {batch_num}")
                    
                    # Track failed resolutions
                    if users.errors:
                        for error in users.errors:
                            failed_username = error.get('value', 'unknown')
                            failed_usernames.append(failed_username)
                            logger.debug(f"⚠️ Failed to resolve: @{failed_username}")
                    
                    # Rate limit protection
                    if batch_num < total_batches:
                        time.sleep(1.1)  # Slightly over 1 second to be safe
                    
                except tweepy.TooManyRequests:
                    logger.warning(f"⚠️ Rate limit hit at batch {batch_num}, waiting...")
                    time.sleep(900)  # Wait 15 minutes
                    continue
                except Exception as e:
                    logger.error(f"❌ Error resolving batch {batch_num}: {e}")
                    failed_usernames.extend(batch)
                    continue
            
            self.trusted_user_ids = resolved_ids
            
            # Save to cache
            cache_data = {
                'user_ids': resolved_ids,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'failed_usernames': failed_usernames,
                'total_accounts': len(self.trusted_accounts),
                'successful_resolutions': len(resolved_ids)
            }
            self._save_cache(cache_data)
            
            success_rate = len(resolved_ids) / len(self.trusted_accounts) * 100
            logger.info(f"✅ Resolution complete: {len(resolved_ids)}/{len(self.trusted_accounts)} usernames ({success_rate:.1f}%)")
            
            if failed_usernames:
                logger.warning(f"⚠️ Failed to resolve {len(failed_usernames)} accounts: {', '.join(failed_usernames[:5])}{'...' if len(failed_usernames) > 5 else ''}")
            
            return len(resolved_ids) > 0
            
        except Exception as e:
            logger.error(f"❌ Error resolving usernames to IDs: {e}")
            return False
    
    def check_trusted_followers(self, target_user_id: str, min_trusted_followers: int = 2) -> Dict[str, Any]:
        """
        Check if target user is followed by trusted accounts
        
        Args:
            target_user_id: Twitter user ID to check
            min_trusted_followers: Minimum trusted followers for positive validation
            
        Returns:
            Dict with validation results and detailed metrics
        """
        try:
            logger.info(f"🔍 Starting trusted followers check for user ID: {target_user_id}")
            
            if not self.trusted_user_ids:
                logger.warning("⚠️ No trusted user IDs available - attempting resolution...")
                if not self.resolve_usernames_to_ids():
                    return self._empty_validation_result("Failed to resolve trusted accounts")
            
            if self.api_calls_made >= self.max_api_calls:
                logger.warning(f"⚠️ API call limit reached ({self.max_api_calls})")
                return self._empty_validation_result("API call limit reached")
            
            # Initialize validation tracking
            trusted_followers = []
            validation_details = {
                'checked_accounts': 0,
                'api_calls_made': 0,
                'trusted_followers_found': [],
                'follower_categories': {},
                'validation_strength': 0,
                'check_method': 'follower_lookup'
            }
            
            # Strategy: Check target user's followers for trusted accounts
            # This is more efficient than checking each trusted account individually
            try:
                logger.info("📋 Fetching target user's followers...")
                
                # Get followers of target user (paginated)
                followers_checked = 0
                max_followers_to_check = 1000  # Reasonable limit
                
                for followers_page in tweepy.Paginator(
                    self.client.get_users_followers,
                    id=target_user_id,
                    max_results=1000,
                    limit=1  # Only check first 1000 followers for efficiency
                ).flatten(limit=max_followers_to_check):
                    
                    self.api_calls_made += 1
                    validation_details['api_calls_made'] += 1
                    
                    if self.api_calls_made >= self.max_api_calls:
                        logger.warning("⚠️ API limit reached during follower check")
                        break
                    
                    if followers_page:
                        followers_checked += 1
                        follower_username = followers_page.username.lower()
                        
                        # Check if this follower is in our trusted list
                        if follower_username in self.trusted_user_ids:
                            logger.info(f"✅ Found trusted follower: @{followers_page.username}")
                            
                            trusted_followers.append({
                                'username': followers_page.username,
                                'user_id': str(followers_page.id),
                                'name': getattr(followers_page, 'name', ''),
                                'category': self._categorize_account(followers_page.username)
                            })
                            
                            category = self._categorize_account(followers_page.username)
                            validation_details['follower_categories'][category] = \
                                validation_details['follower_categories'].get(category, 0) + 1
                
                validation_details['checked_accounts'] = followers_checked
                logger.info(f"📊 Checked {followers_checked} followers, found {len(trusted_followers)} trusted")
                
            except tweepy.Forbidden:
                logger.warning("⚠️ Target account is private - cannot check followers")
                return self._empty_validation_result("Target account is private")
            except tweepy.NotFound:
                logger.warning("⚠️ Target account not found")
                return self._empty_validation_result("Target account not found")
            except Exception as e:
                logger.error(f"❌ Error checking followers: {e}")
                return self._empty_validation_result(f"Error checking followers: {str(e)}")
            
            # Calculate validation metrics
            trusted_follower_count = len(trusted_followers)
            is_validated = trusted_follower_count >= min_trusted_followers
            
            # Calculate validation strength (0-100)
            validation_strength = self._calculate_validation_strength(
                trusted_follower_count, 
                validation_details['follower_categories']
            )
            
            validation_details.update({
                'trusted_followers_found': [f"@{tf['username']}" for tf in trusted_followers],
                'validation_strength': validation_strength
            })
            
            # Calculate comprehensive trust score
            trust_score = self._calculate_trust_score(trusted_followers, validation_details)
            
            result = {
                'is_validated': is_validated,
                'trusted_follower_count': trusted_follower_count,
                'min_required': min_trusted_followers,
                'validation_strength': validation_strength,
                'trusted_followers': trusted_followers,
                'validation_details': validation_details,
                'trust_score': trust_score,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'api_calls_used': validation_details['api_calls_made']
            }
            
            status = "✅ VALIDATED" if is_validated else "❌ NOT VALIDATED"
            logger.info(f"🎯 Trust validation complete: {trusted_follower_count} trusted followers → {status}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in trusted followers check: {e}")
            return self._empty_validation_result(f"Validation error: {str(e)}")
    
    def _calculate_validation_strength(self, follower_count: int, categories: Dict[str, int]) -> int:
        """Calculate validation strength score (0-100)"""
        if follower_count == 0:
            return 0
        
        # Base score from follower count (max 60 points)
        base_score = min(follower_count * 15, 60)
        
        # Category diversity bonus (max 25 points)
        category_diversity = len(categories)
        diversity_bonus = min(category_diversity * 5, 25)
        
        # High-value category bonus (max 15 points)
        high_value_bonus = 0
        if 'Key Opinion Leader' in categories:
            high_value_bonus += 10
        if 'Infrastructure' in categories:
            high_value_bonus += 5
        
        total_score = min(base_score + diversity_bonus + high_value_bonus, 100)
        return int(total_score)
    
    def _categorize_account(self, username: str) -> str:
        """Categorize trusted account by username patterns"""
        username_lower = username.lower()
        
        # Check each category
        for category, keywords in self.category_patterns.items():
            if any(keyword in username_lower for keyword in keywords):
                return category
        
        return "Other"
    
    def _calculate_trust_score(self, trusted_followers: List[Dict], validation_details: Dict) -> Dict[str, Any]:
        """Calculate detailed trust score based on follower analysis"""
        
        if not trusted_followers:
            return {
                'overall_score': 0,
                'category_scores': {},
                'trust_level': 'Unverified',
                'weighted_score': 0
            }
        
        # Category weights (higher = more valuable)
        category_weights = {
            'Key Opinion Leader': 30,
            'Infrastructure': 25,
            'DeFi Protocol': 20,
            'NFT/Gaming': 15,
            'Gaming/Metaverse': 12,
            'Media/Community': 10,
            'Other': 5
        }
        
        # Calculate weighted score
        total_weighted_score = 0
        category_scores = {}
        
        for follower in trusted_followers:
            category = follower['category']
            weight = category_weights.get(category, 5)
            total_weighted_score += weight
            category_scores[category] = category_scores.get(category, 0) + weight
        
        # Normalize to 0-100 scale
        # Max theoretical score for this number of followers
        max_possible_score = len(trusted_followers) * max(category_weights.values())
        normalized_score = min((total_weighted_score / max_possible_score) * 100, 100) if max_possible_score > 0 else 0
        
        # Determine trust level
        if normalized_score >= 80:
            trust_level = 'Highly Trusted'
        elif normalized_score >= 65:
            trust_level = 'Well Trusted'
        elif normalized_score >= 45:
            trust_level = 'Moderately Trusted'
        elif normalized_score >= 25:
            trust_level = 'Lightly Trusted'
        else:
            trust_level = 'Minimally Trusted'
        
        return {
            'overall_score': round(normalized_score, 1),
            'category_scores': category_scores,
            'trust_level': trust_level,
            'weighted_score': total_weighted_score,
            'max_possible': max_possible_score
        }
    
    def _load_cache(self) -> Optional[Dict]:
        """Load cached trusted account data"""
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
    
    def _save_cache(self, data: Dict) -> bool:
        """Save trusted account data to cache"""
        try:
            # Ensure directory exists
            import os
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            
            with open(self.cache_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug(f"💾 Cache saved: {len(data.get('user_ids', {}))} user IDs")
            return True
        except Exception as e:
            logger.error(f"❌ Error saving cache: {e}")
            return False
    
    def _is_cache_valid(self, cached_data: Dict) -> bool:
        """Check if cached data is still valid"""
        try:
            cache_timestamp = cached_data.get('timestamp')
            if not cache_timestamp:
                return False
            
            cache_time = datetime.fromisoformat(cache_timestamp.replace('Z', '+00:00'))
            age = datetime.now(timezone.utc) - cache_time
            is_valid = age < self.cache_duration
            
            if is_valid:
                logger.debug(f"📦 Cache is valid (age: {age})")
            else:
                logger.debug(f"⏰ Cache expired (age: {age})")
            
            return is_valid
        except (KeyError, ValueError, TypeError) as e:
            logger.debug(f"❌ Cache validation error: {e}")
            return False
    
    def _empty_validation_result(self, error_message: str) -> Dict[str, Any]:
        """Return empty validation result with error"""
        return {
            'is_validated': False,
            'trusted_follower_count': 0,
            'min_required': 2,
            'validation_strength': 0,
            'trusted_followers': [],
            'validation_details': {
                'error': error_message,
                'checked_accounts': 0,
                'api_calls_made': 0,
                'check_method': 'error'
            },
            'trust_score': {
                'overall_score': 0,
                'trust_level': 'Unverified',
                'weighted_score': 0
            },
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'api_calls_used': 0
        }

    def format_validation_report(self, validation_result: Dict[str, Any], username: str) -> str:
        """Format validation results for display"""
        
        if not validation_result:
            return f"""
🔒 TRUSTED ACCOUNT VALIDATION - @{username}
========================================
❌ Validation Error: No validation data available
"""
        
        error_msg = validation_result.get('validation_details', {}).get('error')
        if error_msg:
            return f"""
🔒 TRUSTED ACCOUNT VALIDATION - @{username}
========================================
❌ Validation Error: {error_msg}
📊 API Calls Used: {validation_result.get('api_calls_used', 0)}
"""
        
        is_validated = validation_result.get('is_validated', False)
        trusted_count = validation_result.get('trusted_follower_count', 0)
        min_required = validation_result.get('min_required', 2)
        validation_strength = validation_result.get('validation_strength', 0)
        trust_score = validation_result.get('trust_score', {})
        
        status_emoji = "✅" if is_validated else "❌"
        status_text = "VALIDATED" if is_validated else "NOT VALIDATED"
        
        output = f"""
🔒 TRUSTED ACCOUNT VALIDATION - @{username}
========================================
{status_emoji} Status: {status_text}
🎯 Trusted Followers: {trusted_count}/{min_required} minimum required
💪 Validation Strength: {validation_strength}/100
🏆 Trust Level: {trust_score.get('trust_level', 'Unknown')}
⭐ Trust Score: {trust_score.get('overall_score', 0)}/100
"""
        
        # Show trusted followers if any found
        trusted_followers = validation_result.get('trusted_followers', [])
        if trusted_followers:
            output += "\n👥 TRUSTED FOLLOWERS FOUND:\n"
            for follower in trusted_followers[:10]:  # Show first 10
                output += f"   └─ @{follower['username']} ({follower['category']})\n"
            
            if len(trusted_followers) > 10:
                output += f"   └─ ... and {len(trusted_followers) - 10} more\n"
        
        # Show category breakdown
        follower_categories = validation_result.get('validation_details', {}).get('follower_categories', {})
        if follower_categories:
            output += "\n📊 CATEGORY BREAKDOWN:\n"
            for category, count in sorted(follower_categories.items(), key=lambda x: x[1], reverse=True):
                output += f"   └─ {category}: {count} follower{'s' if count != 1 else ''}\n"
        
        # Show validation stats
        validation_details = validation_result.get('validation_details', {})
        api_calls = validation_result.get('api_calls_used', 0)
        checked_accounts = validation_details.get('checked_accounts', 0)
        
        output += f"\n📈 Validation Stats:\n"
        output += f"   └─ Followers checked: {checked_accounts:,}\n"
        output += f"   └─ API calls used: {api_calls}\n"
        output += f"   └─ Check method: {validation_details.get('check_method', 'unknown')}\n"
        
        return output

    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status and statistics"""
        cache_data = self._load_cache()
        
        status = {
            'trusted_accounts_loaded': len(self.trusted_accounts),
            'user_ids_resolved': len(self.trusted_user_ids),
            'api_calls_made': self.api_calls_made,
            'api_calls_remaining': max(0, self.max_api_calls - self.api_calls_made),
            'cache_status': 'valid' if cache_data and self._is_cache_valid(cache_data) else 'invalid',
            'last_cache_update': cache_data.get('timestamp', 'Never') if cache_data else 'Never',
            'system_ready': len(self.trusted_user_ids) > 0
        }
        
        if cache_data:
            status['cache_stats'] = {
                'total_accounts': cache_data.get('total_accounts', 0),
                'successful_resolutions': cache_data.get('successful_resolutions', 0),
                'failed_resolutions': len(cache_data.get('failed_usernames', []))
            }
        
        return status

    def initialize_system(self) -> bool:
        """Initialize the complete trusted account system"""
        try:
            logger.info("🚀 Initializing Trusted Account Validation System...")
            
            # Step 1: Load trusted accounts list
            if not self.load_trusted_accounts():
                logger.error("❌ Failed to load trusted accounts list")
                return False
            
            # Step 2: Resolve usernames to IDs
            if not self.resolve_usernames_to_ids():
                logger.error("❌ Failed to resolve usernames to user IDs")
                return False
            
            logger.info("✅ Trusted Account Validation System initialized successfully")
            
            # Log system status
            status = self.get_system_status()
            logger.info(f"📊 System ready: {status['user_ids_resolved']}/{status['trusted_accounts_loaded']} accounts resolved")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error initializing trusted account system: {e}")
            return False