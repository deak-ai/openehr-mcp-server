"""
Template operations client for the EHRbase API.

This module provides specialized client functionality for template operations:
- Listing templates
- Retrieving template details
- Generating example compositions from templates
"""
from utils.logging_utils import get_logger
from .http_client import EHRbaseHttpClient

class TemplateClient:
    """Client for template-related operations against the EHRbase API."""
    
    def __init__(self, http_client=None):
        """
        Initialize the Template Client.
        
        Args:
            http_client: An optional EHRbaseHttpClient instance for making HTTP requests.
                         If not provided, a new instance will be created.
        """
        self.logger = get_logger("template_client")
        self.http_client = http_client or EHRbaseHttpClient()
    
    async def list_templates(self, format_type="json"):
        """
        List all available templates in EHRbase.
        
        Args:
            format_type: Format type for the response (default: json)
            
        Returns:
            A list of templates
        """
        self.logger.info("Listing all templates")
        return await self.http_client.request(
            "openehr/v1/definition/template/adl1.4",
            format_type=format_type
        )
    
    async def get_template(self, template_id, format_type="web_template"):
        """
        Get a specific template by ID.
        
        Args:
            template_id: The ID of the template to retrieve
            format_type: Format type for the response (default: web_template)
            
        Returns:
            The template data
        """
        self.logger.info(f"Retrieving template {template_id}")
        return await self.http_client.request(
            f"openehr/v1/definition/template/adl1.4/{template_id}",
            format_type=format_type
        )
    
    async def get_example_composition(self, template_id, format_type="flat_json"):
        """
        Generate an example composition based on a template.
        
        Args:
            template_id: The ID of the template to use
            format_type: Format type for the response (default: flat_json)
            
        Returns:
            An example composition
        """
        self.logger.info(f"Generating example composition for template {template_id}")
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
