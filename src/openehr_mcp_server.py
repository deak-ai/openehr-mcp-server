from fastmcp import FastMCP
import json
import time
import os
import argparse
import sys

# Import custom logging utilities
from utils.logging_utils import get_logger

# Import the EHRbase client facade
from ehrbase import EHRbaseClient

# Import prompts
from mcp_prompts import register_prompts

# Get a logger for this module
logger = get_logger("openehr_mcp_server")

# Initialize the EHRbase client
ehrbase_client = EHRbaseClient()

# Get default EHR ID from client
DEFAULT_EHR_ID = ehrbase_client.default_ehr_id

# Initialize the MCP server with the official SDK
mcp = FastMCP("openEHR MCP Server")

# Register prompts and resources
mcp = register_prompts(mcp)
logger.info("Registered prompts and resources for the openEHR MCP Server")

# TRANSPORT PLUGIN SYSTEM
class TransportPlugin:
    """Base class for transport plugins."""
    
    def __init__(self, name: str):
        self.name = name
    
    def run(self, mcp_server, **kwargs):
        """Run the transport with the given MCP server."""
        raise NotImplementedError("Transport plugins must implement run()")

class StdioTransportPlugin(TransportPlugin):
    """Standard I/O transport plugin (default behavior)."""
    
    def __init__(self):
        super().__init__("stdio")
    
    def run(self, mcp_server, **kwargs):
        """Run the MCP server with stdio transport."""
        logger.info("Using stdio transport")
        mcp_server.run(transport='stdio')

# Global transport registry
_transport_plugins = {}

def register_transport_plugin(plugin: TransportPlugin):
    """Register a transport plugin."""
    _transport_plugins[plugin.name] = plugin
    logger.info(f"Registered transport plugin: {plugin.name}")

def get_transport_plugin(name: str) -> TransportPlugin:
    """Get a registered transport plugin by name."""
    return _transport_plugins.get(name)

def list_transport_plugins():
    """List all registered transport plugins."""
    return list(_transport_plugins.keys())

# Register the default stdio transport
register_transport_plugin(StdioTransportPlugin())

# TOOLS - Actions to perform with templates and EHRs
@mcp.tool()
async def openehr_template_list() -> str:
    """List all available openEHR templates from the EHRbase server.
    
    Returns a JSON array of available openEHR templates with their metadata. 
    These templates define the structure for clinical data compositions within the openEHR standard.
    
    Returns:
        JSON string containing the list of available openEHR templates
    """
    logger.info("MCP Tool call: openehr_template_list")
    start_time = time.time()
    
    try:
        # Get templates using the fixed formats in the client
        templates = await ehrbase_client.get_template_list()
        result = json.dumps(templates, indent=2)
        
        elapsed = time.time() - start_time
        count = len(templates) if isinstance(templates, list) else 'N/A'
        logger.info(f"Returning template list with {count} templates in {elapsed:.2f}s")
        return result
    except Exception as e:
        elapsed = time.time() - start_time
        error_msg = f"Error listing templates: {str(e)}"
        logger.error(f"{error_msg} after {elapsed:.2f}s")
        return error_msg

@mcp.tool()
async def openehr_template_get(template_id: str) -> str:
    """Retrieve a specific openEHR template by its unique identifier.
    
    Fetches the complete definition of an openEHR template, including all archetypes,
    constraints, and data point definitions. The template is returned in openEHR Web Template
    format, which can be used to understand the structure required for creating valid
    compositions based on this template.
    
    Args:
        template_id: The unique identifier of the openEHR template to retrieve
        
    Returns:
        JSON string containing the complete openEHR template definition
    """
    logger.info(f"MCP Tool call: openehr_template_get with ID {template_id}")
    start_time = time.time()
    
    try:
        # Get template using the fixed formats in the client
        template = await ehrbase_client.get_template(template_id)
        result = json.dumps(template, indent=2)
        
        elapsed = time.time() - start_time
        logger.info(f"Retrieved template {template_id} in {elapsed:.2f}s")
        return result
    except Exception as e:
        elapsed = time.time() - start_time
        error_msg = f"Error retrieving template {template_id}: {str(e)}"
        logger.error(f"{error_msg} after {elapsed:.2f}s")
        return error_msg

