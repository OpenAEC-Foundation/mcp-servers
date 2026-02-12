# -*- coding: utf-8 -*-
"""Selection and inspection tools for Revit MCP"""

from fastmcp import Context
from typing import Optional, List
from .utils import format_response


def register_selection_tools(mcp, revit_get, revit_post):
    """Register selection and inspection tools"""

    @mcp.tool()
    async def get_active_selection(ctx: Context = None) -> str:
        """
        Get details about currently selected elements in Revit.

        Returns information about the active selection including:
        - Total count of selected elements
        - Elements grouped by category
        - List of all element IDs
        - Detailed info about the first selected element

        Returns:
            JSON with selection details or message if nothing is selected
        """
        if ctx:
            ctx.info("Getting active selection info...")
        response = await revit_get("/active_selection/", ctx)
        return format_response(response)

    @mcp.tool()
    async def inspect_selected_element(index: int = 0, ctx: Context = None) -> str:
        """
        Get detailed information about a specific selected element by index.
        
        Args:
            index: 0-based index into the selection set (default: 0 = first element)

        Returns:
            JSON with detailed element information including all parameters
        """
        if ctx:
            ctx.info("Inspecting selected element at index {}...".format(index))
        response = await revit_get("/inspect_selected/{}".format(index), ctx)
        return format_response(response)

    @mcp.tool()
    async def inspect_element(element_id: int, ctx: Context = None) -> str:
        """
        Get comprehensive information about ANY element by its ID.
        
        This is the "what am I looking at" tool - use it to get complete details
        about any element, including:
        - Basic info (ID, name, category, type)
        - Location (point or curve) with coordinates in feet and mm
        - Bounding box with dimensions
        - Level information
        - Host element (for windows, doors, etc.)
        - All parameters with values
        - Geometry summary
        
        Args:
            element_id: The Revit element ID to inspect

        Returns:
            JSON with comprehensive element information
        """
        if ctx:
            ctx.info("Inspecting element ID {}...".format(element_id))
        response = await revit_get("/inspect_element/{}".format(element_id), ctx)
        return format_response(response)

    @mcp.tool()
    async def get_link_status(ctx: Context = None) -> str:
        """
        Get comprehensive information about all linked models in the project.
        
        Returns for each link:
        - Instance ID and load status
        - Pinned status
        - Transform information (origin, is_identity)
        - Document path
        - Element counts per category
        - Total element count
        
        Useful for understanding IFC links and their coordinate systems.

        Returns:
            JSON with all linked model information
        """
        if ctx:
            ctx.info("Getting link status...")
        response = await revit_get("/link_status/", ctx)
        return format_response(response)

    @mcp.tool()
    async def quick_count(
        category: str,
        type_contains: Optional[str] = None,
        type_excludes: Optional[List[str]] = None,
        level: Optional[str] = None,
        in_view: bool = False,
        ctx: Context = None
    ) -> str:
        """
        Fast element count with filters.
        
        Get a quick count of elements matching specific criteria.
        Much faster than getting full element details.
        
        Args:
            category: Category name to count (e.g., "Windows", "Walls", "Doors")
            type_contains: Only count elements whose type name contains this string
            type_excludes: Exclude elements whose type name contains any of these strings
            level: Only count elements on this level
            in_view: If True, only count elements visible in the current view

        Returns:
            JSON with count, filters applied, and first 100 element IDs
        
        Examples:
            - quick_count("Windows") -> all windows
            - quick_count("Windows", type_contains="31_K") -> kunststof windows
            - quick_count("Windows", type_contains="31_K", type_excludes=["SK", "H"]) -> kunststof without SK/H
            - quick_count("Walls", level="00_begane grond") -> walls on ground floor
        """
        if ctx:
            ctx.info("Quick count for category: {}".format(category))
        
        data = {
            "category": category,
            "in_view": in_view
        }
        
        if type_contains:
            data["type_contains"] = type_contains
        if type_excludes:
            data["type_excludes"] = type_excludes
        if level:
            data["level"] = level
        
        response = await revit_post("/quick_count/", data, ctx)
        return format_response(response)
