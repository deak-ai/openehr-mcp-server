"""
Integration test for template operations using the TemplateClient.
This test directly validates template operations against the EHRbase server.
"""
import asyncio
import os
import json
import pytest
import sys
from datetime import datetime

# Add the parent directory to the path so we can import the src modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the EHRbaseClient
from src.ehrbase import EHRbaseClient

# Initialize the client
ehrbase_client = EHRbaseClient()

# Test constants
VITAL_SIGNS_TEMPLATE_ID = "vital_signs_basic.v1"

@pytest.mark.asyncio
async def test_list_templates():
    """Test listing available templates directly using the TemplateClient."""
    
    # List all templates using the client
    templates = await ehrbase_client.templates.list_templates()
    
    # Print the templates for debugging
    print(f"Templates response: {templates}")
    
    # Verify we received a valid response
    assert templates is not None, "No templates response received"
    assert isinstance(templates, list), f"Expected a list of templates, got {type(templates)}"
    
    # Check for expected template structure
    assert len(templates) > 0, "Expected at least one template in the response"
    
    # Find our vital signs template in the list
    vital_signs_found = False
    for template in templates:
        assert "template_id" in template, f"Expected 'template_id' in template data: {template}"
        if template["template_id"] == VITAL_SIGNS_TEMPLATE_ID:
            vital_signs_found = True
            break
    
    assert vital_signs_found, f"Expected to find {VITAL_SIGNS_TEMPLATE_ID} in templates list"
    
    print(f"Successfully retrieved {len(templates)} templates")
    return templates

@pytest.mark.asyncio
async def test_get_template():
    """Test retrieving a specific template by ID directly using the TemplateClient."""
    
    # Get the vital signs template using the client
    template = await ehrbase_client.templates.get_template(VITAL_SIGNS_TEMPLATE_ID)
    
    # Print template info for debugging
    print(f"Template response type: {type(template)}")
    
    # Verify we received a valid response
    assert template is not None, "No template response received"
    
    # Check that we have the expected template data
    # The response format will depend on the format requested (web_template)
    if isinstance(template, dict):
        # Check for common template elements
        expected_keys = ["tree", "templateId", "defaultLanguage"]
        for key in expected_keys:
            assert key in template, f"Expected '{key}' in template response"
        
        # Verify the template ID matches
        assert template["templateId"] == VITAL_SIGNS_TEMPLATE_ID, "Template ID mismatch"
        
        # Check for vital signs elements in the template
        vital_sign_components = ["pulse", "heart", "blood pressure", "oxygen", "height", "weight"]
        component_found = False
        template_str = json.dumps(template).lower()
        
        for component in vital_sign_components:
            if component in template_str:
                component_found = True
                print(f"Found vital sign component: {component}")
                break
                
        assert component_found, f"Expected at least one vital sign component in template: {vital_sign_components}"
    
    print(f"Successfully retrieved template: {VITAL_SIGNS_TEMPLATE_ID}")
    return template

@pytest.mark.asyncio
async def test_get_example_composition():
    """Test generating an example composition directly using the TemplateClient."""
    
    # Generate an example composition for the vital signs template
    example = await ehrbase_client.templates.get_example_composition(VITAL_SIGNS_TEMPLATE_ID)
    
    # Print example info for debugging
    print(f"Example response type: {type(example)}")
    
    # Verify we received a valid response
    assert example is not None, "No example composition response received"
    assert isinstance(example, dict), f"Expected a dictionary for example composition, got {type(example)}"
    
    # Check for expected format in the flat JSON example composition
    # Keys should contain the template ID
    template_prefix = f"{VITAL_SIGNS_TEMPLATE_ID}/"
    template_keys_found = False
    
    for key in example.keys():
        if key.startswith(template_prefix):
            template_keys_found = True
            break
    
    assert template_keys_found, f"Expected keys starting with '{template_prefix}' in example composition"
    
    # Check for vital signs components in the example
    vital_sign_fields = ["pulse_heart_beat", "blood_pressure", "pulse_oximetry", "height_length", "body_weight"]
    components_found = []
    
    for key in example.keys():
        for field in vital_sign_fields:
            if field in key and field not in components_found:
                components_found.append(field)
    
    assert len(components_found) > 0, f"Expected at least one vital sign component in example composition"
    print(f"Found vital sign components in example composition: {components_found}")
    
    print(f"Successfully generated example composition for template: {VITAL_SIGNS_TEMPLATE_ID}")
    return example

@pytest.mark.asyncio
async def test_get_template_not_found():
    """Test retrieving a non-existent template directly using the TemplateClient."""
    non_existent_id = "non_existent_template.v1"
    
    try:
        # Attempt to get a non-existent template
        template = await ehrbase_client.templates.get_template(non_existent_id)
        assert False, f"Expected exception when requesting non-existent template, but got response: {template}"
    except Exception as e:
        # We expect an exception when the template doesn't exist
        print(f"Got expected exception when requesting non-existent template: {e}")
        assert "404" in str(e) or "Not Found" in str(e), f"Expected 404 error for non-existent template, got: {e}"
    
    print(f"Successfully confirmed error handling for non-existent template")

if __name__ == "__main__":
    # Run the tests directly for debugging
    asyncio.run(test_list_templates())
    asyncio.run(test_get_template())
    asyncio.run(test_get_example_composition())
    asyncio.run(test_get_template_not_found())