@mcp.tool()
async def openehr_template_example_composition(template_id: str) -> str:
    """Generate an example openEHR composition based on a specific template.
    
    Creates a sample openEHR composition that adheres to the structure defined in the
    specified template. This includes mock data for all required fields and demonstrates
    the proper format for creating valid compositions. The current implementation uses 
    the flat JSON representation (application/openehr.wt.flat.schema+json)
    
    Args:
        template_id: The unique identifier of the openEHR template to use for generating the example
        
    Returns:
        JSON string containing an example openEHR composition in flat JSON format
    """
    logger.info(f"MCP Tool call: openehr_template_example_composition for template {template_id}")
    start_time = time.time()
    
    try:
        # Get example composition using the fixed formats in the client
        example = await ehrbase_client.get_template_example(template_id)
        result = json.dumps(example, indent=2)
        
        elapsed = time.time() - start_time
        logger.info(f"Generated example composition for {template_id} in {elapsed:.2f}s")
        return result
    except Exception as e:
        elapsed = time.time() - start_time
        error_msg = f"Error generating example: {str(e)}"
        logger.error(f"{error_msg} after {elapsed:.2f}s")
        return error_msg


# EHR MANAGEMENT TOOLS
@mcp.tool()
async def openehr_ehr_create(ehr_status=None) -> str:
    """Create a new EHR in the system.
    
    Creates a new Electronic Health Record (EHR) in the EHRbase server. An EHR is a
    container for all health data about a single patient. The optional ehr_status
    parameter can be used to provide additional metadata about the EHR.
    
    Args:
        ehr_status: Optional EHR status document as JSON string or object
        
    Returns:
        JSON string containing the new EHR ID and creation response
    """
    logger.info(f"MCP Tool call: openehr_ehr_create")
    start_time = time.time()
    
    try:
        # Handle ehr_status as either string or dict
        status_json = None
        if ehr_status:
            if isinstance(ehr_status, str):
                try:
                    status_json = json.loads(ehr_status)
                except json.JSONDecodeError:
                    return f"Error: ehr_status must be a valid JSON string, received: {ehr_status}"
            else:
                # If it's already a dict/object, use it directly
                status_json = ehr_status
        
        # Create the EHR
        result = await ehrbase_client.create_ehr(status_json)
        response = json.dumps(result, indent=2)
        
        elapsed = time.time() - start_time
        logger.info(f"Created EHR in {elapsed:.2f}s with ID: {result.get('ehr_id', 'unknown')}")
        return response
    except Exception as e:
        elapsed = time.time() - start_time
        error_msg = f"Error creating EHR: {str(e)}"
        logger.error(f"{error_msg} after {elapsed:.2f}s")
        return error_msg

@mcp.tool()
async def openehr_ehr_get(ehr_id: str) -> str:
    """Retrieve an EHR by its ID.
    
    Fetches an existing Electronic Health Record (EHR) from the EHRbase server using
    its unique identifier. The EHR contains metadata about the patient record but not
    the actual clinical data (which is stored in compositions).
    
    Args:
        ehr_id: The unique identifier of the EHR to retrieve
        
    Returns:
        JSON string containing the EHR details
    """
    if not ehr_id:
        return "Error: No EHR ID provided"
        
    logger.info(f"MCP Tool call: openehr_ehr_get for EHR {ehr_id}")
    start_time = time.time()
    
    try:
        # Retrieve the EHR
        result = await ehrbase_client.get_ehr(ehr_id)
        response = json.dumps(result, indent=2)
        
        elapsed = time.time() - start_time
        logger.info(f"Retrieved EHR in {elapsed:.2f}s")
        return response
    except Exception as e:
        elapsed = time.time() - start_time
        error_msg = f"Error retrieving EHR: {str(e)}"
        logger.error(f"{error_msg} after {elapsed:.2f}s")
        return error_msg

@mcp.tool()
async def openehr_ehr_list() -> str:
    """List all available EHRs in the system.
    
    Retrieves a list of all Electronic Health Records (EHRs) available in the EHRbase server.
    This provides an overview of all patient records in the system without retrieving
    the detailed clinical data.
    
    Returns:
        JSON string containing the list of EHR IDs
    """
    logger.info("MCP Tool call: openehr_ehr_list")
    start_time = time.time()
    
    try:
        # Use the ad hoc query functionality to get all EHR IDs
        query = "SELECT e/ehr_id/value AS ehr_id FROM EHR e"
        query_result = await ehrbase_client.execute_adhoc_query(query)
        
        # Extract just the EHR IDs from the query result for a cleaner response
        ehr_ids = []
        if "rows" in query_result:
            for row in query_result["rows"]:
                if row and len(row) > 0:
                    ehr_ids.append(row[0])
        
        # Format the response
        result = {
            "ehr_ids": ehr_ids,
            "total": len(ehr_ids)
        }
        response = json.dumps(result, indent=2)
        
        elapsed = time.time() - start_time
        logger.info(f"Listed {len(ehr_ids)} EHRs in {elapsed:.2f}s")
        return response
    except Exception as e:
        elapsed = time.time() - start_time
        error_msg = f"Error listing EHRs: {str(e)}"
        logger.error(f"{error_msg} after {elapsed:.2f}s")
        return error_msg

