# Lessons Learned - Revit MCP Server Development

This document captures critical insights from developing the Revit MCP server, particularly around threading, IronPython compatibility, and coordinate systems.

## 1. Threading & Transaction Handling

### The Problem
Revit API operations must run on Revit's main UI thread. pyRevit Routes runs HTTP handlers on background threads by default, causing transaction failures:

```
InvalidOperationException: Starting a transaction from an external application 
running outside of API context is not allowed.
```

### The Solution: `doc` Parameter Triggers IExternalEventHandler

When a route handler function includes `doc` (or `uidoc`, `uiapp`) as a parameter, pyRevit's Routes framework automatically:

1. Queues the handler via `IExternalEventHandler`
2. Executes on Revit's main thread
3. Passes the active document as the argument

```python
# ❌ WRONG - Runs on background thread, transactions FAIL
@api.route('/endpoint/', methods=["POST"])
def handler(request):
    doc = revit.doc  # Still on wrong thread!
    with Transaction(doc, "Op") as t:
        t.Start()  # FAILS!

# ✅ CORRECT - Runs on main thread via IExternalEventHandler
@api.route('/endpoint/', methods=["POST"])
def handler(doc, request):  # 'doc' parameter triggers main thread execution
    with Transaction(doc, "Op") as t:
        t.Start()  # WORKS!
```

### Important Notes

1. **Parameter name matters**: Must be exactly `doc`, `uidoc`, or `uiapp`
2. **Order doesn't matter**: `handler(doc, request)` and `handler(request, doc)` both work
3. **Read-only operations**: Can use `revit.doc` pattern if no transactions needed
4. **After code changes**: Restart Revit - routes are cached in memory

### Reference
The mechanism is implemented in:
```
%APPDATA%\pyRevit-Master\pyrevitlib\pyrevit\routes\server\handler.py
```

Look for `_get_handler_params()` and `ExternalEventHandler` class.

---

## 2. IronPython 2.7 Compatibility

The pyRevit extension runs in IronPython 2.7 (.NET CLR). Follow these rules:

### String Formatting
```python
# ❌ NO f-strings (Python 3.6+ only)
message = f"Count: {count}"

# ✅ Use .format()
message = "Count: {}".format(count)
message = "Name: {name}, ID: {id}".format(name=n, id=i)
```

### Element Name Access
```python
# ❌ Direct .Name access can fail on some element types
name = element.Name

# ✅ Safe pattern using __get__
from pyrevit import DB
name = DB.Element.Name.__get__(element)

# ✅ Or for FamilySymbol
family_name = symbol.FamilyName  # Works
type_name = DB.Element.Name.__get__(symbol)  # Safe
```

### Dictionary/JSON Handling
```python
# ❌ dict.get() with complex defaults can fail
value = data.get("key", {}).get("nested")

# ✅ Explicit checks
value = None
if "key" in data and data["key"]:
    value = data["key"].get("nested")
```

### Import Patterns
```python
# ❌ Relative imports can be tricky
from .utils import helper

# ✅ Explicit imports from known modules
from pyrevit import DB, revit, routes
from utils import helper  # If utils.py is in same folder
import json
import math
```

---

## 3. Coordinate Systems & Unit Conversion

### Revit Internal Units
Revit API uses **feet** internally for all length values.

```python
# Conversion constants
FEET_TO_MM = 304.8
MM_TO_FEET = 1 / 304.8

# Convert user input (mm) to Revit (feet)
x_feet = x_mm / 304.8

# Convert Revit output (feet) to display (mm)  
x_mm = x_feet * 304.8
```

### IFC Transform Coordinates

**Critical Discovery**: IFC `Transform.Origin` represents the **insertion point** at edges/corners, NOT the geometric center!

For windows/doors, the true center is calculated as:
```python
# IFC provides insertion point (corner)
origin = transform.Origin

# Get basis vectors
basis_x = transform.BasisX
basis_y = transform.BasisY

# Calculate true center
# (assumes standard IFC export with origin at front-left)
true_center_x = origin.X + (half_width * basis_x.X) + (front_offset * basis_y.X)
true_center_y = origin.Y + (half_width * basis_x.Y) + (front_offset * basis_y.Y)
true_center_z = origin.Z
```

### WorkPlaneBased Family Orientation

Windows with `normal_y > 0` appear upside down and require 180° rotation:

