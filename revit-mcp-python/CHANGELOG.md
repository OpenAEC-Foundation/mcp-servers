# Changelog

All notable changes to this project are documented in this file.

## [2.1.0] - 2026-01-27

### Added
- **`place_workplane_families`** tool in `family_tools.py` - Batch placement of WorkPlaneBased families (windows, doors) with full coordinate and normal vector support
- **`place_workplane_windows`** tool in `modification_tools.py` - Specialized window placement workflow with automatic 180° rotation handling
- **`use_transaction`** parameter to `execute_revit_code` tool - Allows explicit control over transaction wrapping (default: True)
- Extended timeout (120s) for batch placement operations
- This `CHANGELOG.md` file
- `LESSONS_LEARNED.md` - Documentation of threading patterns and IronPython compatibility
- `SKILL.md` - Claude skill definition for automated project assistance

### Changed
- Updated all tool docstrings with comprehensive examples
- Improved error messages with more context

### Fixed
- Removed duplicate `get_link_status` registration from `ifc_tools.py` (now only in `selection_tools.py`)

### Documentation
- Complete rewrite of `README.md` with full tool inventory (34 tools)
- Updated `LLM.txt` with threading patterns and all current routes

---

## [2.0.0] - 2026-01-26

### Added - Threading Safety Overhaul
All server routes updated to use pyRevit's IExternalEventHandler mechanism for thread-safe Revit API access.

#### Route Modules Fixed
- `placement.py` - 5 routes with `doc` parameter
- `code_execution.py` - 1 route with `doc` parameter  
- `colors.py` - 3 routes with `doc` parameter
- `views.py` - 4 routes with `doc`/`uidoc` parameters
- `modification.py` - 7 routes with `doc` parameter
- `parameters.py` - 6 routes with `doc` parameter
- `ifc_query.py` - 2 routes with `doc` parameter
- `selection.py` - 5 routes (read-only, kept `revit.doc` pattern)
- `model_info.py` - 1 route (read-only)
- `status.py` - 1 route (no doc needed)

### Changed
- All write operations now run on Revit main thread via IExternalEventHandler
- Transaction handling moved inside dedicated routes (not generic execute_code)
- Route handlers receive `doc` as parameter instead of using `revit.doc`

### Technical Details
The key insight: when a route handler function includes `doc` as a parameter, pyRevit's Routes framework automatically:
1. Queues the handler via IExternalEventHandler
2. Executes on Revit's main thread
3. Passes the active document as the `doc` argument

```python
# ❌ Old pattern - runs on background thread, transactions fail
@api.route('/endpoint/', methods=["POST"])
def handler(request):
    doc = revit.doc  # Gets doc but still on wrong thread
    
# ✅ New pattern - runs on main thread via IExternalEventHandler
@api.route('/endpoint/', methods=["POST"])  
def handler(doc, request):  # doc parameter triggers handler.py
    # Already on main thread, transactions work
```

---

## [1.5.0] - 2026-01-20

### Added
- `place_workplane_families` server route for window placement
- `place_workplane_windows` server route for window placement workflow
- `coordinate_converter` route and tool
- `create_walls_at_lines` route and tool
- `batch_family_placement` route and tool

### Changed
- Improved IFC element querying with transform support

---

## [1.4.0] - 2026-01-15

### Added
- IFC query tools (`query_ifc_elements`, `get_ifc_element_properties`)
- Parameter tools (`get_parameter`, `set_parameter`, `get_all_parameters`)
- Bulk parameter operations (`set_parameters_bulk`, `set_parameters_multi`)
- `batch_update` for multi-element parameter updates

---

## [1.3.0] - 2026-01-10

### Added
- Selection inspection tools
- `inspect_element` - deep inspection of any element by ID
- `quick_count` - fast filtered element counting
- `get_link_status` - linked model information

---

## [1.2.0] - 2026-01-05

### Added
- Color visualization tools (`color_splash`, `clear_colors`)
- `list_category_parameters` for discovering colorable parameters
- View export improvements

---

## [1.1.0] - 2025-12-20

### Added
- `execute_revit_code` tool for dynamic IronPython execution
- Current view tools (`get_current_view_info`, `get_current_view_elements`)
- Family listing with filters

---

## [1.0.0] - 2025-12-01

### Initial Release
- Basic MCP server with FastMCP
- pyRevit Routes integration
- Core tools: status, model_info, list_levels, place_family
- View export functionality