@mcp.tool()
async def openehr_ehr_get_by_subject(subject_id: str, subject_namespace: str) -> str:
    """Get an EHR by subject ID and namespace.
    
    Retrieves an Electronic Health Record (EHR) from the EHRbase server using
    the subject's ID and namespace. This is useful for finding a patient's EHR
    when you have their identifier.
    
    Args:
        subject_id: The subject ID to search for
        subject_namespace: The subject namespace
        
    Returns:
        JSON string containing the EHR details
    """
    if not subject_id or not subject_namespace:
        return "Error: Both subject_id and subject_namespace are required"
        
    logger.info(f"MCP Tool call: openehr_ehr_get_by_subject for subject {subject_id} in namespace {subject_namespace}")
    start_time = time.time()
    
    try:
        # Get EHR by subject ID and namespace
        ehr = await ehrbase_client.get_ehr_by_subject_id(subject_id, subject_namespace)
        result = json.dumps(ehr, indent=2)
        
        elapsed = time.time() - start_time
        logger.info(f"Retrieved EHR for subject {subject_id} in {elapsed:.2f}s")
        return result
    except Exception as e:
        elapsed = time.time() - start_time
        error_msg = f"Error retrieving EHR by subject: {str(e)}"
        logger.error(f"{error_msg} after {elapsed:.2f}s")
        return error_msg

# COMPOSITION LIFECYCLE TOOLS
@mcp.tool()
async def openehr_composition_create(composition_data = None, ehr_id = None) -> str:
    """Create a new openEHR composition in the Electronic Health Record.
    
    Submits a new clinical data composition to the openEHR server, creating a persistent
    health record entry. The composition must conform to an existing openEHR template structure.
    The current implementation uses the flat JSON representation (application/openehr.wt.flat.schema+json)
    and the composition_data should include the template_id as part of its structure.
    
    Args:
        composition_data: The openEHR composition data as a JSON string
        ehr_id: Optional EHR ID to use (uses default if not provided)
        
    Returns:
        JSON string containing the creation response with the new composition's unique identifier
    """
    
    if not composition_data:
        return "Error: No composition data provided"
    
    # Use provided EHR ID or fall back to default
    target_ehr_id = ehr_id or DEFAULT_EHR_ID
        
    logger.info(f"MCP Tool call: openehr_composition_create for EHR {target_ehr_id}")
    start_time = time.time()
    
    try:
        # Handle composition_data as either string or dict
        if isinstance(composition_data, str):
            try:
                composition_json = json.loads(composition_data)
            except json.JSONDecodeError:
                return f"Error: composition_data must be a valid JSON string, received: {composition_data}"
        else:
            # If it's already a dict/object, use it directly
            composition_json = composition_data
        
        # Create the composition using the specified EHR ID
        result = await ehrbase_client.create_composition(target_ehr_id, composition_json)
        response = json.dumps(result, indent=2)
        
        elapsed = time.time() - start_time
        logger.info(f"Created composition in {elapsed:.2f}s")
        return response
    except Exception as e:
        elapsed = time.time() - start_time
        error_msg = f"Error creating composition: {str(e)}"
        logger.error(f"{error_msg} after {elapsed:.2f}s")
        return error_msg

