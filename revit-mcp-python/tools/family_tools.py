# -*- coding: utf-8 -*-
"""Family and placement tools"""

from fastmcp import Context
from typing import Dict, Any, List, Optional
from .utils import format_response


def register_family_tools(mcp, revit_get, revit_post):
    """Register family-related tools"""

    @mcp.tool()
    async def place_family(
        family_name: str,
        type_name: str = None,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        rotation: float = 0.0,
        level_name: str = None,
        properties: Dict[str, Any] = None,
        ctx: Context = None,
    ) -> str:
        """Place a family instance at a specified location in the Revit model"""
        data = {
            "family_name": family_name,
            "type_name": type_name,
            "location": {"x": x, "y": y, "z": z},
            "rotation": rotation,
            "level_name": level_name,
            "properties": properties or {},
        }
        response = await revit_post("/place_family/", data, ctx)
        return format_response(response)

    @mcp.tool()
    async def place_workplane_families(
        symbol_id: int,
        placements: List[Dict[str, Any]],
        ctx: Context = None,
    ) -> str:
        """
        Place WorkPlaneBased families on vertical planes (for windows, doors, etc).
        
        This is the core tool for batch placement of wall-hosted families like windows
        and doors. Uses symbol_id directly for efficiency.

        Args:
            symbol_id: FamilySymbol ElementId (get from list_families)
            placements: List of placement dictionaries, each containing:
                - x_mm: X coordinate in millimeters
                - y_mm: Y coordinate in millimeters  
                - z_mm: Z coordinate in millimeters
                - normal_x: X component of wall normal vector
                - normal_y: Y component of wall normal vector
                - normal_z: Z component of wall normal vector (usually 0)
                - rotate_180: Optional, 1 to rotate 180 degrees (default: 0)
                - mark: Optional, Mark parameter value

        Returns:
            JSON with placed element IDs and any failures

        Example:
            place_workplane_families(
                symbol_id=1281171,
                placements=[
                    {
                        "x_mm": 4335.8,
                        "y_mm": 43672.5,
                        "z_mm": 900.0,
                        "normal_x": -0.906,
                        "normal_y": -0.422,
                        "normal_z": 0.0,
                        "mark": "W-101"
                    }
                ]
            )
        """
        if ctx:
            ctx.info("Placing {} WorkPlaneBased families with symbol {}".format(
                len(placements), symbol_id))

        data = {
            "symbol_id": symbol_id,
            "placements": placements
        }
        response = await revit_post("/place_workplane_families/", data, ctx, timeout=120.0)
        return format_response(response)

    @mcp.tool()
    async def list_families(
        contains: str = None, limit: int = 50, ctx: Context = None
    ) -> str:
        """Get a flat list of available family types in the current Revit model"""
        params = {}
        if contains:
            params["contains"] = contains
        if limit != 50:
            params["limit"] = str(limit)

        result = await revit_get("/list_families/", ctx, params=params)
        return format_response(result)

    @mcp.tool()
    async def list_family_categories(ctx: Context = None) -> str:
        """Get a list of all family categories in the current Revit model"""
        response = await revit_get("/list_family_categories/", ctx)
        return format_response(response)
