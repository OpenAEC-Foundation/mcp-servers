# -*- coding: utf-8 -*-
"""Modification tools for Revit MCP - batch updates, sheets, walls, family placement"""

from fastmcp import Context
from typing import Optional, List, Dict, Any
from .utils import format_response


def register_modification_tools(mcp, revit_get, revit_post):
    """Register modification tools"""

    @mcp.tool()
    async def batch_update(
        updates: List[Dict[str, Any]],
        ctx: Context = None
    ) -> str:
        """
        Batch update parameters on multiple elements in a single transaction.

        Efficient way to update many parameters across multiple elements at once.

        Args:
            updates: List of update objects, each containing:
                - element_id: The element ID to update
                - parameters: Dict of parameter_name -> new_value pairs

        Returns:
            JSON with success/failure counts and detailed results

        Example:
            batch_update([
                {"element_id": 12345, "parameters": {"Mark": "A-101", "Comments": "Updated"}},
                {"element_id": 12346, "parameters": {"Mark": "A-102"}},
                {"element_id": 12347, "parameters": {"Mark": "A-103", "Level": "Ground Floor"}}
            ])
        """
        if ctx:
            ctx.info("Batch updating {} elements".format(len(updates)))

        data = {"updates": updates}
        response = await revit_post("/batch_update/", data, ctx)
        return format_response(response)

    @mcp.tool()
    async def create_sheet(
        sheet_number: str,
        sheet_name: str = "New Sheet",
        title_block_name: str = "",
        ctx: Context = None
    ) -> str:
        """
        Create a new sheet in the Revit document.

        Args:
            sheet_number: The sheet number (e.g., "A-101", "S-001")
            sheet_name: The sheet name/title (default: "New Sheet")
            title_block_name: Name of title block family to use (partial match).
                            If empty, uses the first available title block.

        Returns:
            JSON with new sheet ID and details

        Example:
            create_sheet("A-101", "Floor Plan - Level 1", "A1 metric")
        """
        if ctx:
            ctx.info("Creating sheet {} - {}".format(sheet_number, sheet_name))

        data = {
            "sheet_number": sheet_number,
            "sheet_name": sheet_name
        }
        if title_block_name:
            data["title_block_name"] = title_block_name

        response = await revit_post("/create_sheet/", data, ctx)
        return format_response(response)

    @mcp.tool()
    async def place_view_on_sheet(
        sheet_id: int = 0,
        view_id: int = 0,
        sheet_number: str = "",
        view_name: str = "",
        x: float = 1.0,
        y: float = 0.75,
        ctx: Context = None
    ) -> str:
        """
        Place a view on a sheet.

        Can specify sheet/view by ID or by name.

        Args:
            sheet_id: ID of the sheet (use this OR sheet_number)
            view_id: ID of the view to place (use this OR view_name)
            sheet_number: Sheet number like "A-101" (use this OR sheet_id)
            view_name: Name of the view to place (use this OR view_id)
            x: X position on sheet in feet (default: 1.0)
            y: Y position on sheet in feet (default: 0.75)

        Returns:
            JSON with viewport details

        Examples:
            # By IDs
            place_view_on_sheet(sheet_id=12345, view_id=67890)

            # By names
            place_view_on_sheet(sheet_number="A-101", view_name="Level 1")
        """
        if ctx:
            identifier = sheet_number or str(sheet_id)
            ctx.info("Placing view on sheet {}".format(identifier))

        data = {"x": x, "y": y}
        if sheet_id:
            data["sheet_id"] = sheet_id
        if view_id:
            data["view_id"] = view_id
        if sheet_number:
            data["sheet_number"] = sheet_number
        if view_name:
            data["view_name"] = view_name

        response = await revit_post("/place_view_on_sheet/", data, ctx)
        return format_response(response)

    @mcp.tool()
    async def create_walls_at_lines(
        line_ids: List[int] = None,
        lines: List[Dict[str, Dict[str, float]]] = None,
        wall_type_name: str = "",
        level_name: str = "",
        height: float = 3000,
        structural: bool = False,
        ctx: Context = None
    ) -> str:
        """
        Create walls from model lines or coordinate pairs.

        Can create walls either from existing model/detail lines in Revit,
        or from coordinate data provided directly.

        Args:
            line_ids: List of element IDs of existing lines to convert to walls
            lines: List of line definitions with start/end coordinates in mm:
                   [{"start": {"x": 0, "y": 0}, "end": {"x": 5000, "y": 0}}]
            wall_type_name: Wall type to use (partial match). Uses first basic wall if empty.
            level_name: Level name (partial match). Uses lowest level if empty.
            height: Wall height in millimeters (default: 3000)
            structural: Whether walls are structural (default: False)

        Returns:
            JSON with created wall IDs and any failures

        Examples:
            # From existing lines
            create_walls_at_lines(line_ids=[12345, 12346], height=2800)

            # From coordinates (creates a rectangle)
            create_walls_at_lines(
                lines=[
                    {"start": {"x": 0, "y": 0}, "end": {"x": 5000, "y": 0}},
                    {"start": {"x": 5000, "y": 0}, "end": {"x": 5000, "y": 4000}},
                    {"start": {"x": 5000, "y": 4000}, "end": {"x": 0, "y": 4000}},
                    {"start": {"x": 0, "y": 4000}, "end": {"x": 0, "y": 0}}
                ],
                wall_type_name="Generic - 200mm",
                level_name="Level 1",
                height=3000
            )
        """
        if ctx:
            count = len(line_ids or []) + len(lines or [])
            ctx.info("Creating walls from {} lines".format(count))

        data = {
            "line_ids": line_ids or [],
            "lines": lines or [],
            "height": height,
            "structural": structural
        }
        if wall_type_name:
            data["wall_type_name"] = wall_type_name
        if level_name:
            data["level_name"] = level_name

        response = await revit_post("/create_walls_at_lines/", data, ctx)
        return format_response(response)

    @mcp.tool()
    async def batch_family_placement(
        family_name: str,
        placements: List[Dict[str, float]],
        type_name: str = "",
        level_name: str = "",
        ctx: Context = None
    ) -> str:
        """
        Place multiple instances of a family at specified locations.

        Efficient batch placement of furniture, equipment, or other families.

        Args:
            family_name: Name of the family to place (partial match)
            placements: List of placement locations with coordinates in mm:
                       [{"x": 1000, "y": 2000, "z": 0, "rotation": 90}]
                       - x, y, z: coordinates in millimeters
                       - rotation: optional rotation in degrees (default: 0)
            type_name: Specific family type to use (partial match, optional)
            level_name: Level to place on (partial match, optional)

        Returns:
            JSON with placed instance IDs and any failures

        Example:
            # Place 3 chairs in a row
            batch_family_placement(
                family_name="Chair",
                type_name="Office",
                placements=[
                    {"x": 1000, "y": 2000, "rotation": 0},
                    {"x": 2000, "y": 2000, "rotation": 0},
                    {"x": 3000, "y": 2000, "rotation": 0}
                ],
                level_name="Level 1"
            )
        """
        if ctx:
            ctx.info("Placing {} instances of family '{}'".format(len(placements), family_name))

        data = {
            "family_name": family_name,
            "placements": placements
        }
        if type_name:
            data["type_name"] = type_name
        if level_name:
            data["level_name"] = level_name

        response = await revit_post("/batch_family_placement/", data, ctx)
        return format_response(response)

    @mcp.tool()
    async def place_workplane_windows(
        symbol_id: int,
        placements: List[Dict[str, Any]],
        ctx: Context = None
    ) -> str:
        """
        Place WorkPlaneBased window families with correct vertical orientation.
        Specifically designed for WorkPlaneBased window placement workflow.

        This is a specialized tool for placing windows from IFC data where the
        normal vectors define wall orientation. Handles the complex coordinate
        transformation and rotation logic automatically.

        Args:
            symbol_id: FamilySymbol ElementId (Revit element ID of the window type)
            placements: List of placement dictionaries, each containing:
                - x_mm: X coordinate in millimeters
                - y_mm: Y coordinate in millimeters
                - z_mm: Z coordinate in millimeters (sill height)
                - normal_x: X component of wall normal vector
                - normal_y: Y component of wall normal vector
                - mark: Optional Mark parameter value

        Returns:
            JSON with placed element IDs, marks, and any failures

        Example:
            place_workplane_windows(
                symbol_id=6285049,
                placements=[
                    {
                        "x_mm": 4335.8,
                        "y_mm": 43672.5,
                        "z_mm": 900.0,
                        "normal_x": -0.906,
                        "normal_y": -0.422,
                        "mark": "W-108"
                    },
                    {
                        "x_mm": 8500.0,
                        "y_mm": 43672.5,
                        "z_mm": 900.0,
                        "normal_x": -0.906,
                        "normal_y": -0.422,
                        "mark": "W-109"
                    }
                ]
            )
        
        Notes:
            - Coordinates are the CENTER of the window (not corner)
            - Normal vector should point outward from the wall face
            - Windows with positive normal_y are automatically rotated 180°
        """
        if ctx:
            ctx.info("Placing {} windows with symbol {}".format(
                len(placements), symbol_id))

        data = {
            "symbol_id": symbol_id,
            "placements": placements
        }
        response = await revit_post("/place_workplane_windows/", data, ctx, timeout=120.0)
        return format_response(response)

    @mcp.tool()
    async def coordinate_converter(
        x: float,
        y: float,
        z: float = 0,
        from_unit: str = "mm",
        to_unit: str = "mm",
        from_system: str = "internal",
        to_system: str = "internal",
        ctx: Context = None
    ) -> str:
        """
        Convert coordinates between different units and coordinate systems.

        Useful for converting between metric/imperial units or between
        Revit's internal, project, shared, and survey coordinate systems.

        Args:
            x: X coordinate
            y: Y coordinate
            z: Z coordinate (default: 0)
            from_unit: Input unit - "mm", "m", "ft", or "in" (default: "mm")
            to_unit: Output unit - "mm", "m", "ft", or "in" (default: "mm")
            from_system: Input coordinate system (default: "internal"):
                        - "internal": Revit's internal coordinates
                        - "project": Project Base Point coordinates
                        - "shared": Shared coordinates
            to_system: Output coordinate system (default: "internal")

        Returns:
            JSON with converted coordinates

        Examples:
            # Convert mm to feet
            coordinate_converter(1000, 2000, from_unit="mm", to_unit="ft")

            # Convert from internal to shared coordinates
            coordinate_converter(100, 200, from_system="internal", to_system="shared")
        """
        if ctx:
            ctx.info("Converting coordinates from {} {} to {} {}".format(
                from_unit, from_system, to_unit, to_system))

        data = {
            "coordinates": {"x": x, "y": y, "z": z},
            "from_unit": from_unit,
            "to_unit": to_unit,
            "from_system": from_system,
            "to_system": to_system
        }

        response = await revit_post("/coordinate_converter/", data, ctx)
        return format_response(response)