@mcp.tool()
async def openehr_composition_get(composition_uid: str, ehr_id = None) -> str:
    """Retrieve an existing openEHR composition by its unique identifier.
    
    Fetches a previously created clinical data composition from the EHRbase server using
    its unique identifier. The composition is returned in flat JSON format, which maintains
    all the clinical data points in a structured format according to the openEHR standard.
    
    Args:
        composition_uid: The unique identifier of the openEHR composition (versioned object UID)
        ehr_id: Optional EHR ID to use (uses default if not provided)
        
    Returns:
        JSON string containing the complete openEHR composition in flat JSON format
    """
    
    if not composition_uid:
        return "Error: No composition UID provided"
    
    # Use provided EHR ID or fall back to default
    target_ehr_id = ehr_id or DEFAULT_EHR_ID
        
    logger.info(f"MCP Tool call: openehr_composition_get for composition {composition_uid} in EHR {target_ehr_id}")
    start_time = time.time()
    
    try:
        # Retrieve the composition using the specified EHR ID
        result = await ehrbase_client.get_composition(target_ehr_id, composition_uid)
        response = json.dumps(result, indent=2)
        
        elapsed = time.time() - start_time
        logger.info(f"Retrieved composition in {elapsed:.2f}s")
        return response
    except Exception as e:
        elapsed = time.time() - start_time
        error_msg = f"Error retrieving composition: {str(e)}"
        logger.error(f"{error_msg} after {elapsed:.2f}s")
        return error_msg

@mcp.tool()
async def openehr_composition_update(composition_uid: str, composition_data, ehr_id = None) -> str:
    """Update an existing openEHR composition in the Electronic Health Record.
    
    Modifies a previously created clinical data composition in the EHRbase server.
    This creates a new version of the composition while maintaining the version history.
    The updated composition must conform to the same openEHR template structure as the original.
    Updates are performed using flat JSON format, and the composition_uid is used to identify
    which composition to update.
    
    Args:
        composition_uid: The unique identifier of the openEHR composition to update (versioned object UID)
        composition_data: The updated openEHR composition data as a JSON string or object in flat JSON format
        ehr_id: Optional EHR ID to use (uses default if not provided)
        
    Returns:
        JSON string containing the update response with the composition's new version identifier
    """
    
    if not composition_uid:
        return "Error: No composition UID provided"
        
    if not composition_data:
        return "Error: No composition data provided"
    
    # Use provided EHR ID or fall back to default
    target_ehr_id = ehr_id or DEFAULT_EHR_ID
        
    logger.info(f"MCP Tool call: openehr_composition_update for composition {composition_uid} in EHR {target_ehr_id}")
    start_time = time.time()
    
    try:
        # Handle composition_data as either string or dict
        if isinstance(composition_data, str):
            try:
                composition_json = json.loads(composition_data)
            except json.JSONDecodeError:
                return f"Error: composition_data must be a valid JSON string, received: {composition_data}"
        else:
            # If it's already a dict/object, use it directly
            composition_json = composition_data
        
        # Update the composition using the specified EHR ID
        result = await ehrbase_client.update_composition(target_ehr_id, composition_uid, composition_json)
        response = json.dumps(result, indent=2)
        
        elapsed = time.time() - start_time
        logger.info(f"Updated composition in {elapsed:.2f}s")
        return response
    except Exception as e:
        elapsed = time.time() - start_time
        error_msg = f"Error updating composition: {str(e)}"
        logger.error(f"{error_msg} after {elapsed:.2f}s")
        return error_msg

@mcp.tool()
async def openehr_composition_delete(preceding_version_uid: str, ehr_id = None) -> str:
    """Delete an existing openEHR composition from the Electronic Health Record.
    
    Removes a clinical data composition from the EHRbase server. In openEHR systems,
    deletions are typically implemented as a new version that marks the composition as
    deleted rather than physically removing it, maintaining the audit trail of all changes.
    The deletion is performed using the composition's version UID to ensure the specific
    version is properly identified.
    
    Args:
        preceding_version_uid: The unique version identifier of the openEHR composition to delete
        ehr_id: Optional EHR ID to use (uses default if not provided)
        
    Returns:
        JSON string containing the deletion response status
    """
    
    if not preceding_version_uid:
        return "Error: No composition version UID provided"
    
    # Use provided EHR ID or fall back to default
    target_ehr_id = ehr_id or DEFAULT_EHR_ID
        
    logger.info(f"MCP Tool call: openehr_composition_delete for version {preceding_version_uid} in EHR {target_ehr_id}")
    start_time = time.time()
    
    try:
        # Delete the composition using the specified EHR ID
        result = await ehrbase_client.delete_composition(target_ehr_id, preceding_version_uid)
        response = json.dumps(result, indent=2)
        
        elapsed = time.time() - start_time
        logger.info(f"Deleted composition in {elapsed:.2f}s")
        return response
    except Exception as e:
        elapsed = time.time() - start_time
        error_msg = f"Error deleting composition: {str(e)}"
        logger.error(f"{error_msg} after {elapsed:.2f}s")
        return error_msg

