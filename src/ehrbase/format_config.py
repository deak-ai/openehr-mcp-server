"""
Format configuration for EHRbase API client.

This module provides configuration for JSON format modes in the EHRbase client,
supporting different serialization formats as specified in the openEHR specification.
"""
import os
from utils.logging_utils import get_logger

class FormatConfig:
    """
    Configuration for JSON format modes in EHRbase client.
    
    Supports three modes:
    - canonical: Uses application/json consistently
    - wt_flat: Uses web template format for templates and flat JSON for compositions
    - wt_structured: Uses web template format for templates and structured JSON for compositions
    """
    
    # Available JSON format modes
    CANONICAL = "canonical"
    WT_FLAT = "wt_flat"
    WT_STRUCTURED = "wt_structured"
    
    # Default format mode
    DEFAULT_FORMAT = WT_FLAT
    
    def __init__(self, json_format=None):
        """
        Initialize with the specified JSON format or default.
        
        Args:
            json_format: The JSON format mode to use (canonical, wt_flat, wt_structured)
                         If None, uses the value from EHRBASE_JSON_FORMAT env var or DEFAULT_FORMAT
        """
        self.logger = get_logger("format_config")
        
        # Get format from parameter, environment, or default
        if json_format:
            self.json_format = json_format
        else:
            env_format = os.environ.get("EHRBASE_JSON_FORMAT")
            if env_format in [self.CANONICAL, self.WT_FLAT, self.WT_STRUCTURED]:
                self.json_format = env_format
            else:
                self.json_format = self.DEFAULT_FORMAT
        
        self.logger.info(f"Using JSON format mode: {self.json_format}")
    
    def get_template_list_format(self, override_format=None):
        """
        Get the appropriate format type for template listing operations.
        
        Args:
            override_format: Optional format to override the configuration
            
        Returns:
            The format type string to use
        """
        if override_format:
            return override_format
            
        # Template listing always uses json format regardless of the mode
        return "json"
    
    def get_template_format(self, override_format=None):
        """
        Get the appropriate format type for template retrieval operations.
        
        Args:
            override_format: Optional format to override the configuration
            
        Returns:
            The format type string to use
        """
        if override_format:
            return override_format
            
        if self.json_format == self.CANONICAL:
            return "json"
        else:  # Both wt_flat and wt_structured use the same template format
            return "web_template"
    
    def get_composition_format(self, override_format=None):
        """
        Get the appropriate format type for composition operations.
        
        Args:
            override_format: Optional format to override the configuration
            
        Returns:
            The format type string to use
        """
        if override_format:
            return override_format
            
        if self.json_format == self.CANONICAL:
            return "json"
        elif self.json_format == self.WT_FLAT:
            return "flat_json"
        elif self.json_format == self.WT_STRUCTURED:
            return "structured_json"
        return "flat_json"  # Default
    
    def get_ehr_format(self, override_format=None):
        """
        Get the appropriate format type for EHR operations.
        
        Args:
            override_format: Optional format to override the configuration
            
        Returns:
            The format type string to use
        """
        if override_format:
            return override_format
        return "json"  # Always json for EHR operations
    
    def get_query_format(self, override_format=None):
        """
        Get the appropriate format type for query operations.
        
        Args:
            override_format: Optional format to override the configuration
            
        Returns:
            The format type string to use
        """
        if override_format:
            return override_format
        return "json"  # Always json for query operations
