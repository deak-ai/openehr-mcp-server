"""
Base HTTP client for EHRbase REST API communication.

This module provides the core HTTP functionality for communicating with the EHRbase API.
"""
import httpx
import json
import time
import os
from utils.logging_utils import get_logger, log_incoming_message, log_outgoing_message, format_message

class EHRbaseHttpClient:
    """Base client for making HTTP requests to the EHRbase REST API."""
    
    # Format headers definitions
    FORMAT_HEADERS = {
        "json": {
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        "xml": {
            "Accept": "application/xml",
            "Content-Type": "application/xml"
        },
        "web_template": {
            "Accept": "application/openehr.wt+json",
            "Content-Type": "application/json"
        },
        "flat_json": {
            "Accept": "application/openehr.wt.flat.schema+json",
            "Content-Type": "application/openehr.wt.flat.schema+json",
            "Prefer": "return=representation"
        },
        "structured_json": {
            "Accept": "application/openehr.wt.structured.schema+json",
            "Content-Type": "application/json"
        }
    }
    
    def __init__(self, base_url=None, default_ehr_id=None):
        """
        Initialize the EHRbase HTTP client.
        
        Args:
            base_url: The base URL of the EHRbase API (default from env var EHRBASE_URL)
            default_ehr_id: Default EHR ID to use (default from env var DEFAULT_EHR_ID)
        """
        self.logger = get_logger("ehrbase_http_client")
        self.base_url = base_url or os.environ.get("EHRBASE_URL", "http://localhost:8080/ehrbase/rest")
        self.default_ehr_id = default_ehr_id or os.environ.get("DEFAULT_EHR_ID")
        
        self.logger.info(f"Initialized EHRbaseHttpClient with URL: {self.base_url}")
    
    async def request(self, path, method="GET", json_data=None, content=None, format_type="json", template_id=None, version_uid=None, params=None):
        """
        Make a request to the EHRbase API.
        
        Args:
            path: The API path to request
            method: HTTP method (GET, POST, PUT, DELETE)
            json_data: Optional JSON data to send with the request
            content: Optional raw content string to send with the request
            format_type: Format type to use (json, xml, web_template, flat_json, structured_json)
            template_id: Optional template ID for composition operations
            version_uid: Optional version UID for If-Match header in PUT requests
            params: Optional dictionary of query parameters
            
        Returns:
            The JSON response from the API
        """
        # Build URL with query parameters if needed
        base_url = f"{self.base_url}/{path}"
        query_params = {}
        
        # Add templateId for composition operations with flat JSON format
        if template_id and ('composition' in path):
            query_params['templateId'] = template_id
        
        # Add any additional query parameters
        if params:
            query_params.update(params)
        
        # Build the final URL
        url = base_url
        
        # Get headers for the specified format
        headers = self.FORMAT_HEADERS.get(format_type, self.FORMAT_HEADERS["json"]).copy()
        
        # Add If-Match header for PUT requests if version_uid is provided
        if method == "PUT" and version_uid:
            headers["If-Match"] = version_uid
        
        # Log the outgoing request to EHRbase
        log_outgoing_message(self.logger, "EHRbase Request", 
                       path, 
                       method=method,
                       format=headers.get("Accept", "default"),
                       has_json=json_data is not None,
                       params=query_params if query_params else None)
        
        start_time = time.time()
        try:
            async with httpx.AsyncClient() as client:
                if method == "GET":
                    response = await client.get(url, headers=headers, params=query_params if query_params else None)
                elif method == "POST":
                    if content is not None:
                        response = await client.post(url, headers=headers, content=content, params=query_params if query_params else None)
                    else:
                        response = await client.post(url, headers=headers, json=json_data, params=query_params if query_params else None)
                elif method == "PUT":
                    response = await client.put(url, headers=headers, json=json_data, params=query_params if query_params else None)
                elif method == "DELETE":
                    response = await client.delete(url, headers=headers, params=query_params if query_params else None)
                
                response.raise_for_status()
                elapsed = time.time() - start_time
                
                # Handle 204 No Content responses (common for DELETE operations)
                if response.status_code == 204:
                    self.logger.info(f"EHRbase Response: No Content (204) after {elapsed:.2f}s")
                    return {"status": "success", "message": "Operation completed successfully"}
                
                # Handle 201 Created responses with empty body (common for POST operations)
                if response.status_code == 201 and not response.content.strip():
                    # Extract EHR ID from Location header if available
                    location = response.headers.get('Location', '')
                    ehr_id = location.split('/')[-1] if location else None
                    
                    result = {
                        "status": "success",
                        "message": "Resource created successfully",
                        "ehr_id": ehr_id
                    }
                    
                    self.logger.info(f"EHRbase Response: Created (201) with EHR ID {ehr_id} after {elapsed:.2f}s")
                    return result
                
                # For other successful responses, parse the JSON
                try:
                    result = response.json()
                except Exception as e:
                    self.logger.warning(f"Failed to parse JSON response: {str(e)}. Content: {response.content[:100]}...")
                    # Return a basic response with headers information
                    result = {
                        "status": "success",
                        "status_code": response.status_code,
                        "headers": dict(response.headers),
                        "content_type": response.headers.get('Content-Type', 'unknown'),
                        "content_length": len(response.content)
                    }
                
                # Log the response from EHRbase
                log_incoming_message(self.logger, "EHRbase Response", 
                                   format_message(str(result)), 
                                   status_code=response.status_code, 
                                   elapsed_seconds=f"{elapsed:.2f}s")
                return result
        except Exception as e:
            elapsed = time.time() - start_time
            self.logger.error(f"EHRbase request error: {path} - {str(e)} after {elapsed:.2f}s")
            raise
