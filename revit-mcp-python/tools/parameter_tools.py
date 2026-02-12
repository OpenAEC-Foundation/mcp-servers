# -*- coding: utf-8 -*-
"""Parameter tools for reading and writing Revit element parameters"""

from fastmcp import Context
from typing import Dict, Any, List, Optional
from .utils import format_response


def register_parameter_tools(mcp, revit_get, revit_post):
    """Register parameter-related tools"""

    @mcp.tool()
    async def get_element_parameter(
        element_id: int,
        parameter_name: str,
        ctx: Context = None
    ) -> str:
        """
        Get a single parameter value from a Revit element.

        This is the most efficient way to read a specific parameter.
        Searches both instance and type parameters.

        Args:
            element_id: The Revit element ID
            parameter_name: Name of the parameter (case-insensitive)

        Returns:
            JSON with parameter value, display value, and metadata

        Examples:
            get_element_parameter(12345, "Mark")
            get_element_parameter(12345, "Height")
            get_element_parameter(12345, "Comments")
        """
        if ctx:
            ctx.info(f"Getting parameter '{parameter_name}' from element {element_id}")

        data = {
            "element_id": element_id,
            "parameter_name": parameter_name
        }
        response = await revit_post("/get_parameter/", data, ctx)
        return format_response(response)

    @mcp.tool()
    async def set_element_parameter(
        element_id: int,
        parameter_name: str,
        value: Any,
        ctx: Context = None
    ) -> str:
        """
        Set a parameter value on a Revit element.

        Automatically handles type conversion:
        - Strings: Set directly
        - Numbers: Converted to appropriate type (int/double)
        - Yes/No: Accepts true/false, yes/no, 1/0
        - Units: For dimensions, use display units (e.g., "2400" for mm)

        Args:
            element_id: The Revit element ID
            parameter_name: Name of the parameter (case-insensitive)
            value: New value for the parameter

        Returns:
            JSON with old value, new value, and success status

        Examples:
            set_element_parameter(12345, "Mark", "A-101")
            set_element_parameter(12345, "Comments", "Updated via MCP")
            set_element_parameter(12345, "Height", 2400)
        """
        if ctx:
            ctx.info(f"Setting parameter '{parameter_name}' = '{value}' on element {element_id}")

        data = {
            "element_id": element_id,
            "parameter_name": parameter_name,
            "value": value
        }
        response = await revit_post("/set_parameter/", data, ctx)
        return format_response(response)

    @mcp.tool()
    async def get_all_parameters(
        element_id: int,
        include_empty: bool = False,
        include_readonly: bool = True,
        ctx: Context = None
    ) -> str:
        """
        Get ALL parameters from a Revit element (instance + type).

        Returns a complete list of all parameters with their values,
        grouped by instance and type parameters.

        Args:
            element_id: The Revit element ID
            include_empty: Include parameters with no value (default: False)
            include_readonly: Include read-only parameters (default: True)

        Returns:
            JSON with instance_parameters and type_parameters lists

        Use this to discover what parameters an element has,
        then use get_element_parameter for specific values.
        """
        if ctx:
            ctx.info(f"Getting all parameters from element {element_id}")

        data = {
            "element_id": element_id,
            "include_empty": include_empty,
            "include_readonly": include_readonly
        }
        response = await revit_post("/get_all_parameters/", data, ctx)
        return format_response(response)

    @mcp.tool()
    async def set_parameters_bulk(
        element_id: int,
        parameters: Dict[str, Any],
        ctx: Context = None
    ) -> str:
        """
        Set multiple parameters on a single element in one transaction.

        More efficient than calling set_element_parameter multiple times
        because it uses a single Revit transaction.

        Args:
            element_id: The Revit element ID
            parameters: Dictionary of parameter_name: value pairs

        Returns:
            JSON with success/failed lists and summary

        Example:
            set_parameters_bulk(12345, {
                "Mark": "A-101",
                "Comments": "Updated via MCP",
                "Phase Created": "New Construction"
            })
        """
        if ctx:
            ctx.info(f"Setting {len(parameters)} parameters on element {element_id}")

        data = {
            "element_id": element_id,
            "parameters": parameters
        }
        response = await revit_post("/set_parameters_bulk/", data, ctx)
        return format_response(response)

    @mcp.tool()
    async def set_parameters_multi_elements(
        element_ids: List[int],
        parameters: Dict[str, Any],
        ctx: Context = None
    ) -> str:
        """
        Set the same parameter(s) on multiple elements in one transaction.

        Very efficient for bulk updates like:
        - Setting Mark on all windows in a view
        - Adding Comments to selected elements
        - Updating custom parameters across many elements

        Args:
            element_ids: List of Revit element IDs
            parameters: Dictionary of parameter_name: value pairs

        Returns:
            JSON with per-element results and summary

        Example:
            set_parameters_multi_elements(
                [12345, 12346, 12347],
                {"Mark": "BATCH-001", "Comments": "Updated in batch"}
            )
        """
        if ctx:
            ctx.info(f"Setting parameters on {len(element_ids)} elements")

        data = {
            "element_ids": element_ids,
            "parameters": parameters
        }
        response = await revit_post("/set_parameters_multi/", data, ctx)
        return format_response(response)