@mcp.tool()
async def openehr_query_adhoc(query: str, query_parameters = None) -> str:
    """Execute an ad-hoc AQL query against the openEHR server.
    
    Executes an Archetype Query Language (AQL) query against the EHRbase server.
    AQL is a declarative query language similar to SQL but designed specifically for
    querying openEHR clinical data. This tool allows running arbitrary AQL queries
    to retrieve data from the clinical repository.
    
    Args:
        query: The AQL query string to execute
        query_parameters: Optional parameters for the query as a JSON string or object
        
    Returns:
        JSON string containing the query results
    """
    
    if not query:
        return "Error: No query provided"
    
    logger.info(f"MCP Tool call: openehr_query_adhoc")
    start_time = time.time()
    
    try:
        # Handle query_parameters as either string or dict
        params = None
        if query_parameters:
            if isinstance(query_parameters, str):
                try:
                    params = json.loads(query_parameters)
                except json.JSONDecodeError:
                    return f"Error: query_parameters must be a valid JSON string, received: {query_parameters}"
            else:
                # If it's already a dict/object, use it directly
                params = query_parameters
        
        # Execute the query
        result = await ehrbase_client.execute_adhoc_query(query, params)
        response = json.dumps(result, indent=2)
        
        elapsed = time.time() - start_time
        logger.info(f"Executed ad-hoc query in {elapsed:.2f}s")
        return response
    except Exception as e:
        elapsed = time.time() - start_time
        error_msg = f"Error executing query: {str(e)}"
        logger.error(f"{error_msg} after {elapsed:.2f}s")
        return error_msg

@mcp.tool()
async def openehr_compositions_list(template_id: str) -> str:
    """List all compositions for a specific openEHR template.
    
    Retrieves all compositions that were created using the specified template from the EHRbase server.
    This provides a way to find all clinical data entries that conform to a particular structure.
    The results include the EHR ID and the full composition data for each matching composition.
    
    Args:
        template_id: The unique identifier of the openEHR template to filter compositions by
        
    Returns:
        JSON string containing the list of compositions that use the specified template
    """
    logger.info(f"MCP Tool call: openehr_compositions_list for template {template_id}")
    start_time = time.time()
    
    try:
        # Prepare the AQL query to find all compositions for the template
        query = "SELECT e/ehr_id/value AS ehr_id, c AS composition FROM EHR e CONTAINS COMPOSITION c WHERE c/archetype_details/template_id/value = $template_id"
        query_parameters = {"template_id": template_id}
        
        # Execute the query using the query client
        result = await ehrbase_client.execute_adhoc_query(query, query_parameters)
        response = json.dumps(result, indent=2)
        
        # Get the count of compositions found
        composition_count = len(result.get("rows", [])) if isinstance(result, dict) and "rows" in result else 0
        
        elapsed = time.time() - start_time
        logger.info(f"Listed {composition_count} compositions for template {template_id} in {elapsed:.2f}s")
        return response
    except Exception as e:
        elapsed = time.time() - start_time
        error_msg = f"Error listing compositions for template {template_id}: {str(e)}"
        logger.error(f"{error_msg} after {elapsed:.2f}s")
        return error_msg



# Run the server
if __name__ == "__main__":
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='openEHR MCP Server')
    parser.add_argument('--transport', type=str, default='stdio',
                        help=f'Transport type (available: {", ".join(list_transport_plugins())})')
    parser.add_argument('--list-transports', action='store_true',
                        help='List available transport plugins')
    
    args, unknown = parser.parse_known_args()
    
    # List available transports if requested
    if args.list_transports:
        print("Available transport plugins:")
        for transport_name in list_transport_plugins():
            print(f"  - {transport_name}")
        sys.exit(0)
    
    # Log the server configuration
    logger.info(f"Starting openEHR MCP Server with {args.transport} transport")
    
    # Get the transport plugin
    transport_plugin = get_transport_plugin(args.transport)
    if not transport_plugin:
        logger.error(f"Unknown transport: {args.transport}")
        logger.info(f"Available transports: {', '.join(list_transport_plugins())}")
        sys.exit(1)
    
    # Run with the selected transport
    try:
        transport_plugin.run(mcp, **vars(args))
    except Exception as e:
        logger.error(f"Error running transport {args.transport}: {e}")
        sys.exit(1)