# Revit MCP Server - Skill Definition

## Overview

This skill enables Claude to interact with Autodesk Revit through the Model Context Protocol (MCP). It provides 34 tools for querying, modifying, and automating Revit models.

## When to Use This Skill

Use when the user needs to:
- Query Revit model information (elements, parameters, views)
- Place or modify elements in Revit
- Automate repetitive BIM tasks
- Inspect or analyze model content
- Work with linked IFC models
- Execute custom Revit API code

## Prerequisites

- Revit must be running with pyRevit installed
- pyRevit Routes must be enabled (Settings → Routes → Enable)
- MCP server must be configured in Claude Desktop

## Quick Start

### Check Connection
```
Use get_revit_status to verify Revit is connected.
```

### Get Model Overview
```
Use get_revit_model_info to see document title and element counts.
Use list_levels to see available levels.
Use list_families to find available family types.
```

### Inspect Elements
```
Use quick_count to count elements by category.
Use inspect_element with an element ID for detailed information.
Use get_all_parameters to see all parameters on an element.
```

### Modify Elements
```
Use set_element_parameter to change a single parameter.
Use batch_update for multiple elements/parameters at once.
Use execute_revit_code for custom operations.
```

## Tool Categories

### Read Operations (No Transaction Needed)
- `get_revit_status` - API health check
- `get_revit_model_info` - Model overview
- `list_levels`, `list_families`, `list_family_categories`
- `list_revit_views`, `get_current_view_info`, `get_current_view_elements`
- `get_active_selection`, `inspect_element`, `inspect_selected_element`
- `get_link_status`, `quick_count`
- `get_element_parameter`, `get_all_parameters`
- `query_ifc_elements`, `get_ifc_element_properties`

### Write Operations (Transaction Required)
- `place_family`, `place_workplane_families`, `place_workplane_windows`
- `batch_family_placement`, `create_walls_at_lines`
- `set_element_parameter`, `set_parameters_bulk`, `set_parameters_multi_elements`
- `batch_update`
- `create_sheet`, `place_view_on_sheet`
- `color_splash`, `clear_colors`
- `execute_revit_code` (with `use_transaction=True`)

## Important Patterns

### Unit Conversion
Revit uses **feet** internally. User-facing values are typically in **millimeters**.
```
feet = mm / 304.8
mm = feet * 304.8
```

### Element IDs
All element operations use Revit ElementIds (integers). Get IDs from:
- `quick_count` results
- `get_active_selection` results
- `inspect_element` output
- `query_ifc_elements` results

### Family Placement
For standard families:
```
place_family(family_name="Chair", type_name="Office", x=1000, y=2000, z=0)
```

For wall-hosted families (windows/doors):
```
place_workplane_families(
    symbol_id=6714302,  # Get from list_families
    placements=[{
        "x_mm": 5000, "y_mm": 3000, "z_mm": 900,
        "normal_x": 0, "normal_y": -1, "normal_z": 0,
        "mark": "W-101"
    }]
)
```

### Custom Code Execution
For operations not covered by existing tools:
```python
execute_revit_code(
    code='''
        # Your IronPython 2.7 code here
        print("Document:", doc.Title)
    ''',
    description="What this code does",
    use_transaction=False  # True for modifications
)
```

## Error Handling

### "Route does not exist"
Revit may need restart, or URL prefix `/revit_mcp/` is missing.

### Empty responses from write operations
The server route may not be using the `doc` parameter pattern for thread-safe execution.

### Transaction failures
Use `execute_revit_code` with `use_transaction=True` as fallback.

## Workflow Examples

### Window Placement Workflow
1. `list_families(contains="Window")` - Find window types
2. `query_ifc_elements(category="Windows")` - Get IFC window positions
3. `place_workplane_windows(symbol_id=..., placements=[...])` - Place windows
4. `quick_count(category="Windows")` - Verify placement

### Parameter Update Workflow
1. `quick_count(category="Doors", type_contains="Interior")` - Find elements
2. `get_all_parameters(element_id=...)` - Discover parameters
3. `batch_update(updates=[...])` - Update multiple elements

### Model Analysis Workflow
1. `get_revit_model_info()` - Overview
2. `list_levels()` - Structure
3. `quick_count(category="Walls", level="Level 1")` - Counts per level
4. `color_splash(category_name="Walls", parameter_name="Type Name")` - Visualize

## Limitations

- No direct file operations (open/save/export)
- No UI automation (dialogs, selections)
- Single Revit instance at a time
- Network-local only (localhost)
- IronPython 2.7 syntax in execute_code

## Related Documentation

- `README.md` - Installation and overview
- `LLM.txt` - Development guide
- `LESSONS_LEARNED.md` - Technical patterns
- `CHANGELOG.md` - Version history
