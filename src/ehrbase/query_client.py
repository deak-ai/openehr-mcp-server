"""
EHRbase Query Client

This module provides a client for executing AQL queries against the EHRbase server.
It supports ad-hoc queries with optional parameters.
"""
import json
from typing import Dict, Any, Optional

from utils.logging_utils import get_logger
from ehrbase.http_client import EHRbaseHttpClient

class QueryClient:
    """
    Client for executing AQL queries against the EHRbase server.
    """
    
    def __init__(self, http_client: EHRbaseHttpClient):
        """
        Initialize the query client with an HTTP client.
        
        Args:
            http_client: The HTTP client to use for requests
        """
        self.http_client = http_client
        self.logger = get_logger("query_client")
    
    async def execute_adhoc_query(self, query: str, query_parameters: Optional[Dict[str, Any]] = None, format_type: str = "json"):
        """
        Execute an ad-hoc AQL query against the EHRbase server.
        
        Args:
            query: The AQL query string to execute
            query_parameters: Optional parameters for the query
            format_type: Format type for the response (default: json)
            
        Returns:
            The query results
        """
        self.logger.info(f"Executing ad-hoc query: {query}")
        
        # Create the query payload
        payload = {
            "q": query
        }
        
        # Add query parameters if provided
        if query_parameters:
            self.logger.info(f"With parameters: {query_parameters}")
            payload["query_parameters"] = query_parameters
        
        # POST to /openehr/v1/query/aql endpoint
        return await self.http_client.request(
            "openehr/v1/query/aql",
            method="POST",
            json_data=payload,
            format_type=format_type
        )
