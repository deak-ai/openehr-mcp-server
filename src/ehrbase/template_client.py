"""
Template operations client for the EHRbase API.

This module provides specialized client functionality for template operations:
- Listing templates
- Retrieving template details
- Generating example compositions from templates
"""
from utils.logging_utils import get_logger
from .http_client import EHRbaseHttpClient
from .format_config import FormatConfig

class TemplateClient:
    """Client for template-related operations against the EHRbase API."""
    
    def __init__(self, http_client=None, format_config=None):
        """
        Initialize the Template Client.
        
        Args:
            http_client: An optional EHRbaseHttpClient instance for making HTTP requests.
                         If not provided, a new instance will be created.
            format_config: Configuration for JSON format modes
        """
        self.logger = get_logger("template_client")
        self.http_client = http_client or EHRbaseHttpClient()
        self.format_config = format_config or FormatConfig()
    
    async def list_templates(self, format_type=None):
        """
        List all available templates in EHRbase.
        
        Args:
            format_type: Format type for the response (optional, uses configuration if not provided)
            
        Returns:
            A list of templates
        """
        self.logger.info("Listing all templates")
        format_type = self.format_config.get_template_list_format(format_type)
        return await self.http_client.request(
            "openehr/v1/definition/template/adl1.4",
            format_type=format_type
        )
    
    async def get_template(self, template_id, format_type=None):
        """
        Get a specific template by ID.
        
        Args:
            template_id: The ID of the template to retrieve
            format_type: Format type for the response (optional, uses configuration if not provided)
            
        Returns:
            The template data
        """
        self.logger.info(f"Retrieving template {template_id}")
        format_type = self.format_config.get_template_format(format_type)
        return await self.http_client.request(
            f"openehr/v1/definition/template/adl1.4/{template_id}",
            format_type=format_type
        )
    
    async def get_example_composition(self, template_id, format_type=None):
        """
        Generate an example composition based on a template.
        
        Args:
            template_id: The ID of the template to use
            format_type: Format type for the response (optional, uses configuration if not provided)
            
        Returns:
            An example composition
        """
        self.logger.info(f"Generating example composition for template {template_id}")
        format_type = self.format_config.get_composition_format(format_type)
        return await self.http_client.request(
            f"openehr/v1/definition/template/adl1.4/{template_id}/example",
            format_type=format_type
        )
    
    async def upload_template(self, template_path):
        """
        Upload an operational template (OPT) to EHRbase.
        
        Args:
            template_path: Path to the OPT file to upload
            
        Returns:
            The response from the template upload operation
        """
        self.logger.info(f"Reading template from file: {template_path}")
        with open(template_path, 'r', encoding='utf-8') as file:
            template_content = file.read()
        
        self.logger.info("Uploading template to EHRbase")
        
        # Use the HTTP client to make the request with raw XML content
        return await self.http_client.request(
            "openehr/v1/definition/template/adl1.4",
            method="POST",
            content=template_content,
            format_type="xml"
        )
