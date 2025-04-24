"""
Simple integration test for the openEHR MCP Server.

This test validates template retrieval from the EHRbase server.
"""
import os
import sys
import asyncio
from pathlib import Path

# Add the src directory to the Python path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Import the EHRbase client
from ehrbase import EHRbaseClient

# Test configuration
EHRBASE_URL = os.environ.get("EHRBASE_URL", "http://localhost:8080/ehrbase/rest")


async def test_template_list():
    """Test retrieving the list of templates from the EHRbase server."""
    print(f"\n=== TESTING TEMPLATE RETRIEVAL ===")
    
    # Initialize the client
    ehrbase_client = EHRbaseClient()
    print(f"Using EHRbase URL: {ehrbase_client.http_client.base_url}")
    
    try:
        # Get template list
        templates = await ehrbase_client.get_template_list()
        print(f"Found {len(templates)} templates:")
        
        # Print each template
        for template in templates:
            template_id = template.get('template_id')
            created = template.get('created_timestamp', 'unknown date')
            print(f"  - {template_id} (created: {created})")
        
        # Check if we found any templates
        if len(templates) == 0:
            print("WARNING: No templates found. You may need to upload a template first.")
        else:
            print(f"Successfully retrieved {len(templates)} templates!")
            
        return templates
        
    except Exception as e:
        print(f"Error retrieving templates: {str(e)}")
        raise


if __name__ == "__main__":
    # Run the test directly
    templates = asyncio.run(test_template_list())
    print("\nTest completed successfully!")
