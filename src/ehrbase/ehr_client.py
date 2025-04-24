"""
EHR operations client for the EHRbase API.

This module provides specialized client functionality for EHR operations:
- Creating EHRs
- Retrieving EHRs
- Listing EHRs
- Managing EHR status
"""
from utils.logging_utils import get_logger
from .http_client import EHRbaseHttpClient

class EHRClient:
    """Client for EHR-related operations against the EHRbase API."""
    
    def __init__(self, http_client=None):
        """
        Initialize the EHR Client.
        
        Args:
            http_client: An optional EHRbaseHttpClient instance for making HTTP requests.
                         If not provided, a new instance will be created.
        """
        self.logger = get_logger("ehr_client")
        self.http_client = http_client or EHRbaseHttpClient()
    
    async def create_ehr(self, ehr_status=None, format_type="json"):
        """
        Create a new EHR in the system.
        
        Args:
            ehr_status: Optional EHR status document as a dict
            format_type: Format type for the response (default: json)
            
        Returns:
            The created EHR data including the EHR ID
        """
        self.logger.info("Creating new EHR")
        
        # POST to /openehr/v1/ehr endpoint
        return await self.http_client.request(
            "openehr/v1/ehr",
            method="POST",
            json_data=ehr_status,
            format_type=format_type
        )
    
    async def get_ehr(self, ehr_id, format_type="json"):
        """
        Get an EHR by its ID.
        
        Args:
            ehr_id: The ID of the EHR to retrieve
            format_type: Format type for the response (default: json)
            
        Returns:
            The EHR data
        """
        self.logger.info(f"Retrieving EHR with ID {ehr_id}")
        
        # GET to /openehr/v1/ehr/{ehr_id} endpoint
        return await self.http_client.request(
            f"openehr/v1/ehr/{ehr_id}",
            format_type=format_type
        )
    
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
        if not subject_id or not subject_namespace:
            raise ValueError("Both subject_id and subject_namespace are required")
            
        self.logger.info(f"Getting EHR for subject {subject_id} in namespace {subject_namespace}")
        params = {
            "subject_id": subject_id,
            "subject_namespace": subject_namespace
        }
        
        # GET to /openehr/v1/ehr endpoint with subject query parameters
        return await self.http_client.request(
            "openehr/v1/ehr",
            params=params,
            format_type=format_type
        )
    
    async def get_ehr_status(self, ehr_id, format_type="json"):
        """
        Get the status of an EHR.
        
        Args:
            ehr_id: The ID of the EHR
            format_type: Format type for the response (default: json)
            
        Returns:
            The EHR status data
        """
        self.logger.info(f"Retrieving status for EHR {ehr_id}")
        
        # GET to /openehr/v1/ehr/{ehr_id}/ehr_status endpoint
        return await self.http_client.request(
            f"openehr/v1/ehr/{ehr_id}/ehr_status",
            format_type=format_type
        )
    
    async def update_ehr_status(self, ehr_id, status_data, version_uid=None, format_type="json"):
        """
        Update the status of an EHR.
        
        Args:
            ehr_id: The ID of the EHR
            status_data: The updated EHR status data
            version_uid: The version UID for the If-Match header (required by the API)
            format_type: Format type for the response (default: json)
            
        Returns:
            The updated EHR status data
        """
        self.logger.info(f"Updating status for EHR {ehr_id}")
        
        # If version_uid is not provided, try to extract it from the status_data
        if not version_uid and status_data and "uid" in status_data:
            version_uid = status_data["uid"]["value"]
            self.logger.info(f"Extracted version UID from status data: {version_uid}")
        
        if not version_uid:
            raise ValueError("Version UID is required for updating EHR status")
        
        # PUT to /openehr/v1/ehr/{ehr_id}/ehr_status endpoint with If-Match header
        return await self.http_client.request(
            f"openehr/v1/ehr/{ehr_id}/ehr_status",
            method="PUT",
            json_data=status_data,
            version_uid=version_uid,
            format_type=format_type
        )
    
    async def delete_ehr(self, ehr_id):
        """
        Delete an EHR using the admin API.
        
        This method uses the admin endpoint which requires admin privileges.
        It's primarily intended for testing and cleanup purposes.
        
        Args:
            ehr_id: The ID of the EHR to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        self.logger.info(f"Deleting EHR with ID {ehr_id} using admin API")
        
        # DELETE to /admin/ehr/{ehr_id} endpoint
        try:
            response = await self.http_client.request(
                f"admin/ehr/{ehr_id}",
                method="DELETE"
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete EHR {ehr_id}: {str(e)}")
            return False
