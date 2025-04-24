"""
EHRbase package for interacting with the EHRbase REST API.

This package provides clients for interacting with EHRbase:
- EHRbaseClient: Facade client for all operations
- EHRbaseHttpClient: Low-level HTTP client
- TemplateClient: Client for template operations
- CompositionClient: Client for composition operations
"""

# Import main client classes for easier access
from .client import EHRbaseClient
from .http_client import EHRbaseHttpClient
from .template_client import TemplateClient
from .composition_client import CompositionClient
