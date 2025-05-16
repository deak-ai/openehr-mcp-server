"""
Prompts for the openEHR MCP Server.

This module defines reusable prompts that help LLMs interact with the openEHR MCP server effectively.
"""
from mcp.server.fastmcp.prompts import base

def register_prompts(mcp):
    """
    Register all prompts with the MCP server.
    
    Args:
        mcp: The MCP server instance
    """

    
    @mcp.prompt()
    def vital_sign_capture(ehr_id: str) -> str:
        """
        Create a new composition for the given EHR using the latest template
        """
        return f"""You are a healthcare professional capturing vital signs for a patient represented by EHR ID {ehr_id}.

        Please proceed as follows:

        1: Using the openehr_template_list tool chose the latest one that has vital signs in the name (abort if you don't find a vital sign one)
        2: If there are multiple, ask the user to choose one
        3: Obtain an example composition for that template id using the openehr_template_example_composition tool
        4. Analyze that example composition about which clinical data will be needed and prompt the user
        5. Once you have all the necessary data (you might have to ask a couple of times), use the openehr_compositionc_create tool to create this in the EHR with ID {ehr_id}

   """


    
    return mcp
