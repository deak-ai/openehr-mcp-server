"""
Composition operations client for the EHRbase API.

This module provides specialized client functionality for composition operations:
- Creating compositions
- Retrieving compositions
- Updating compositions
- Deleting compositions
"""
from utils.logging_utils import get_logger
from .http_client import EHRbaseHttpClient

class CompositionClient:
    """Client for composition-related operations against the EHRbase API."""
    
    def __init__(self, http_client=None):
        """
        Initialize the Composition Client.
        
        Args:
            http_client: An optional EHRbaseHttpClient instance for making HTTP requests.
                         If not provided, a new instance will be created.
        """
        self.logger = get_logger("composition_client")
        self.http_client = http_client or EHRbaseHttpClient()
    
    def _extract_template_id(self, composition_data):
        """
        Extract template ID from composition data.
        
        Args:
            composition_data: The composition data
            
        Returns:
            The extracted template ID or None
        """
        if isinstance(composition_data, dict) and composition_data:
            # The template ID is the first part of any key (before the first '/')
            first_key = next(iter(composition_data.keys()))
            if '/' in first_key:
                template_id = first_key.split('/')[0]
                self.logger.info(f"Extracted template ID from composition data: {template_id}")
                return template_id
        return None
    
    async def create_composition(self, ehr_id, composition_data, format_type="flat_json", template_id=None):
        """
        Create a new composition in the EHR.
        
        Args:
            ehr_id: The EHR ID to create the composition in
            composition_data: The composition data to create
            format_type: Format type for the request/response (default: flat_json)
            template_id: Optional template ID, will be extracted from composition_data if not provided
            
        Returns:
            The created composition response
        """
        self.logger.info(f"Creating composition for EHR {ehr_id}")
        
        # Extract template ID from composition data if not provided
        if template_id is None:
            template_id = self._extract_template_id(composition_data)
        
        return await self.http_client.request(
            f"openehr/v1/ehr/{ehr_id}/composition",
            method="POST",
            json_data=composition_data,
            format_type=format_type,
            template_id=template_id
        )
    
    async def get_composition(self, ehr_id, composition_uid, format_type="flat_json"):
        """
        Get a composition by its UID.
        
        Args:
            ehr_id: The EHR ID containing the composition
            composition_uid: The composition's versioned object UID
            format_type: Format type for the response (default: flat_json)
            
        Returns:
            The composition data
        """
        self.logger.info(f"Retrieving composition {composition_uid} from EHR {ehr_id}")
        return await self.http_client.request(
            f"openehr/v1/ehr/{ehr_id}/composition/{composition_uid}",
            format_type=format_type
        )
    
    async def update_composition(self, ehr_id, composition_uid, composition_data, format_type="flat_json", template_id=None):
        """
        Update an existing composition.
        
        Args:
            ehr_id: The EHR ID containing the composition
            composition_uid: The composition's versioned object UID
            composition_data: The updated composition data
            format_type: Format type for the request/response (default: flat_json)
            template_id: Optional template ID, will be extracted from composition_data if not provided
            
        Returns:
            The updated composition response
        """
        self.logger.info(f"Updating composition {composition_uid} in EHR {ehr_id}")
        
        # Extract template ID from composition data if not provided
        if template_id is None:
            template_id = self._extract_template_id(composition_data)
        
        # Extract the versioned_object_uid (the part before the first ::)
        # This is needed for the URL path
        versioned_object_uid = composition_uid
        if "::" in composition_uid:
            versioned_object_uid = composition_uid.split("::")[0]
            self.logger.info(f"Extracted versioned_object_uid: {versioned_object_uid}")
        
        return await self.http_client.request(
            f"openehr/v1/ehr/{ehr_id}/composition/{versioned_object_uid}",  # Use versioned_object_uid in URL path
            method="PUT",
            json_data=composition_data,
            format_type=format_type,
            template_id=template_id,
            version_uid=composition_uid  # Pass the full composition_uid as version_uid for If-Match header
        )
    
    async def delete_composition(self, ehr_id, composition_uid, format_type="flat_json"):
        """
        Delete a composition.
        
        Args:
            ehr_id: The EHR ID containing the composition
            composition_uid: The composition's UID (can be full version UID or versioned object UID)
            format_type: Format type for the request (default: flat_json)
            
        Returns:
            Success status
        """
        self.logger.info(f"Deleting composition {composition_uid} from EHR {ehr_id}")
        return await self.http_client.request(
            f"openehr/v1/ehr/{ehr_id}/composition/{composition_uid}",
            method="DELETE",
            format_type=format_type
        )
