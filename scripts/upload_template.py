#!/usr/bin/env python
"""
Initialize EHRbase environment by uploading templates.

This script uploads the vital signs template to the EHRbase server.
"""
import os
import sys
import asyncio
import argparse
from pathlib import Path

# Add the src directory to the Python path
# This mimics the Docker environment where PYTHONPATH=/app and src is in /app/src
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Now we can import using the same style as in the Docker environment
from ehrbase.template_client import TemplateClient
from utils.logging_utils import get_logger

logger = get_logger("initialize_templates")

async def main():
    """Upload the vital signs template to EHRbase."""
    parser = argparse.ArgumentParser(description="Upload vital signs template to EHRbase")
    parser.add_argument("--ehrbase-url", help="EHRbase URL (defaults to EHRBASE_URL environment variable)")
    parser.add_argument("--template", help="Path to template file (defaults to vital_signs_basic.opt)")
    args = parser.parse_args()
    
    # Initialize template client
    template_client = TemplateClient()
    
    # Override base URL if provided
    if args.ehrbase_url:
        template_client.http_client.base_url = args.ehrbase_url
        
    logger.info(f"Using EHRbase URL: {template_client.http_client.base_url}")
    
    # Path to the vital signs template
    if args.template:
        template_path = Path(args.template)
    else:
        # Default to the vital signs template in the resources directory
        template_path = Path(__file__).parent.parent / "resources" / "vital_signs_basic.opt"
    
    if not template_path.exists():
        logger.error(f"Template file not found: {template_path}")
        return 1
    
    try:
        logger.info(f"Uploading template: {template_path}")
        response = await template_client.upload_template(str(template_path))
        logger.info("Template upload successful")
        return 0
    except Exception as e:
        logger.error(f"Failed to upload template: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