```python
# Determine if rotation needed
needs_rotation = normal_y > 0

# Create placement plane
normal = XYZ(normal_x, normal_y, 0).Normalize()
plane = Plane.CreateByNormalAndOrigin(normal, point)
sketch_plane = SketchPlane.Create(doc, plane)

# Place family
instance = doc.Create.NewFamilyInstance(
    point, symbol, sketch_plane,
    StructuralType.NonStructural
)

# Apply rotation if needed
if needs_rotation:
    axis = Line.CreateBound(point, point + XYZ.BasisZ)
    ElementTransformUtils.RotateElement(
        doc, instance.Id, axis, math.pi  # 180 degrees
    )
```

---

## 4. Route Registration & Caching

### Routes are Cached
After Revit starts, route handlers are cached in memory. Changes require:
1. Restart Revit, OR
2. Delete pyRevit cache: `%APPDATA%\pyRevit-Master\cache\`

### URL Prefix Required
All routes must include the API name prefix:
```
❌ http://localhost:48884/status/
✅ http://localhost:48884/revit_mcp/status/
```

### Route Not Found Errors
```
RouteHandlerNotDefinedException: Route does not exist: "GET status/"
```
Usually means:
1. Missing `/revit_mcp/` prefix
2. Route not registered in `startup.py`
3. Syntax error in route module (check Revit console)

---

## 5. Error Handling Patterns

### Server Side (pyRevit)
```python
@api.route('/endpoint/', methods=["POST"])
def handler(doc, request):
    try:
        data = json.loads(request.data) if isinstance(request.data, str) else request.data
        
        # Validate required fields
        if not data.get("required_field"):
            return routes.make_response(
                data={"error": "required_field is required"}, 
                status=400
            )
        
        # Do work...
        result = {"status": "success", "data": output}
        return routes.make_response(data=result)
        
    except Exception as e:
        import traceback
        return routes.make_response(
            data={"error": str(e), "traceback": traceback.format_exc()},
            status=500
        )
```

### Client Side (MCP Tools)
```python
@mcp.tool()
async def my_tool(param: str, ctx: Context = None) -> str:
    try:
        response = await revit_post("/endpoint/", {"param": param}, ctx)
        return format_response(response)
    except Exception as e:
        error_msg = "Error: {}".format(str(e))
        if ctx:
            ctx.error(error_msg)
        return error_msg
```

---

## 6. Testing Patterns

### Direct Route Testing (PowerShell)
```powershell
# GET request
Invoke-RestMethod "http://localhost:48884/revit_mcp/status/"

# POST request
$body = @{ category = "Windows" } | ConvertTo-Json
Invoke-RestMethod "http://localhost:48884/revit_mcp/quick_count/" `
    -Method POST -Body $body -ContentType "application/json"
```

### Verify Server is Running
```powershell
Test-NetConnection -ComputerName localhost -Port 48884
```

### Check for Transaction Issues
If operations fail silently or return empty results:
1. Check if handler has `doc` parameter
2. Look for transaction errors in Revit console
3. Test same logic via `execute_code` with `use_transaction=True`

---

## 7. File Synchronization

### Development Locations
- **Server (pyRevit)**: `%APPDATA%\pyRevit-Master\extensions\revit-mcp-python.extension\`
- **Client (MCP)**: `<your-project-path>/revit-mcp-python/`

### After Changes
| Changed | Action |
|---------|--------|
| Server routes | Restart Revit |
| MCP tools | Restart Claude Desktop |
| Both | Restart both |

### Backup Strategy
Before major changes, create timestamped backup:
```
_backup_20250127/
├── placement.py
├── modification.py
└── ...
```

---

## 8. Common Pitfalls

### 1. "Starting a transaction from external application"
**Cause**: Handler missing `doc` parameter  
**Fix**: Add `doc` as first parameter

### 2. "Route does not exist"
**Cause**: Missing URL prefix or registration  
**Fix**: Use `/revit_mcp/` prefix, check `startup.py`

### 3. Empty response from write operations
**Cause**: Transaction never committed  
**Fix**: Ensure `doc` parameter triggers main thread execution

### 4. "Name" attribute errors
**Cause**: IronPython property access issues  
**Fix**: Use `DB.Element.Name.__get__(element)`

### 5. Coordinate offset issues
**Cause**: IFC origin vs geometric center mismatch  
**Fix**: Apply correction formula with BasisX/BasisY vectors

---

## Summary Checklist

Before deploying new routes:

- [ ] Handler has `doc` parameter for write operations
- [ ] No f-strings in IronPython code
- [ ] Element names accessed safely
- [ ] Units converted (mm ↔ feet)
- [ ] Route registered in `startup.py`
- [ ] Tool registered in `tools/__init__.py`
- [ ] Tested via direct HTTP call
- [ ] Tested via MCP tool
- [ ] Documentation updated
