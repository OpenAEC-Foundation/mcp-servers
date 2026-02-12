# -*- coding: utf-8 -*-
"""IFC query tools for Revit MCP - search elements in linked IFC models"""

from fastmcp import Context
from typing import Optional, List
from .utils import format_response


def register_ifc_tools(mcp, revit_get, revit_post):
    """Register IFC query tools"""

    @mcp.tool()
    async def query_ifc_elements(
        link_name: str = "",
        category: str = "",
        ifc_class: str = "",
        parameter_name: str = "",
        parameter_value: str = "",
        max_results: int = 100,
        ctx: Context = None
    ) -> str:
        """
        Search for elements in linked IFC models with flexible filtering.

        Use this tool to find elements in linked IFC/Revit models based on
        various criteria. All filters are optional and combined with AND logic.

        Args:
            link_name: Filter by linked model name (partial match, case-insensitive)
                       Example: "Architecture" to find links containing that word
            category: Revit category name to filter on
                      Examples: "Windows", "Doors", "Walls", "Floors"
            ifc_class: IFC class/type to filter on
                       Examples: "IfcWall", "IfcDoor", "IfcWindow", "IfcSlab"
            parameter_name: Parameter name to search for
                           Examples: "Mark", "IfcName", "Type Name"
            parameter_value: Value to match (partial match for strings)
                            Examples: "A-101", "External", "Concrete"
            max_results: Maximum number of elements to return (default: 100)

        Returns:
            JSON with matching elements including:
            - link_name: Name of the linked model
            - element_id: ID within the linked model
            - name, category, type_name
            - ifc_properties: Common IFC parameters
            - matched_parameter: The parameter that matched (if filtering)

        Examples:
            # Find all doors in any linked model
            query_ifc_elements(category="Doors")

            # Find walls in a specific linked model
            query_ifc_elements(link_name="Architecture", category="Walls")

            # Find elements with specific Mark value
            query_ifc_elements(parameter_name="Mark", parameter_value="W-101")

            # Find IfcWindow elements
            query_ifc_elements(ifc_class="IfcWindow")
        """
        if ctx:
            filters = []
            if link_name:
                filters.append("link={}".format(link_name))
            if category:
                filters.append("category={}".format(category))
            if ifc_class:
                filters.append("ifc_class={}".format(ifc_class))
            if parameter_name:
                filters.append("{}={}".format(parameter_name, parameter_value or "*"))
            ctx.info("Querying IFC elements: {}".format(", ".join(filters) if filters else "all"))

        data = {
            "link_name": link_name,
            "category": category,
            "ifc_class": ifc_class,
            "parameter_name": parameter_name,
            "parameter_value": parameter_value,
            "max_results": max_results
        }
        response = await revit_post("/query_ifc_elements/", data, ctx)
        return format_response(response)

    @mcp.tool()
    async def get_ifc_element_properties(
        link_instance_id: int,
        element_id: int,
        ctx: Context = None
    ) -> str:
        """
        Get all properties from an element in a linked IFC model.

        Use this after query_ifc_elements to get full details about a specific
        element. Retrieves both instance and type parameters.

        Args:
            link_instance_id: ID of the RevitLinkInstance (from query results)
            element_id: ID of the element within the linked model

        Returns:
            JSON with complete element information:
            - Basic info (name, category)
            - All instance parameters with values
            - All type parameters with values

        Example:
            # First find elements
            results = query_ifc_elements(category="Doors", max_results=5)
            # Then get full details for one
            get_ifc_element_properties(link_instance_id=12345, element_id=67890)
        """
        if ctx:
            ctx.info("Getting properties for element {} in link {}".format(element_id, link_instance_id))

        data = {
            "link_instance_id": link_instance_id,
            "element_id": element_id
        }
        response = await revit_post("/get_ifc_element_properties/", data, ctx)
        return format_response(response)

    # NOTE: get_link_status is registered in selection_tools.py
    # Removed duplicate registration to avoid MCP tool conflicts
