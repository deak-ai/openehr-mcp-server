"""
EHRbase client facade for OpenEHR operations.

This module provides a facade for accessing specialized clients for the EHRbase REST API.
"""
import os
# Use a simple import that works with the project structure
from utils.logging_utils import get_logger
from .http_client import EHRbaseHttpClient
from .template_client import TemplateClient
from .composition_client import CompositionClient
from .ehr_client import EHRClient
from .query_client import QueryClient

class EHRbaseClient:
    """
    Facade client for the EHRbase API.
    
    This class provides a unified interface to access both template
    and composition operations, while maintaining separation of concerns
    between these different domains internally.
    """
    
    def __init__(self, base_url=None, default_ehr_id=None):
        """
        Initialize the EHRbase client facade.
        
        Args:
            base_url: The base URL of the EHRbase API (default from env var EHRBASE_URL)
            default_ehr_id: Default EHR ID to use (default from env var DEFAULT_EHR_ID)
        """
        self.logger = get_logger("ehrbase_client")
        
        # Create shared HTTP client
        self.http_client = EHRbaseHttpClient(base_url, default_ehr_id)
        
        # Create specialized domain clients
        self.templates = TemplateClient(self.http_client)
        self.compositions = CompositionClient(self.http_client)
        self.ehrs = EHRClient(self.http_client)
        self.queries = QueryClient(self.http_client)
        
        # Expose default EHR ID for convenience
        self.default_ehr_id = self.http_client.default_ehr_id
        
        self.logger.info(f"Initialized EHRbaseClient facade with URL: {self.http_client.base_url}")
    
    # Template operations - delegated to template client
    
    async def get_template_list(self, format_type="json"):
        """Get a list of all templates."""
        return await self.templates.list_templates(format_type)
    
    async def get_template(self, template_id, format_type="web_template"):
        """Get a specific template by ID."""
        return await self.templates.get_template(template_id, format_type)
    
    async def get_template_example(self, template_id, format_type="flat_json"):
        """Generate an example composition based on a template."""
        return await self.templates.get_example_composition(template_id, format_type)
    
    # Composition operations - delegated to composition client
    
    async def create_composition(self, ehr_id, composition_data, format_type="flat_json", template_id=None):
        """Create a new composition in the EHR."""
        return await self.compositions.create_composition(ehr_id, composition_data, format_type, template_id)
    
    async def get_composition(self, ehr_id, composition_uid, format_type="flat_json"):
        """Get a composition by its UID."""
        return await self.compositions.get_composition(ehr_id, composition_uid, format_type)
    
    async def update_composition(self, ehr_id, composition_uid, composition_data, format_type="flat_json"):
        """Update an existing composition."""
        return await self.compositions.update_composition(ehr_id, composition_uid, composition_data, format_type)
    
    async def delete_composition(self, ehr_id, preceding_version_uid, format_type="json"):
        """Delete a composition by its preceding version UID."""
        return await self.compositions.delete_composition(ehr_id, preceding_version_uid, format_type)
    
    # EHR operations - delegated to EHR client
    
    async def create_ehr(self, ehr_status=None, format_type="json"):
        """Create a new EHR in the system."""
        return await self.ehrs.create_ehr(ehr_status, format_type)
    
    async def get_ehr(self, ehr_id, format_type="json"):
        """Get an EHR by its ID."""
        return await self.ehrs.get_ehr(ehr_id, format_type)
    
    async def get_ehr_by_subject_id(self, subject_id, subject_namespace, format_type="json"):
        """
        Get an EHR by subject ID and namespace.
        
        This method retrieves an EHR based on the subject's ID and namespace,
        which is useful for finding a patient's EHR when you have their identifier.
        
        Args:
            subject_id: The subject ID to search for (required)
            subject_namespace: The subject namespace (required)
            format_type: Format type for the response (default: json)
            
        Returns:
            The EHR matching the subject criteria
        """
        return await self.ehrs.get_ehr_by_subject_id(subject_id, subject_namespace, format_type)
    
    async def get_ehr_status(self, ehr_id, format_type="json"):
        """Get the status of an EHR."""
        return await self.ehrs.get_ehr_status(ehr_id, format_type)
    
    async def update_ehr_status(self, ehr_id, status_data, version_uid=None, format_type="json"):
        """Update the status of an EHR with the required version UID."""
        return await self.ehrs.update_ehr_status(ehr_id, status_data, version_uid, format_type)
    
    async def delete_ehr(self, ehr_id):
        """
        Delete an EHR using the admin API.
        
        This method uses the admin endpoint which requires admin privileges.
        It's primarily intended for testing and cleanup purposes.
        """
        return await self.ehrs.delete_ehr(ehr_id)

    # Query operations - delegated to query client
    
    async def execute_adhoc_query(self, query, query_parameters=None, format_type="json"):
        """
        Execute an ad-hoc AQL query against the EHRbase server.
        
        Args:
            query: The AQL query string to execute
            query_parameters: Optional parameters for the query
            format_type: Format type for the response (default: json)
            
        Returns:
            The query results
        """
        return await self.queries.execute_adhoc_query(query, query_parameters, format_type)
