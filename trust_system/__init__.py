"""
Trust System Package
===================

Comprehensive trusted account validation system for X/Twitter account analysis.
This package provides trust verification by checking if accounts are followed by
trusted members of the Solana ecosystem and broader crypto community.

Components:
- TrustedAccountValidator: Core trust validation engine
- TrustIntegratedAnalyzer: Integration with comprehensive analysis
- TrustAwareReporting: Enhanced reporting with trust information

Trust Data Source:
https://github.com/devsyrem/turst-list/blob/main/list

Author: X Analysis Bot
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "X Analysis Bot"
__description__ = "Trusted account validation system for X/Twitter analysis"

# Import main classes for easy access
from .trusted_accounts import TrustedAccountValidator
from .trust_integration import TrustIntegratedAnalyzer, TrustAwareReporting

# Package-level constants
TRUST_LIST_URL = "https://raw.githubusercontent.com/devsyrem/turst-list/main/list"
DEFAULT_MIN_TRUSTED_FOLLOWERS = 2
DEFAULT_CACHE_DURATION_HOURS = 24
DEFAULT_MAX_API_CALLS = 50

# Convenience functions
def create_trust_validator(api_client):
    """
    Create a configured TrustedAccountValidator instance
    
    Args:
        api_client: Authenticated tweepy.Client instance
        
    Returns:
        TrustedAccountValidator: Configured validator instance
    """
    return TrustedAccountValidator(api_client)

def create_trust_integrated_analyzer(api_client, base_analyzer):
    """
    Create a configured TrustIntegratedAnalyzer instance
    
    Args:
        api_client: Authenticated tweepy.Client instance
        base_analyzer: ComprehensiveAnalyzer instance
        
    Returns:
        TrustIntegratedAnalyzer: Configured integrated analyzer
    """
    return TrustIntegratedAnalyzer(api_client, base_analyzer)

def get_package_info():
    """
    Get package information and status
    
    Returns:
        dict: Package information including version, components, etc.
    """
    return {
        'name': 'trust_system',
        'version': __version__,
        'author': __author__,
        'description': __description__,
        'trust_list_url': TRUST_LIST_URL,
        'components': [
            'TrustedAccountValidator',
            'TrustIntegratedAnalyzer', 
            'TrustAwareReporting'
        ],
        'default_settings': {
            'min_trusted_followers': DEFAULT_MIN_TRUSTED_FOLLOWERS,
            'cache_duration_hours': DEFAULT_CACHE_DURATION_HOURS,
            'max_api_calls': DEFAULT_MAX_API_CALLS
        }
    }

# Export all public components
__all__ = [
    'TrustedAccountValidator',
    'TrustIntegratedAnalyzer', 
    'TrustAwareReporting',
    'create_trust_validator',
    'create_trust_integrated_analyzer',
    'get_package_info',
    'TRUST_LIST_URL',
    'DEFAULT_MIN_TRUSTED_FOLLOWERS',
    'DEFAULT_CACHE_DURATION_HOURS',
    'DEFAULT_MAX_API_CALLS'
]