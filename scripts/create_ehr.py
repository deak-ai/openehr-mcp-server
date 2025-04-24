#!/usr/bin/env python
"""
Create a new EHR in the EHRbase server.

This script creates a new Electronic Health Record (EHR) in the EHRbase server
with a specified subject ID or a randomly generated one.
"""
import os
import sys
import asyncio
import argparse
import json
import uuid
from pathlib import Path

# Add the src directory to the Python path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Import the EHRbase client
from ehrbase import EHRbaseClient

async def main():
    """Create a new EHR in the EHRbase server."""
    parser = argparse.ArgumentParser(description="Create a new EHR in the EHRbase server")
    parser.add_argument("--ehrbase-url", help="EHRbase URL (defaults to EHRBASE_URL environment variable)")
    parser.add_argument("--subject-id", help="Subject ID for the EHR (defaults to a random UUID)")
    parser.add_argument("--namespace", default="EHR", help="Subject namespace (defaults to 'EHR')")
    parser.add_argument("--scheme", default="http://hl7.org/fhir/Patient", help="ID scheme (defaults to 'http://hl7.org/fhir/Patient')")
    args = parser.parse_args()
    
    # Initialize EHRbase client
    ehrbase_client = EHRbaseClient()
    
    # Override base URL if provided
    if args.ehrbase_url:
        ehrbase_client.http_client.base_url = args.ehrbase_url
    
    print(f"Using EHRbase URL: {ehrbase_client.http_client.base_url}")
    
    # Use provided subject ID or generate a random one
    subject_id = args.subject_id or f"test_subject_{uuid.uuid4()}"
    
    # Create a simple EHR status with a subject ID (following test_ehr_client.py approach)
    ehr_status = {
        "_type": "EHR_STATUS",
        "archetype_node_id": "openEHR-EHR-EHR_STATUS.generic.v1",
        "name": {
            "value": "ehr status"
        },
        "subject": {
            "external_ref": {
                "id": {
                    "_type": "GENERIC_ID",
                    "value": subject_id,
                    "scheme": args.scheme
                },
                "namespace": args.namespace,
                "type": "PERSON"
            }
        },
        "is_modifiable": "true",
        "is_queryable": "true"
    }
    
    try:
        print(f"\n=== CREATING NEW EHR ===")
        print(f"Subject ID: {subject_id}")
        print(f"Namespace: {args.namespace}")
        
        # Create the EHR
        create_response = await ehrbase_client.create_ehr(ehr_status)
        
        # Pretty print the response
        print(f"\nCreate EHR response: {json.dumps(create_response, indent=2)}")
        
        # Extract the EHR ID
        ehr_id = create_response.get("ehr_id", {}).get("value") if isinstance(create_response.get("ehr_id"), dict) else create_response.get("ehr_id")
        
        print(f"\nSuccessfully created EHR with ID: {ehr_id}")
        print(f"\nUse this EHR ID when creating compositions or querying the EHR.")
        
        return 0
    except Exception as e:
        print(f"Error creating EHR: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
