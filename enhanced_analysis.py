"""
Enhanced Comprehensive X/Twitter Account Analysis Module
======================================================

This module provides advanced analysis capabilities for X/Twitter accounts,
including profile intelligence, content behavior analysis, risk assessment,
and business intelligence.

Author: X Analysis Bot
Version: 2.0
"""

import re
import math
import json
from datetime import datetime, timezone
from collections import Counter
from typing import Dict, List, Optional, Any

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False

class ComprehensiveAnalyzer:
    """Advanced Twitter/X account analysis engine"""
    
    def __init__(self):
        self.crypto_keywords = [
            'crypto', 'blockchain', 'bitcoin', 'ethereum', 'defi', 'nft',
            'web3', 'dao', 'solidity', 'smart contract', '.eth', '.btc',
            'dapp', 'yield', 'farming', 'staking', 'mining', 'hodl'
        ]
        
        self.professional_keywords = [
            'ceo', 'cto', 'founder', 'developer', 'engineer', 'analyst',
            'manager', 'director', 'consultant', 'researcher', 'scientist',
            'professor', 'doctor', 'phd', 'mba', 'attorney', 'lawyer',
            'designer', 'architect', 'lead', 'senior', 'principal'
        ]
        
        self.tech_keywords = [
            'python', 'javascript', 'react', 'node', 'rust', 'go', 'java',
            'aws', 'kubernetes', 'docker', 'ai', 'ml', 'machine learning',
            'data science', 'cybersecurity', 'devops', 'frontend', 'backend'
        ]
        
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'i', 'me', 'my', 'we', 'our', 'you', 'your',
            'he', 'she', 'it', 'they', 'them', 'is', 'are', 'was', 'were',
            'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did'
        }
    
    def analyze_comprehensive_profile(self, user, tweets_data=None) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of a Twitter/X user profile
        
        Args:
            user: Twitter user object with profile data
            tweets_data: Optional recent tweets data
            
        Returns:
            Dictionary containing comprehensive analysis results
        """
        analysis = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'username': getattr(user, 'username', 'unknown'),
            'account_fundamentals': self._analyze_account_fundamentals(user),
            'profile_intelligence': self._analyze_profile_intelligence(user),
            'content_behavior': self._analyze_content_behavior(tweets_data) if tweets_data else None,
            'network_influence': self._analyze_network_influence(user, tweets_data),
            'risk_assessment': self._analyze_risk_factors(user, tweets_data),
            'business_intelligence': self._analyze_business_indicators(user, tweets_data)
        }
        
        # Calculate overall scores
        analysis['overall_scores'] = self._calculate_overall_scores(analysis)
        
        return analysis
    
    def _analyze_account_fundamentals(self, user) -> Dict[str, Any]:
        """Analyze basic account metrics and vitals"""
        
        # Account age calculation
        account_age = {'total_days': 0, 'years': 0, 'days': 0, 'created_at': None}
        if hasattr(user, 'created_at') and user.created_at:
            created_date = user.created_at
            if created_date.tzinfo is None:
                created_date = created_date.replace(tzinfo=timezone.utc)
            
            now = datetime.now(timezone.utc)
            age_delta = now - created_date
            years = age_delta.days // 365
            remaining_days = age_delta.days % 365
            
            account_age = {
                'total_days': age_delta.days,
                'years': years,
                'days': remaining_days,
                'created_at': created_date.isoformat()
            }
        
        # Verification and protection status
        verification = {
            'is_verified': getattr(user, 'verified', False),
            'verification_type': getattr(user, 'verified_type', None),
            'is_protected': getattr(user, 'protected', False)
        }
        
        # Social metrics
        social_metrics = {}
        if hasattr(user, 'public_metrics'):
            metrics = user.public_metrics
            followers = metrics.get('followers_count', 0)
            following = metrics.get('following_count', 0)
            tweets_total = metrics.get('tweet_count', 0)
            
            # Calculate derived metrics
            follower_ratio = followers / following if following > 0 else followers
            tweets_per_day = tweets_total / max(account_age['total_days'], 1)
            
            social_metrics = {
                'followers': followers,
                'following': following,
                'ratio': round(follower_ratio, 2),
                'tweets_total': tweets_total,
                'listed_count': metrics.get('listed_count', 0),
                'tweets_per_day': round(tweets_per_day, 2),
                'like_count': metrics.get('like_count', 0)
            }
        
        # Account type classification
        account_type = self._classify_account_type(social_metrics, verification)
        
        return {
            'account_age': account_age,
            'verification': verification,
            'social_metrics': social_metrics,
            'account_type': account_type
        }
    
    def _analyze_profile_intelligence(self, user) -> Dict[str, Any]:
        """Deep analysis of profile information and bio"""
        
        bio = getattr(user, 'description', '') or ''
        location = getattr(user, 'location', '') or ''
        website = getattr(user, 'url', '') or ''
        name = getattr(user, 'name', '') or ''
        
        # Bio structural analysis
        bio_analysis = {
            'length': len(bio),
            'word_count': len(bio.split()) if bio else 0,
            'has_links': bool(re.search(r'http[s]?://|www\.', bio)),
            'has_mentions': bool(re.search(r'@\w+', bio)),
            'has_hashtags': bool(re.search(r'#\w+', bio)),
            'has_emojis': bool(re.search(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', bio))
        }
        
        # Keyword extraction and categorization
        bio_lower = bio.lower()
        name_lower = name.lower()
        combined_text = f"{bio_lower} {name_lower}".strip()
        
        # Professional indicators
        professional_indicators = [kw for kw in self.professional_keywords if kw in combined_text]
        crypto_indicators = [kw for kw in self.crypto_keywords if kw in combined_text]
        tech_indicators = [kw for kw in self.tech_keywords if kw in combined_text]
        
        # Extract meaningful keywords
        clean_text = re.sub(r'http[s]?://\S+|www\.\S+|@\w+|#\w+', '', bio)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', clean_text.lower())
        meaningful_words = [word for word in words if word not in self.stop_words]
        word_counts = Counter(meaningful_words)
        top_keywords = [word for word, count in word_counts.most_common(10)]
        
        # Industry classification
        industry_signals = self._classify_industry(professional_indicators, crypto_indicators, tech_indicators, bio_lower)
        
        # Profile completeness score
        completeness_elements = [
            (bio, 4),  # Bio is most important
            (location, 2),
            (website, 2),
            (getattr(user, 'profile_banner_url', None), 1),
            (getattr(user, 'profile_image_url', None), 1)
        ]
        completeness_score = sum(weight for element, weight in completeness_elements if element)
        
        # Communication style analysis
        communication_style = self._analyze_communication_style(bio, name)
        
        return {
            'bio_analysis': bio_analysis,
            'keywords': {
                'top_keywords': top_keywords,
                'professional_indicators': professional_indicators,
                'crypto_indicators': crypto_indicators,
                'tech_indicators': tech_indicators
            },
            'industry_signals': industry_signals,
            'completeness_score': completeness_score,
            'max_completeness': 10,
            'profile_data': {
                'location': location,
                'website': website,
                'name': name
            },
            'communication_style': communication_style
        }
    
    def _analyze_content_behavior(self, tweets_data) -> Optional[Dict[str, Any]]:
        """Analyze tweet content and behavioral patterns"""
        
        if not tweets_data or not hasattr(tweets_data, 'data') or not tweets_data.data:
            return None
        
        tweets = tweets_data.data
        
        # Initialize counters
        total_likes = total_retweets = total_replies = 0
        original_tweets = reply_tweets = thread_tweets = 0
        media_tweets = link_tweets = 0
        hashtags = []
        mentions = []
        all_text = ""
        
        # Time-based analysis
        tweet_times = []
        daily_counts = Counter()
        hourly_counts = Counter()
        
        for tweet in tweets:
            tweet_text = getattr(tweet, 'text', '')
            all_text += " " + tweet_text
            
            # Engagement metrics
            if hasattr(tweet, 'public_metrics'):
                metrics = tweet.public_metrics
                total_likes += metrics.get('like_count', 0)
                total_retweets += metrics.get('retweet_count', 0)
                total_replies += metrics.get('reply_count', 0)
            
            # Content type analysis
            if hasattr(tweet, 'in_reply_to_user_id') and tweet.in_reply_to_user_id:
                reply_tweets += 1
            else:
                original_tweets += 1
            
            # Extract social signals
            hashtag_matches = re.findall(r'#(\w+)', tweet_text)
            mention_matches = re.findall(r'@(\w+)', tweet_text)
            hashtags.extend(hashtag_matches)
            mentions.extend(mention_matches)
            
            # Media and link detection
            if re.search(r'http[s]?://\S+', tweet_text):
                link_tweets += 1
            
            if hasattr(tweet, 'entities') and tweet.entities:
                if 'media' in str(tweet.entities):
                    media_tweets += 1
            
            # Time analysis
            if hasattr(tweet, 'created_at') and tweet.created_at:
                tweet_times.append(tweet.created_at)
                day = tweet.created_at.strftime('%A')
                hour = tweet.created_at.hour
                daily_counts[day] += 1
                hourly_counts[hour] += 1
        
        tweet_count = len(tweets)
        
        # Calculate engagement metrics
        engagement_metrics = {
            'avg_likes': round(total_likes / tweet_count, 1) if tweet_count > 0 else 0,
            'avg_retweets': round(total_retweets / tweet_count, 1) if tweet_count > 0 else 0,
            'avg_replies': round(total_replies / tweet_count, 1) if tweet_count > 0 else 0,
            'total_engagement': total_likes + total_retweets + total_replies
        }
        
        # Content pattern analysis
        content_patterns = {
            'original_ratio': round(original_tweets / tweet_count, 2) if tweet_count > 0 else 0,
            'reply_ratio': round(reply_tweets / tweet_count, 2) if tweet_count > 0 else 0,
            'media_ratio': round(media_tweets / tweet_count, 2) if tweet_count > 0 else 0,
            'link_ratio': round(link_tweets / tweet_count, 2) if tweet_count > 0 else 0
        }
        
        # Social signals
        hashtag_counts = Counter(hashtags)
        mention_counts = Counter(mentions)
        social_signals = {
            'top_hashtags': [tag for tag, count in hashtag_counts.most_common(10)],
            'top_mentions': [mention for mention, count in mention_counts.most_common(10)],
            'hashtag_diversity': len(set(hashtags)),
            'mention_diversity': len(set(mentions)),
            'avg_hashtags_per_tweet': round(len(hashtags) / tweet_count, 1) if tweet_count > 0 else 0
        }
        
        # Sentiment analysis
        sentiment = {'score': 0, 'classification': 'Neutral'}
        if TEXTBLOB_AVAILABLE and all_text.strip():
            try:
                blob = TextBlob(all_text)
                sentiment_score = round(blob.sentiment.polarity, 3)
                sentiment = {
                    'score': sentiment_score,
                    'classification': self._classify_sentiment(sentiment_score)
                }
            except Exception:
                pass
        
        # Posting patterns
        posting_patterns = {
            'most_active_day': daily_counts.most_common(1)[0][0] if daily_counts else 'Unknown',
            'most_active_hour': hourly_counts.most_common(1)[0][0] if hourly_counts else 'Unknown',
            'posting_consistency': len(daily_counts) / 7.0 if daily_counts else 0
        }
        
        return {
            'tweet_count': tweet_count,
            'engagement_metrics': engagement_metrics,
            'content_patterns': content_patterns,
            'social_signals': social_signals,
            'sentiment': sentiment,
            'posting_patterns': posting_patterns
        }
    
    def _analyze_network_influence(self, user, tweets_data) -> Dict[str, Any]:
        """Calculate influence metrics and network position indicators"""
        
        # Get basic metrics
        followers = 0
        following = 0
        listed_count = 0
        
        if hasattr(user, 'public_metrics'):
            metrics = user.public_metrics
            followers = metrics.get('followers_count', 0)
            following = metrics.get('following_count', 0)
            listed_count = metrics.get('listed_count', 0)
        
        # Calculate influence components
        follower_impact = math.log10(max(followers, 1)) * 15
        ratio = followers / following if following > 0 else followers
        ratio_impact = min(ratio * 2, 25)
        
        # Engagement impact from tweets
        engagement_impact = 0
        if tweets_data and hasattr(tweets_data, 'data') and tweets_data.data:
            avg_engagement = sum(
                tweet.public_metrics.get('like_count', 0) + 
                tweet.public_metrics.get('retweet_count', 0)
                for tweet in tweets_data.data 
                if hasattr(tweet, 'public_metrics')
            ) / len(tweets_data.data)
            engagement_impact = min(avg_engagement * 0.5, 20)
        
        # Authority indicators
        verification_bonus = 10 if getattr(user, 'verified', False) else 0
        listed_ratio = (listed_count / max(followers / 1000, 1)) if followers > 0 else 0
        authority_impact = min(listed_ratio * 5, 15) + verification_bonus
        
        # Calculate final influence score
        raw_score = follower_impact + ratio_impact + engagement_impact + authority_impact
        influence_score = min(max(int(raw_score), 1), 100)
        
        # Determine influence tier
        if influence_score >= 80:
            influence_tier = "Macro Influencer"
        elif influence_score >= 65:
            influence_tier = "High Influence"
        elif influence_score >= 45:
            influence_tier = "Medium Influence"
        elif influence_score >= 25:
            influence_tier = "Emerging Influence"
        else:
            influence_tier = "Limited Reach"
        
        # Network position analysis
        network_position = self._analyze_network_position(followers, following, listed_count)
        
        return {
            'influence_score': influence_score,
            'influence_tier': influence_tier,
            'score_components': {
                'follower_impact': round(follower_impact, 1),
                'ratio_impact': round(ratio_impact, 1),
                'engagement_impact': round(engagement_impact, 1),
                'authority_impact': round(authority_impact, 1)
            },
            'network_metrics': {
                'followers': followers,
                'following': following,
                'ratio': round(ratio, 2),
                'listed_count': listed_count
            },
            'network_position': network_position
        }
    
    def _analyze_risk_factors(self, user, tweets_data) -> Dict[str, Any]:
        """Assess account authenticity and potential risk indicators"""
        
        risk_score = 100  # Start with perfect score, deduct for red flags
        risk_factors = []
        
        # Account age risks
        account_age_days = 0
        if hasattr(user, 'created_at') and user.created_at:
            created_date = user.created_at
            if created_date.tzinfo is None:
                created_date = created_date.replace(tzinfo=timezone.utc)
            account_age_days = (datetime.now(timezone.utc) - created_date).days
        
        if account_age_days < 30:
            risk_score -= 25
            risk_factors.append("Very new account (< 30 days)")
        elif account_age_days < 90:
            risk_score -= 10
            risk_factors.append("New account (< 90 days)")
        
        # Profile completeness risks
        bio = getattr(user, 'description', '') or ''
        if not bio:
            risk_score -= 15
            risk_factors.append("No bio/description")
        
        if not getattr(user, 'location', ''):
            risk_score -= 5
            risk_factors.append("No location specified")
        
        # Follower pattern analysis
        if hasattr(user, 'public_metrics'):
            metrics = user.public_metrics
            followers = metrics.get('followers_count', 0)
            following = metrics.get('following_count', 0)
            tweets_count = metrics.get('tweet_count', 0)
            
            # Suspicious ratios
            if following > 0:
                ratio = followers / following
                if ratio > 100 and followers > 10000:
                    # Very high ratio might indicate purchased followers
                    risk_score -= 10
                    risk_factors.append("Unusually high follower ratio")
                elif ratio < 0.1 and followers < 100:
                    # Following many, few followers back
                    risk_score -= 5
                    risk_factors.append("Low follower-to-following ratio")
            
            # Activity consistency
            if account_age_days > 0:
                tweets_per_day = tweets_count / account_age_days
                if tweets_per_day > 50:
                    risk_score -= 15
                    risk_factors.append("Extremely high posting frequency")
                elif tweets_per_day < 0.01 and account_age_days > 365:
                    risk_score -= 10
                    risk_factors.append("Very low activity for account age")
        
        # Content behavior risks
        if tweets_data and hasattr(tweets_data, 'data') and tweets_data.data:
            tweets = tweets_data.data
            
            # Check for bot-like patterns
            if len(tweets) > 5:
                # Repetitive content check
                tweet_texts = [getattr(tweet, 'text', '') for tweet in tweets]
                unique_ratio = len(set(tweet_texts)) / len(tweet_texts)
                if unique_ratio < 0.8:
                    risk_score -= 15
                    risk_factors.append("High content repetition detected")
                
                # Suspicious timing patterns
                if len(tweets) > 10:
                    time_intervals = []
                    for i in range(1, len(tweets)):
                        if hasattr(tweets[i], 'created_at') and hasattr(tweets[i-1], 'created_at'):
                            interval = abs((tweets[i].created_at - tweets[i-1].created_at).total_seconds())
                            time_intervals.append(interval)
                    
                    if time_intervals:
                        avg_interval = sum(time_intervals) / len(time_intervals)
                        if avg_interval < 60:  # Less than 1 minute average
                            risk_score -= 20
                            risk_factors.append("Suspicious posting intervals")
        
        # Determine risk level
        if risk_score >= 80:
            risk_level = "Low Risk"
        elif risk_score >= 60:
            risk_level = "Medium Risk"
        elif risk_score >= 40:
            risk_level = "High Risk"
        else:
            risk_level = "Very High Risk"
        
        # Authenticity indicators
        authenticity_score = max(risk_score, 0)
        authenticity_indicators = self._calculate_authenticity_indicators(user, tweets_data)
        
        return {
            'risk_score': max(risk_score, 0),
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'authenticity_score': authenticity_score,
            'authenticity_indicators': authenticity_indicators
        }
    
    def _analyze_business_indicators(self, user, tweets_data) -> Dict[str, Any]:
        """Analyze commercial activity and business indicators"""
        
        bio = getattr(user, 'description', '') or ''
        website = getattr(user, 'url', '') or ''
        name = getattr(user, 'name', '') or ''
        
        business_score = 0
        business_indicators = []
        commercial_keywords = []
        
        # Business keyword detection
        business_terms = [
            'ceo', 'founder', 'startup', 'company', 'business', 'entrepreneur',
            'consulting', 'services', 'agency', 'firm', 'corp', 'inc', 'llc',
            'marketing', 'sales', 'advisor', 'investor', 'partner'
        ]
        
        combined_text = f"{bio} {name}".lower()
        for term in business_terms:
            if term in combined_text:
                business_score += 5
                commercial_keywords.append(term)
        
        # Website analysis
        if website:
            business_score += 10
            business_indicators.append("Has business website")
            
            # Domain analysis
            if any(domain in website for domain in ['.com', '.io', '.co', '.org']):
                business_score += 5
        
        # Professional title detection
        professional_titles = ['ceo', 'cto', 'founder', 'director', 'manager', 'head of']
        if any(title in combined_text for title in professional_titles):
            business_score += 15
            business_indicators.append("Professional title in profile")
        
        # Content analysis for business activity
        commercial_activity = {'score': 0, 'indicators': []}
        if tweets_data and hasattr(tweets_data, 'data') and tweets_data.data:
            tweets = tweets_data.data
            
            promotional_keywords = [
                'buy', 'purchase', 'sale', 'discount', 'promo', 'launch',
                'product', 'service', 'offer', 'deal', 'limited time'
            ]
            
            promotional_tweets = 0
            for tweet in tweets:
                tweet_text = getattr(tweet, 'text', '').lower()
                if any(keyword in tweet_text for keyword in promotional_keywords):
                    promotional_tweets += 1
            
            if promotional_tweets > 0:
                promo_ratio = promotional_tweets / len(tweets)
                commercial_activity['score'] = min(promo_ratio * 100, 50)
                commercial_activity['indicators'].append(f"{promotional_tweets} promotional tweets found")
                
                if promo_ratio > 0.3:
                    business_score += 20
                    business_indicators.append("High promotional content")
                elif promo_ratio > 0.1:
                    business_score += 10
                    business_indicators.append("Moderate promotional content")
        
        # Business sophistication level
        if business_score >= 40:
            business_level = "High Commercial Activity"
        elif business_score >= 20:
            business_level = "Moderate Business Presence"
        elif business_score >= 10:
            business_level = "Some Business Indicators"
        else:
            business_level = "Personal/Non-Commercial"
        
        return {
            'business_score': min(business_score, 100),
            'business_level': business_level,
            'business_indicators': business_indicators,
            'commercial_keywords': commercial_keywords,
            'commercial_activity': commercial_activity,
            'monetization_signals': {
                'has_website': bool(website),
                'professional_title': any(title in combined_text for title in professional_titles),
                'business_keywords_count': len(commercial_keywords)
            }
        }
    
    def _calculate_overall_scores(self, analysis) -> Dict[str, Any]:
        """Calculate overall assessment scores"""
        
        # Extract key metrics
        fundamentals = analysis.get('account_fundamentals', {})
        profile = analysis.get('profile_intelligence', {})
        network = analysis.get('network_influence', {})
        risk = analysis.get('risk_assessment', {})
        business = analysis.get('business_intelligence', {})
        
        # Overall credibility score
        credibility_components = [
            fundamentals.get('account_age', {}).get('total_days', 0) / 365 * 20,  # Age factor
            profile.get('completeness_score', 0) * 2,  # Profile completeness
            min(network.get('influence_score', 0) / 2, 30),  # Influence factor
            risk.get('authenticity_score', 0) / 4,  # Authenticity
            10 if fundamentals.get('verification', {}).get('is_verified') else 0  # Verification bonus
        ]
        
        credibility_score = min(sum(credibility_components), 100)
        
        # Overall engagement quality
        engagement_quality = 0
        if analysis.get('content_behavior'):
            content = analysis['content_behavior']
            engagement_metrics = content.get('engagement_metrics', {})
            content_patterns = content.get('content_patterns', {})
            
            # Quality indicators
            avg_likes = engagement_metrics.get('avg_likes', 0)
            original_ratio = content_patterns.get('original_ratio', 0)
            
            engagement_quality = min(
                (math.log10(max(avg_likes, 1)) * 20) + (original_ratio * 30),
                100
            )
        
        # Key insights generation
        insights = self._generate_key_insights(analysis)
        
        return {
            'credibility_score': round(credibility_score, 1),
            'engagement_quality': round(engagement_quality, 1),
            'overall_rating': self._calculate_overall_rating(credibility_score, engagement_quality),
            'key_insights': insights
        }
    
    # Helper methods
    
    def _classify_account_type(self, social_metrics, verification):
        """Classify account type based on metrics"""
        followers = social_metrics.get('followers', 0)
        ratio = social_metrics.get('ratio', 0)
        is_verified = verification.get('is_verified', False)
        
        if is_verified and followers > 100000:
            return "Celebrity/Public Figure"
        elif followers > 50000 and ratio > 10:
            return "Influencer"
        elif followers > 10000:
            return "Popular Account"
        elif ratio < 0.5 and social_metrics.get('following', 0) > 1000:
            return "Active Networker"
        else:
            return "Regular User"
    
    def _classify_industry(self, professional_indicators, crypto_indicators, tech_indicators, bio_text):
        """Classify likely industry based on profile signals"""
        if crypto_indicators:
            return "Crypto/Blockchain"
        elif tech_indicators:
            return "Technology"
        elif professional_indicators:
            if any(term in bio_text for term in ['marketing', 'sales', 'growth']):
                return "Marketing/Sales"
            elif any(term in bio_text for term in ['finance', 'investment', 'trading']):
                return "Finance"
            else:
                return "Professional Services"
        else:
            return "General/Personal"
    
    def _analyze_communication_style(self, bio, name):
        """Analyze communication style from profile text"""
        combined_text = f"{bio} {name}".lower()
        
        # Style indicators
        formal_indicators = ['professional', 'executive', 'phd', 'dr.', 'professor']
        casual_indicators = ['hey', 'love', 'passionate', 'enthusiast', 'fan']
        tech_indicators = ['building', 'coding', 'developing', 'engineering']
        
        if any(indicator in combined_text for indicator in formal_indicators):
            return "Formal/Professional"
        elif any(indicator in combined_text for indicator in tech_indicators):
            return "Technical/Builder"
        elif any(indicator in combined_text for indicator in casual_indicators):
            return "Casual/Personal"
        else:
            return "Neutral"
    
    def _classify_sentiment(self, score):
        """Classify sentiment score into categories"""
        if score > 0.1:
            return "Positive"
        elif score < -0.1:
            return "Negative"
        else:
            return "Neutral"
    
    def _analyze_network_position(self, followers, following, listed_count):
        """Analyze network position and role"""
        ratio = followers / following if following > 0 else followers
        
        if ratio > 50 and followers > 10000:
            return "Information Broadcaster"
        elif ratio > 10 and followers > 1000:
            return "Thought Leader"
        elif ratio < 2 and following > 500:
            return "Active Community Member"
        elif listed_count > followers / 100:
            return "Curated Content Creator"
        else:
            return "Standard User"
    
    def _calculate_authenticity_indicators(self, user, tweets_data):
        """Calculate various authenticity indicators"""
        indicators = {}
        
        # Profile consistency check
        name = getattr(user, 'name', '') or ''
        username = getattr(user, 'username', '') or ''
        bio = getattr(user, 'description', '') or ''
        
        indicators['profile_consistency'] = len(bio) > 20 and name.strip() != ''
        indicators['username_quality'] = not re.search(r'\d{4,}', username)  # No long number sequences
        
        # Activity patterns
        if tweets_data and hasattr(tweets_data, 'data') and tweets_data.data:
            tweets = tweets_data.data
            
            # Time diversity check
            if len(tweets) > 5:
                hours = set()
                for tweet in tweets:
                    if hasattr(tweet, 'created_at'):
                        hours.add(tweet.created_at.hour)
                indicators['time_diversity'] = len(hours) > 3
            else:
                indicators['time_diversity'] = True
        else:
            indicators['time_diversity'] = True
        
        # Verification status
        indicators['verified_account'] = getattr(user, 'verified', False)
        
        return indicators
    
    def _generate_key_insights(self, analysis):
        """Generate key insights from the analysis"""
        insights = []
        
        # Account fundamentals insights
        fundamentals = analysis.get('account_fundamentals', {})
        account_age = fundamentals.get('account_age', {})
        social_metrics = fundamentals.get('social_metrics', {})
        
        if account_age.get('years', 0) > 5:
            insights.append("Established account with long history")
        elif account_age.get('years', 0) < 1:
            insights.append("Relatively new account")
        
        # Influence insights
        network = analysis.get('network_influence', {})
        influence_score = network.get('influence_score', 0)
        
        if influence_score > 70:
            insights.append("High influence potential in their network")
        elif influence_score > 40:
            insights.append("Moderate influence within community")
        
        # Content insights
        content = analysis.get('content_behavior')
        if content:
            original_ratio = content.get('content_patterns', {}).get('original_ratio', 0)
            if original_ratio > 0.7:
                insights.append("Primarily creates original content")
            elif original_ratio < 0.3:
                insights.append("Heavily relies on sharing/replying to others")
        
        # Industry insights
        profile = analysis.get('profile_intelligence', {})
        industry = profile.get('industry_signals', '')
        if industry and industry != 'General/Personal':
            insights.append(f"Professional presence in {industry}")
        
        # Risk insights
        risk = analysis.get('risk_assessment', {})
        risk_level = risk.get('risk_level', '')
        if risk_level == 'Low Risk':
            insights.append("High authenticity indicators")
        elif risk_level in ['High Risk', 'Very High Risk']:
            insights.append("Some authenticity concerns detected")
        
        # Business insights
        business = analysis.get('business_intelligence', {})
        business_level = business.get('business_level', '')
        if 'Commercial' in business_level:
            insights.append("Active commercial/business presence")
        
        return insights[:5]  # Return top 5 insights
    
    def _calculate_overall_rating(self, credibility_score, engagement_quality):
        """Calculate overall account rating"""
        combined_score = (credibility_score * 0.6) + (engagement_quality * 0.4)
        
        if combined_score >= 80:
            return "Excellent"
        elif combined_score >= 65:
            return "Very Good"
        elif combined_score >= 50:
            return "Good"
        elif combined_score >= 35:
            return "Fair"
        else:
            return "Poor"
    
    def format_comprehensive_analysis(self, analysis_results) -> str:
        """Format comprehensive analysis results for display"""
        
        username = analysis_results.get('username', 'Unknown')
        output = []
        
        # Header
        output.append("=" * 80)
        output.append("🔬 COMPREHENSIVE ACCOUNT ANALYSIS")
        output.append("=" * 80)
        output.append(f"👤 Account: @{username}")
        output.append(f"🕐 Analysis Time: {analysis_results.get('timestamp', 'N/A')}")
        output.append("")
        
        # Account Fundamentals
        fundamentals = analysis_results.get('account_fundamentals', {})
        if fundamentals:
            output.append("📊 ACCOUNT FUNDAMENTALS")
            output.append("-" * 40)
            
            age = fundamentals.get('account_age', {})
            output.append(f"📅 Account Age: {age.get('years', 0)} years, {age.get('days', 0)} days")
            
            verification = fundamentals.get('verification', {})
            verified_status = "✅ Verified" if verification.get('is_verified') else "❌ Not Verified"
            output.append(f"🔒 Status: {verified_status}")
            
            social = fundamentals.get('social_metrics', {})
            if social:
                output.append(f"👥 Network: {social.get('followers', 0):,} followers / {social.get('following', 0):,} following")
                output.append(f"📊 Ratio: {social.get('ratio', 0)} | Activity: {social.get('tweets_per_day', 0)} tweets/day")
            
            output.append(f"🏷️  Type: {fundamentals.get('account_type', 'Unknown')}")
            output.append("")
        
        # Profile Intelligence
        profile = analysis_results.get('profile_intelligence', {})
        if profile:
            output.append("🧠 PROFILE INTELLIGENCE")
            output.append("-" * 40)
            
            bio_analysis = profile.get('bio_analysis', {})
            output.append(f"📝 Bio: {bio_analysis.get('length', 0)} chars, {bio_analysis.get('word_count', 0)} words")
            
            keywords = profile.get('keywords', {})
            if keywords.get('top_keywords'):
                output.append(f"🔤 Keywords: {', '.join(keywords['top_keywords'][:5])}")
            
            if keywords.get('professional_indicators'):
                output.append(f"💼 Professional: {', '.join(keywords['professional_indicators'][:3])}")
            
            if keywords.get('crypto_indicators'):
                output.append(f"₿ Crypto/Web3: {', '.join(keywords['crypto_indicators'][:3])}")
            
            output.append(f"🌐 Industry: {profile.get('industry_signals', 'General')}")
            output.append(f"📋 Completeness: {profile.get('completeness_score', 0)}/10")
            output.append(f"💬 Style: {profile.get('communication_style', 'Unknown')}")
            output.append("")
        
        # Content Behavior
        content = analysis_results.get('content_behavior')
        if content:
            output.append("📈 CONTENT BEHAVIOR")
            output.append("-" * 40)
            
            output.append(f"🐦 Tweets Analyzed: {content.get('tweet_count', 0)}")
            
            engagement = content.get('engagement_metrics', {})
            output.append(f"❤️  Avg Engagement: {engagement.get('avg_likes', 0)} likes, {engagement.get('avg_retweets', 0)} RTs")
            
            patterns = content.get('content_patterns', {})
            output.append(f"📊 Content Mix: {patterns.get('original_ratio', 0)*100:.1f}% original")
            
            sentiment = content.get('sentiment', {})
            output.append(f"😊 Sentiment: {sentiment.get('score', 0)} ({sentiment.get('classification', 'Neutral')})")
            
            social_signals = content.get('social_signals', {})
            if social_signals.get('top_hashtags'):
                output.append(f"# Top Tags: {', '.join(['#' + tag for tag in social_signals['top_hashtags'][:3]])}")
            
            posting = content.get('posting_patterns', {})
            output.append(f"⏰ Most Active: {posting.get('most_active_day', 'Unknown')} at {posting.get('most_active_hour', 'Unknown')}:00")
            output.append("")
        
        # Network Influence
        network = analysis_results.get('network_influence', {})
        if network:
            output.append("🌐 NETWORK & INFLUENCE")
            output.append("-" * 40)
            
            output.append(f"⭐ Influence Score: {network.get('influence_score', 0)}/100")
            output.append(f"🎯 Tier: {network.get('influence_tier', 'Unknown')}")
            output.append(f"📍 Position: {network.get('network_position', 'Unknown')}")
            
            components = network.get('score_components', {})
            output.append(f"🔹 Components: Followers({components.get('follower_impact', 0):.1f}) + Ratio({components.get('ratio_impact', 0):.1f}) + Engagement({components.get('engagement_impact', 0):.1f})")
            output.append("")
        
        # Risk Assessment
        risk = analysis_results.get('risk_assessment', {})
        if risk:
            output.append("🚨 RISK ASSESSMENT")
            output.append("-" * 40)
            
            output.append(f"🛡️  Risk Level: {risk.get('risk_level', 'Unknown')}")
            output.append(f"✅ Authenticity: {risk.get('authenticity_score', 0)}/100")
            
            risk_factors = risk.get('risk_factors', [])
            if risk_factors:
                output.append(f"⚠️  Concerns: {', '.join(risk_factors[:3])}")
            else:
                output.append("✅ No significant risk factors detected")
            output.append("")
        
        # Business Intelligence
        business = analysis_results.get('business_intelligence', {})
        if business:
            output.append("💼 BUSINESS INTELLIGENCE")
            output.append("-" * 40)
            
            output.append(f"🏢 Business Level: {business.get('business_level', 'Unknown')}")
            output.append(f"💰 Commercial Score: {business.get('business_score', 0)}/100")
            
            indicators = business.get('business_indicators', [])
            if indicators:
                output.append(f"📈 Indicators: {', '.join(indicators[:3])}")
            
            monetization = business.get('monetization_signals', {})
            signals = []
            if monetization.get('has_website'):
                signals.append("Website")
            if monetization.get('professional_title'):
                signals.append("Prof. Title")
            if signals:
                output.append(f"💳 Monetization: {', '.join(signals)}")
            output.append("")
        
        # Overall Scores
        overall = analysis_results.get('overall_scores', {})
        if overall:
            output.append("🎯 OVERALL ASSESSMENT")
            output.append("-" * 40)
            
            output.append(f"🏆 Overall Rating: {overall.get('overall_rating', 'Unknown')}")
            output.append(f"🎖️  Credibility: {overall.get('credibility_score', 0)}/100")
            output.append(f"📊 Engagement Quality: {overall.get('engagement_quality', 0)}/100")
            
            insights = overall.get('key_insights', [])
            if insights:
                output.append("\n💡 KEY INSIGHTS:")
                for i, insight in enumerate(insights, 1):
                    output.append(f"   {i}. {insight}")
            output.append("")
        
        # Footer
        output.append("=" * 80)
        output.append("")
        
        return "\n".join(output)
    
    def save_analysis_to_file(self, analysis_results, filename="comprehensive_analysis.txt"):
        """Save comprehensive analysis to file"""
        try:
            formatted_output = self.format_comprehensive_analysis(analysis_results)
            
            with open(filename, 'a', encoding='utf-8') as f:
                f.write(f"\n--- Comprehensive Analysis: {datetime.now(timezone.utc).isoformat()} ---\n")
                f.write(f"Username: @{analysis_results.get('username', 'Unknown')}\n\n")
                f.write(formatted_output)
                f.write("\n\n")
            
            return True
        except Exception as e:
            print(f"❌ Error saving analysis: {e}")
            return False