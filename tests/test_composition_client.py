"""
Integration test for openEHR composition operations using the CompositionClient.

This test validates the complete composition lifecycle (create, update, delete) 
in a single integrated test flow, ensuring all operations work correctly and
no resources are left behind on the EHRbase server.
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

# Template ID for testing
VITAL_SIGNS_TEMPLATE_ID = "vital_signs_basic.v1"

@pytest.mark.asyncio
async def test_composition_lifecycle():
    """
    Test the complete composition lifecycle in a single test.
    
    This test validates:
    1. Creating a new EHR to use for the test
    2. Creating a new composition with vital signs data
    3. Updating the same composition with modified vital signs
    4. Deleting the composition
    5. Deleting the EHR
    
    All operations use the same composition and EHR to ensure a clean test that
    doesn't leave test data on the server.
    """
    # PART 0: CREATE A NEW EHR FOR TESTING
    print("\n=== CREATING TEST EHR ===")
    
    # Create a simple EHR for testing
    ehr_response = await ehrbase_client.create_ehr()
    
    # Verify we received a valid response
    assert ehr_response is not None, "No EHR creation response received"
    assert "ehr_id" in ehr_response, f"Expected 'ehr_id' in response: {ehr_response}"
    
    # Store the EHR ID for subsequent operations
    ehr_id = ehr_response["ehr_id"]
    print(f"Successfully created test EHR with ID: {ehr_id}")
    
    # PART 1: CREATE A NEW COMPOSITION
    print("\n=== TESTING COMPOSITION CREATION ===")
    
    # Create flat JSON composition data for vital signs
    composition_data = {
        f"{VITAL_SIGNS_TEMPLATE_ID}/category|code": "433",
        f"{VITAL_SIGNS_TEMPLATE_ID}/category|value": "event",
        f"{VITAL_SIGNS_TEMPLATE_ID}/category|terminology": "openehr",
        f"{VITAL_SIGNS_TEMPLATE_ID}/context/start_time": "2025-04-14T00:00:00",
        f"{VITAL_SIGNS_TEMPLATE_ID}/context/setting|code": "225",
        f"{VITAL_SIGNS_TEMPLATE_ID}/context/setting|value": "home",
        f"{VITAL_SIGNS_TEMPLATE_ID}/context/setting|terminology": "openehr",
        
        # Pulse/heart rate data
        f"{VITAL_SIGNS_TEMPLATE_ID}/pulse_heart_beat/rate|magnitude": 62.0,
        f"{VITAL_SIGNS_TEMPLATE_ID}/pulse_heart_beat/rate|unit": "/min",
        f"{VITAL_SIGNS_TEMPLATE_ID}/pulse_heart_beat/time": "2025-04-14T00:00:00",
        f"{VITAL_SIGNS_TEMPLATE_ID}/pulse_heart_beat/language|code": "en",
        f"{VITAL_SIGNS_TEMPLATE_ID}/pulse_heart_beat/language|terminology": "ISO_639-1",
        f"{VITAL_SIGNS_TEMPLATE_ID}/pulse_heart_beat/encoding|code": "UTF-8",
        f"{VITAL_SIGNS_TEMPLATE_ID}/pulse_heart_beat/encoding|terminology": "IANA_character-sets",
        
        # Blood pressure data
        f"{VITAL_SIGNS_TEMPLATE_ID}/blood_pressure/systolic|magnitude": 128.0,
        f"{VITAL_SIGNS_TEMPLATE_ID}/blood_pressure/systolic|unit": "mm[Hg]",
        f"{VITAL_SIGNS_TEMPLATE_ID}/blood_pressure/diastolic|magnitude": 80.0,
        f"{VITAL_SIGNS_TEMPLATE_ID}/blood_pressure/diastolic|unit": "mm[Hg]",
        f"{VITAL_SIGNS_TEMPLATE_ID}/blood_pressure/time": "2025-04-14T00:00:00",
        f"{VITAL_SIGNS_TEMPLATE_ID}/blood_pressure/language|code": "en",
        f"{VITAL_SIGNS_TEMPLATE_ID}/blood_pressure/language|terminology": "ISO_639-1",
        f"{VITAL_SIGNS_TEMPLATE_ID}/blood_pressure/encoding|terminology": "IANA_character-sets",
        f"{VITAL_SIGNS_TEMPLATE_ID}/blood_pressure/encoding|code": "UTF-8",
        
        # SpO2 data
        f"{VITAL_SIGNS_TEMPLATE_ID}/pulse_oximetry/spo": 0.99,
        f"{VITAL_SIGNS_TEMPLATE_ID}/pulse_oximetry/spo|type": 3,
        f"{VITAL_SIGNS_TEMPLATE_ID}/pulse_oximetry/spo|numerator": 99.0,
        f"{VITAL_SIGNS_TEMPLATE_ID}/pulse_oximetry/spo|denominator": 100.0,
        f"{VITAL_SIGNS_TEMPLATE_ID}/pulse_oximetry/time": "2025-04-14T00:00:00",
        f"{VITAL_SIGNS_TEMPLATE_ID}/pulse_oximetry/language|code": "en",
        f"{VITAL_SIGNS_TEMPLATE_ID}/pulse_oximetry/language|terminology": "ISO_639-1",
        f"{VITAL_SIGNS_TEMPLATE_ID}/pulse_oximetry/encoding|code": "UTF-8",
        f"{VITAL_SIGNS_TEMPLATE_ID}/pulse_oximetry/encoding|terminology": "IANA_character-sets",
        
        # Height data
        f"{VITAL_SIGNS_TEMPLATE_ID}/height_length/height_length|magnitude": 192.0,
        f"{VITAL_SIGNS_TEMPLATE_ID}/height_length/height_length|unit": "cm",
        f"{VITAL_SIGNS_TEMPLATE_ID}/height_length/time": "2025-04-14T00:00:00",
        f"{VITAL_SIGNS_TEMPLATE_ID}/height_length/language|code": "en",
        f"{VITAL_SIGNS_TEMPLATE_ID}/height_length/language|terminology": "ISO_639-1",
        f"{VITAL_SIGNS_TEMPLATE_ID}/height_length/encoding|code": "UTF-8",
        f"{VITAL_SIGNS_TEMPLATE_ID}/height_length/encoding|terminology": "IANA_character-sets",
        
        # Weight data
        f"{VITAL_SIGNS_TEMPLATE_ID}/body_weight/weight|magnitude": 84.0,
        f"{VITAL_SIGNS_TEMPLATE_ID}/body_weight/weight|unit": "kg",
        f"{VITAL_SIGNS_TEMPLATE_ID}/body_weight/time": "2025-04-14T00:00:00",
        f"{VITAL_SIGNS_TEMPLATE_ID}/body_weight/language|code": "en",
        f"{VITAL_SIGNS_TEMPLATE_ID}/body_weight/language|terminology": "ISO_639-1",
        f"{VITAL_SIGNS_TEMPLATE_ID}/body_weight/encoding|code": "UTF-8",
        f"{VITAL_SIGNS_TEMPLATE_ID}/body_weight/encoding|terminology": "IANA_character-sets",
        
        # Required composition metadata
        f"{VITAL_SIGNS_TEMPLATE_ID}/language|code": "en",
        f"{VITAL_SIGNS_TEMPLATE_ID}/language|terminology": "ISO_639-1",
        f"{VITAL_SIGNS_TEMPLATE_ID}/territory|terminology": "ISO_3166-1",
        f"{VITAL_SIGNS_TEMPLATE_ID}/territory|code": "US",
        f"{VITAL_SIGNS_TEMPLATE_ID}/composer|name": "Test User"
    }
    
    # Create the composition using the client
    create_response = await ehrbase_client.create_composition(
        ehr_id, 
        composition_data
    )
    
    # Basic validation of the create response
    assert create_response is not None, "No composition creation response received"
    
    # Extract and validate the composition UID
    uid_key = f"{VITAL_SIGNS_TEMPLATE_ID}/_uid"
    assert uid_key in create_response, f"Expected {uid_key} in response, got: {list(create_response.keys())}"
    composition_uid = create_response[uid_key]
    
    # Validate heart rate value in the created composition
    heart_rate_key = f"{VITAL_SIGNS_TEMPLATE_ID}/pulse_heart_beat/rate|magnitude"
    assert heart_rate_key in create_response, f"Expected {heart_rate_key} in response"
    assert create_response[heart_rate_key] == 62.0, "Expected heart rate to be 62.0"
    
    print(f"Successfully created composition with UID: {composition_uid}")
    
    # PART 2: UPDATE THE COMPOSITION
    print("\n=== TESTING COMPOSITION UPDATE ===")
    
    # Create updated data with modified vital signs
    update_data = composition_data.copy()
    update_data[f"{VITAL_SIGNS_TEMPLATE_ID}/pulse_heart_beat/rate|magnitude"] = 70.0  # Changed from 62
    update_data[f"{VITAL_SIGNS_TEMPLATE_ID}/blood_pressure/systolic|magnitude"] = 130.0  # Changed from 128
    update_data[f"{VITAL_SIGNS_TEMPLATE_ID}/blood_pressure/diastolic|magnitude"] = 85.0  # Changed from 80
    
    # Update the composition
    update_response = await ehrbase_client.update_composition(
        ehr_id, 
        composition_uid, 
        update_data
    )
    
    # Basic validation of the update response
    assert update_response is not None, "No composition update response received"
    
    # Ensure the UID was updated (should have a new version)
    assert uid_key in update_response, f"Expected {uid_key} in update response"
    updated_uid = update_response[uid_key]
    assert updated_uid != composition_uid, "Expected new version UID after update"
    
    # Validate the updated heart rate
    assert heart_rate_key in update_response, f"Expected {heart_rate_key} in update response"
    assert update_response[heart_rate_key] == 70.0, f"Expected updated heart rate to be 70.0, got {update_response[heart_rate_key]}"
    
    # Validate the updated blood pressure
    systolic_key = f"{VITAL_SIGNS_TEMPLATE_ID}/blood_pressure/systolic|magnitude"
    diastolic_key = f"{VITAL_SIGNS_TEMPLATE_ID}/blood_pressure/diastolic|magnitude"
    
    assert systolic_key in update_response, f"Expected {systolic_key} in update response"
    assert update_response[systolic_key] == 130.0, f"Expected systolic to be 130.0, got {update_response[systolic_key]}"
    
    assert diastolic_key in update_response, f"Expected {diastolic_key} in update response"
    assert update_response[diastolic_key] == 85.0, f"Expected diastolic to be 85.0, got {update_response[diastolic_key]}"
    
    print(f"Successfully updated composition, new UID: {updated_uid}")
    
    # PART 3: DELETE THE COMPOSITION
    print("\n=== TESTING COMPOSITION DELETION ===")
    
    # Delete using the updated composition UID
    delete_response = await ehrbase_client.delete_composition(
        ehr_id, 
        updated_uid
    )
    
    # Verify deletion was successful
    assert isinstance(delete_response, dict), f"Expected dict response, got {type(delete_response)}"
    assert "status" in delete_response, f"Expected 'status' in response: {delete_response}"
    assert delete_response["status"] == "success", f"Deletion failed: {delete_response}"
    
    print("Successfully deleted composition")
    
    # PART 4: DELETE THE TEST EHR
    print("\n=== CLEANING UP - DELETING TEST EHR ===")
    
    # Delete the EHR using the admin API
    delete_ehr_result = await ehrbase_client.delete_ehr(ehr_id)
    
    # Verify the deletion was successful
    assert delete_ehr_result is True, f"Failed to delete EHR with ID {ehr_id}"
    print(f"Successfully deleted test EHR with ID: {ehr_id}")
    
    # Verify the EHR is no longer accessible
    try:
        # Try to get the deleted EHR
        verification_response = await ehrbase_client.get_ehr(ehr_id)
        assert False, f"Expected 404 error when getting deleted EHR, but got response: {verification_response}"
    except Exception as e:
        # We expect an exception
        print(f"Got expected exception when getting deleted EHR: {str(e)}")
        assert "404" in str(e) or "Not Found" in str(e), f"Expected 404 Not Found error, got: {str(e)}"
    
    print("Successfully verified that the EHR was deleted")
    print("\n=== COMPOSITION LIFECYCLE TEST COMPLETED SUCCESSFULLY ===")
    return True

@pytest.mark.asyncio
async def test_composition_from_template_example():
    """
    Test creating a composition using an example generated from the template.
    
    This test demonstrates the integration between template and composition operations
    and exercises the workflow a client would typically use:
    1. Create a new EHR for testing
    2. Get example composition from template
    3. Modify the example with custom values
    4. Create a composition with the modified example
    5. Clean up by deleting the composition
    6. Clean up by deleting the EHR
    """
    # PART 0: CREATE A NEW EHR FOR TESTING
    print("\n=== CREATING TEST EHR ===")
    
    # Create a simple EHR for testing
    ehr_response = await ehrbase_client.create_ehr()
    
    # Verify we received a valid response
    assert ehr_response is not None, "No EHR creation response received"
    assert "ehr_id" in ehr_response, f"Expected 'ehr_id' in response: {ehr_response}"
    
    # Store the EHR ID for subsequent operations
    ehr_id = ehr_response["ehr_id"]
    print(f"Successfully created test EHR with ID: {ehr_id}")
    
    print("\n=== TESTING COMPOSITION FROM TEMPLATE EXAMPLE ===")
    
    # Step 1: Generate example composition from template
    example = await ehrbase_client.get_template_example(VITAL_SIGNS_TEMPLATE_ID)
    
    # Verify we received a valid example
    assert example is not None, "No example composition received"
    assert isinstance(example, dict), f"Expected dictionary for example, got {type(example)}"
    
    # Step 2: Find and modify vital signs values in the example
    modified_example = example.copy()
    
    # Find keys containing vital signs elements (search by pattern)
    for key in modified_example.keys():
        if "pulse_heart_beat/rate|magnitude" in key:
            modified_example[key] = 75.0  # Set heart rate to 75 bpm
        elif "blood_pressure/systolic|magnitude" in key:
            modified_example[key] = 125.0  # Set systolic BP to 125 mmHg
        elif "blood_pressure/diastolic|magnitude" in key:
            modified_example[key] = 82.0  # Set diastolic BP to 82 mmHg
        elif "pulse_oximetry/spo|numerator" in key:
            modified_example[key] = 98.0  # Set SpO2 to 98%
    
    # Step 3: Create composition with the modified example
    create_response = await ehrbase_client.create_composition(
        ehr_id, 
        modified_example
    )
    
    # Verify we received a valid response
    assert create_response is not None, "No composition creation response received"
    
    # Extract the composition UID for deletion
    uid_key = None
    for key in create_response.keys():
        if key.endswith("/_uid"):
            uid_key = key
            break
    
    assert uid_key is not None, "Could not find _uid key in response"
    composition_uid = create_response[uid_key]
    print(f"Successfully created composition with UID: {composition_uid}")
    
    # Step 4: Delete the composition to clean up
    delete_response = await ehrbase_client.delete_composition(
        ehr_id, 
        composition_uid
    )
    
    # Verify deletion was successful
    assert isinstance(delete_response, dict), f"Expected dict response, got {type(delete_response)}"
    assert "status" in delete_response, f"Expected 'status' in response: {delete_response}"
    assert delete_response["status"] == "success", f"Deletion failed: {delete_response}"
    
    print("Successfully deleted composition")
    
    # PART 5: DELETE THE TEST EHR
    print("\n=== CLEANING UP - DELETING TEST EHR ===")
    
    # Delete the EHR using the admin API
    delete_ehr_result = await ehrbase_client.delete_ehr(ehr_id)
    
    # Verify the deletion was successful
    assert delete_ehr_result is True, f"Failed to delete EHR with ID {ehr_id}"
    print(f"Successfully deleted test EHR with ID: {ehr_id}")
    
    print("\n=== TEMPLATE EXAMPLE TEST COMPLETED SUCCESSFULLY ===")
    return True

if __name__ == "__main__":
    # Execute the tests directly for debugging
    asyncio.run(test_composition_lifecycle())
    asyncio.run(test_composition_from_template_example())
