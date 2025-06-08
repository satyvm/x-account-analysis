"""
Trust Integration Module
========================

Integrates the trusted account validation system with the enhanced analysis framework.
Provides seamless trust validation as part of comprehensive account analysis.

Author: X Analysis Bot
Version: 1.0
"""

import logging
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple
from .trusted_accounts import TrustedAccountValidator

logger = logging.getLogger(__name__)

class TrustIntegratedAnalyzer:
    """Enhanced analyzer with integrated trusted account validation"""
    
    def __init__(self, api_client, base_analyzer):
        """
        Initialize trust-integrated analyzer
        
        Args:
            api_client: Twitter API client
            base_analyzer: Instance of ComprehensiveAnalyzer
        """
        self.api_client = api_client
        self.base_analyzer = base_analyzer
        self.trust_validator = None
        self.trust_enabled = False
        
        # Trust validation settings
        self.min_trusted_followers = 2
        self.trust_boost_factor = 0.3  # How much trust validation boosts scores
        self.max_trust_api_calls = 20  # API calls budget for trust validation
        
    def initialize_trust_system(self) -> bool:
        """Initialize the trusted account validation system"""
        try:
            logger.info("🔐 Initializing trust validation system...")
            
            self.trust_validator = TrustedAccountValidator(self.api_client)
            
            # Set API call limit for trust validation
            self.trust_validator.max_api_calls = self.max_trust_api_calls
            
            # Initialize the system
            if self.trust_validator.initialize_system():
                self.trust_enabled = True
                logger.info("✅ Trust validation system ready")
                return True
            else:
                logger.warning("⚠️ Trust validation system initialization failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error initializing trust system: {e}")
            return False
    
    def analyze_with_trust_validation(self, user, tweets_data=None, force_trust_check=False) -> Dict[str, Any]:
        """
        Perform comprehensive analysis including trusted account validation
        
        Args:
            user: Twitter user object
            tweets_data: Optional tweets data
            force_trust_check: Force trust validation even if disabled
            
        Returns:
            Enhanced analysis results with trust validation
        """
        try:
            logger.info(f"🔬 Starting trust-integrated analysis for @{getattr(user, 'username', 'unknown')}")
            
            # Perform base comprehensive analysis
            analysis_results = self.base_analyzer.analyze_comprehensive_profile(user, tweets_data)
            
            # Add trust validation if enabled
            trust_results = None
            if self.trust_enabled or force_trust_check:
                trust_results = self._perform_trust_validation(user)
                if trust_results:
                    analysis_results['trust_validation'] = trust_results
                    
                    # Enhance existing scores with trust data
                    analysis_results = self._integrate_trust_scores(analysis_results, trust_results)
            else:
                logger.info("ℹ️ Trust validation skipped (system not enabled)")
                analysis_results['trust_validation'] = {
                    'enabled': False,
                    'reason': 'Trust system not initialized'
                }
            
            # Add trust integration metadata
            analysis_results['trust_integration'] = {
                'enabled': self.trust_enabled,
                'validation_performed': trust_results is not None,
                'api_calls_used': self.trust_validator.api_calls_made if self.trust_validator else 0,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"❌ Error in trust-integrated analysis: {e}")
            # Return base analysis without trust validation
            return self.base_analyzer.analyze_comprehensive_profile(user, tweets_data)
    
    def _perform_trust_validation(self, user) -> Optional[Dict[str, Any]]:
        """Perform trusted account validation for a user"""
        try:
            if not self.trust_validator:
                logger.warning("⚠️ Trust validator not available")
                return None
            
            user_id = str(getattr(user, 'id', ''))
            if not user_id:
                logger.warning("⚠️ No user ID available for trust validation")
                return None
            
            logger.info(f"🔍 Performing trust validation for user ID: {user_id}")
            
            # Perform the validation
            validation_result = self.trust_validator.check_trusted_followers(
                user_id, 
                self.min_trusted_followers
            )
            
            if validation_result:
                # Add additional trust metrics
                validation_result['trust_integration_score'] = self._calculate_trust_integration_score(validation_result)
                
                status = "✅ Validated" if validation_result.get('is_validated') else "❌ Not Validated"
                follower_count = validation_result.get('trusted_follower_count', 0)
                logger.info(f"🎯 Trust validation complete: {follower_count} trusted followers → {status}")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"❌ Error performing trust validation: {e}")
            return None
    
    def _integrate_trust_scores(self, analysis_results: Dict[str, Any], trust_results: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate trust validation results into the main analysis scores"""
        try:
            if not trust_results or not trust_results.get('is_validated'):
                # No trust boost if not validated
                return analysis_results
            
            trust_score = trust_results.get('trust_score', {})
            validation_strength = trust_results.get('validation_strength', 0)
            
            # Calculate trust boost factor
            trust_boost = (validation_strength / 100) * self.trust_boost_factor
            
            # Enhance credibility score
            if 'overall_scores' in analysis_results:
                current_credibility = analysis_results['overall_scores'].get('credibility_score', 0)
                trust_enhanced_credibility = min(current_credibility + (trust_boost * 100), 100)
                analysis_results['overall_scores']['credibility_score'] = round(trust_enhanced_credibility, 1)
                
                # Add trust-specific scoring
                analysis_results['overall_scores']['trust_boost_applied'] = round(trust_boost * 100, 1)
                analysis_results['overall_scores']['trust_enhanced'] = True
            
            # Enhance risk assessment
            if 'risk_assessment' in analysis_results:
                current_authenticity = analysis_results['risk_assessment'].get('authenticity_score', 0)
                trust_enhanced_authenticity = min(current_authenticity + (trust_boost * 50), 100)
                analysis_results['risk_assessment']['authenticity_score'] = round(trust_enhanced_authenticity, 1)
                
                # Reduce risk factors if highly trusted
                if trust_score.get('trust_level') in ['Highly Trusted', 'Well Trusted']:
                    risk_factors = analysis_results['risk_assessment'].get('risk_factors', [])
                    if risk_factors:
                        analysis_results['risk_assessment']['risk_factors'] = [
                            f"(Mitigated by trust validation) {factor}" for factor in risk_factors
                        ]
            
            # Enhance network influence
            if 'network_influence' in analysis_results:
                current_influence = analysis_results['network_influence'].get('influence_score', 0)
                trust_enhanced_influence = min(current_influence + (trust_boost * 30), 100)
                analysis_results['network_influence']['influence_score'] = round(trust_enhanced_influence, 1)
                
                # Add trust tier information
                trust_level = trust_score.get('trust_level', 'Unknown')
                analysis_results['network_influence']['trust_tier'] = trust_level
            
            logger.info(f"✅ Trust scores integrated - boost factor: {trust_boost:.3f}")
            return analysis_results
            
        except Exception as e:
            logger.error(f"❌ Error integrating trust scores: {e}")
            return analysis_results
    
    def _calculate_trust_integration_score(self, validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate additional trust metrics for integration"""
        try:
            trusted_count = validation_result.get('trusted_follower_count', 0)
            validation_strength = validation_result.get('validation_strength', 0)
            trust_score = validation_result.get('trust_score', {})
            
            # Calculate integration-specific metrics
            trust_density = trusted_count / max(validation_result.get('validation_details', {}).get('checked_accounts', 1), 1)
            trust_quality = trust_score.get('overall_score', 0) / 100
            
            # Combined trust metric (0-1 scale)
            combined_trust_metric = (
                (validation_strength / 100) * 0.4 +
                trust_quality * 0.4 +
                min(trust_density * 10, 1) * 0.2
            )
            
            # Trust reliability indicator
            api_calls_used = validation_result.get('api_calls_used', 0)
            reliability_score = min(api_calls_used / 10, 1.0)  # More API calls = more reliable
            
            return {
                'trust_density': round(trust_density, 4),
                'trust_quality': round(trust_quality, 3),
                'combined_metric': round(combined_trust_metric, 3),
                'reliability_score': round(reliability_score, 3),
                'integration_tier': self._determine_integration_tier(combined_trust_metric)
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculating trust integration score: {e}")
            return {}
    
    def _determine_integration_tier(self, combined_metric: float) -> str:
        """Determine trust integration tier based on combined metric"""
        if combined_metric >= 0.8:
            return "Premium Trust"
        elif combined_metric >= 0.6:
            return "High Trust"
        elif combined_metric >= 0.4:
            return "Moderate Trust"
        elif combined_metric >= 0.2:
            return "Basic Trust"
        else:
            return "Limited Trust"
    
    def format_enhanced_analysis_report(self, analysis_results: Dict[str, Any]) -> str:
        """Format comprehensive analysis with integrated trust validation"""
        try:
            username = analysis_results.get('username', 'Unknown')
            
            # Get base formatted analysis
            base_report = self.base_analyzer.format_comprehensive_analysis(analysis_results)
            
            # Add trust validation section
            trust_section = self._format_trust_section(analysis_results)
            
            # Combine reports
            enhanced_report = base_report
            
            # Insert trust section before overall assessment
            if "🎯 OVERALL ASSESSMENT" in enhanced_report:
                parts = enhanced_report.split("🎯 OVERALL ASSESSMENT")
                enhanced_report = parts[0] + trust_section + "\n🎯 OVERALL ASSESSMENT" + parts[1]
            else:
                enhanced_report += trust_section
            
            return enhanced_report
            
        except Exception as e:
            logger.error(f"❌ Error formatting enhanced analysis report: {e}")
            return self.base_analyzer.format_comprehensive_analysis(analysis_results)
    
    def _format_trust_section(self, analysis_results: Dict[str, Any]) -> str:
        """Format the trust validation section of the report"""
        trust_validation = analysis_results.get('trust_validation', {})
        trust_integration = analysis_results.get('trust_integration', {})
        
        if not trust_validation or not trust_integration.get('validation_performed'):
            return """
🔒 TRUST VALIDATION
----------------------------------------
❌ Trust validation not performed
⚠️ Reason: System not available or disabled
"""
        
        # Check for errors
        if trust_validation.get('validation_details', {}).get('error'):
            error_msg = trust_validation['validation_details']['error']
            return f"""
🔒 TRUST VALIDATION
----------------------------------------
❌ Validation Error: {error_msg}
📊 API Calls Used: {trust_validation.get('api_calls_used', 0)}
"""
        
        # Format successful validation
        is_validated = trust_validation.get('is_validated', False)
        trusted_count = trust_validation.get('trusted_follower_count', 0)
        min_required = trust_validation.get('min_required', 2)
        validation_strength = trust_validation.get('validation_strength', 0)
        trust_score = trust_validation.get('trust_score', {})
        trust_integration_score = trust_validation.get('trust_integration_score', {})
        
        status_emoji = "✅" if is_validated else "❌"
        status_text = "VALIDATED" if is_validated else "NOT VALIDATED"
        
        output = f"""
🔒 TRUST VALIDATION
----------------------------------------
{status_emoji} Status: {status_text}
🎯 Trusted Followers: {trusted_count}/{min_required} required
💪 Validation Strength: {validation_strength}/100
🏆 Trust Level: {trust_score.get('trust_level', 'Unknown')}
⭐ Trust Score: {trust_score.get('overall_score', 0)}/100
"""
        
        # Add trust integration metrics
        if trust_integration_score:
            integration_tier = trust_integration_score.get('integration_tier', 'Unknown')
            combined_metric = trust_integration_score.get('combined_metric', 0)
            output += f"🔗 Integration Tier: {integration_tier}\n"
            output += f"📊 Combined Trust Metric: {combined_metric:.3f}\n"
        
        # Show trusted followers (limited)
        trusted_followers = trust_validation.get('trusted_followers', [])
        if trusted_followers:
            output += f"\n👥 Trusted Followers ({len(trusted_followers)}):\n"
            for follower in trusted_followers[:5]:  # Show first 5
                output += f"   └─ @{follower['username']} ({follower['category']})\n"
            
            if len(trusted_followers) > 5:
                output += f"   └─ ... and {len(trusted_followers) - 5} more\n"
        
        # Show category breakdown
        follower_categories = trust_validation.get('validation_details', {}).get('follower_categories', {})
        if follower_categories:
            output += "\n📂 Categories:\n"
            for category, count in sorted(follower_categories.items(), key=lambda x: x[1], reverse=True):
                output += f"   └─ {category}: {count}\n"
        
        # Show validation stats
        api_calls = trust_validation.get('api_calls_used', 0)
        checked_accounts = trust_validation.get('validation_details', {}).get('checked_accounts', 0)
        output += f"\n📈 Stats: {checked_accounts:,} followers checked, {api_calls} API calls\n"
        
        return output
    
    def get_trust_system_status(self) -> Dict[str, Any]:
        """Get comprehensive trust system status"""
        base_status = {
            'trust_enabled': self.trust_enabled,
            'validator_available': self.trust_validator is not None,
            'min_trusted_followers': self.min_trusted_followers,
            'trust_boost_factor': self.trust_boost_factor,
            'max_trust_api_calls': self.max_trust_api_calls
        }
        
        if self.trust_validator:
            validator_status = self.trust_validator.get_system_status()
            base_status.update(validator_status)
        
        return base_status
    
    def save_enhanced_analysis(self, analysis_results: Dict[str, Any], filename: str = None) -> bool:
        """Save enhanced analysis with trust validation to file"""
        try:
            if not filename:
                username = analysis_results.get('username', 'unknown')
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"enhanced_analysis_{username}_{timestamp}.txt"
            
            formatted_report = self.format_enhanced_analysis_report(analysis_results)
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Enhanced Analysis Report with Trust Validation\n")
                f.write(f"Generated: {datetime.now(timezone.utc).isoformat()}\n")
                f.write("=" * 80 + "\n\n")
                f.write(formatted_report)
            
            logger.info(f"💾 Enhanced analysis saved: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving enhanced analysis: {e}")
            return False
    
    def quick_trust_check(self, user_id: str, username: str = None) -> Dict[str, Any]:
        """Perform a quick trust validation check"""
        try:
            if not self.trust_enabled or not self.trust_validator:
                return {
                    'available': False,
                    'reason': 'Trust system not initialized'
                }
            
            logger.info(f"⚡ Quick trust check for user ID: {user_id}")
            
            # Perform validation with lower limits for quick check
            original_max_calls = self.trust_validator.max_api_calls
            self.trust_validator.max_api_calls = 5  # Limited for quick check
            
            validation_result = self.trust_validator.check_trusted_followers(user_id, 1)  # Lower threshold
            
            # Restore original limit
            self.trust_validator.max_api_calls = original_max_calls
            
            # Format quick result
            quick_result = {
                'available': True,
                'validated': validation_result.get('is_validated', False),
                'trusted_count': validation_result.get('trusted_follower_count', 0),
                'trust_level': validation_result.get('trust_score', {}).get('trust_level', 'Unknown'),
                'validation_strength': validation_result.get('validation_strength', 0),
                'api_calls_used': validation_result.get('api_calls_used', 0),
                'quick_check': True
            }
            
            if username:
                quick_result['username'] = username
            
            return quick_result
            
        except Exception as e:
            logger.error(f"❌ Error in quick trust check: {e}")
            return {
                'available': False,
                'reason': f'Error: {str(e)}'
            }

class TrustAwareReporting:
    """Enhanced reporting with trust-aware formatting"""
    
    @staticmethod
    def format_trust_summary(analysis_results: Dict[str, Any]) -> str:
        """Create a concise trust summary for display"""
        trust_validation = analysis_results.get('trust_validation', {})
        
        if not trust_validation or not trust_validation.get('is_validated'):
            return "🔒 Trust: Not Validated"
        
        trust_score = trust_validation.get('trust_score', {})
        trusted_count = trust_validation.get('trusted_follower_count', 0)
        trust_level = trust_score.get('trust_level', 'Unknown')
        
        return f"🔒 Trust: ✅ {trust_level} ({trusted_count} trusted followers)"
    
    @staticmethod
    def format_trust_badge(validation_result: Dict[str, Any]) -> str:
        """Create a trust badge for user profiles"""
        if not validation_result or not validation_result.get('is_validated'):
            return "❌ Unverified"
        
        trust_score = validation_result.get('trust_score', {})
        trust_level = trust_score.get('trust_level', 'Unknown')
        
        badges = {
            'Highly Trusted': '🏆 Highly Trusted',
            'Well Trusted': '⭐ Well Trusted',
            'Moderately Trusted': '✅ Trusted',
            'Lightly Trusted': '🔹 Verified',
            'Minimally Trusted': '◾ Basic Trust'
        }
        
        return badges.get(trust_level, '✅ Verified')