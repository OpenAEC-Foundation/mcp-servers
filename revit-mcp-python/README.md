# Revit MCP Python

A pyRevit-based implementation of the [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) for Autodesk Revit.

Connect Large Language Models (like Claude) directly to your Revit models for querying, modifying, and automating BIM workflows.

## Architecture

```
Claude Desktop --> MCP Server (Python 3.x) --> HTTP --> pyRevit Routes (IronPython 2.7) --> Revit API
                   (FastMCP, stdio)              (port 48884)
```

| Component | Location | Runtime |
|-----------|----------|---------|
| MCP Server (client) | `main.py` + `tools/` | Python 3.x via Claude Desktop |
| pyRevit Extension (server) | Installed in pyRevit extensions folder | IronPython 2.7 inside Revit |

## Available Tools (34)

| Category | Tools | Description |
|----------|-------|-------------|
| **Status & Model** | 3 | Connection check, model info, levels |
| **Views** | 4 | Export view as PNG, list views, current view info/elements |
| **Families** | 4 | Place families, list types/categories, WorkPlaneBased placement |
| **Selection** | 5 | Active selection, inspect elements, link status, quick count |
| **Parameters** | 5 | Get/set single or bulk parameters |
| **Modification** | 7 | Batch update, sheets, walls, placement, coordinate conversion |
| **Visualization** | 3 | Color elements by parameter, clear colors |
| **IFC Query** | 2 | Search linked IFC models, get IFC properties |
| **Code Execution** | 1 | Run IronPython code inside Revit |

## Prerequisites

- **Autodesk Revit** with [pyRevit](https://github.com/pyrevitlabs/pyRevit) installed
- **Python 3.11+**
- **Claude Desktop** (or any MCP-compatible client)

## Installation

### 1. Enable pyRevit Routes

1. In Revit, go to pyRevit tab > Settings
2. Navigate to Routes > Enable "Routes Server"
3. Restart Revit

### 2. Install the pyRevit Extension

Copy the `revit-mcp-python.extension/` folder to your pyRevit extensions directory:

```
%APPDATA%\pyRevit-Master\extensions\
```

Or add a custom extension path in pyRevit Settings.

### 3. Install Python Dependencies

```bash
# Using uv (recommended)
uv venv
uv pip install -r requirements.txt

# Or using pip
pip install -r requirements.txt
```

See [README_UV.md](README_UV.md) for detailed uv setup instructions.

### 4. Configure Claude Desktop

Edit `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "Revit MCP Python": {
      "command": "<path-to-venv>\\Scripts\\python.exe",
      "args": ["<path-to-project>/main.py"]
    }
  }
}
```

Replace `<path-to-venv>` with the path to your Python virtual environment and `<path-to-project>` with the path to this repository.

### 5. Restart

- Restart **Revit** to load the pyRevit extension
- Restart **Claude Desktop** to load the MCP server

## Testing

### Test the Routes API directly

```powershell
# Status check
Invoke-RestMethod "http://localhost:48884/revit_mcp/status/"

# Model info
Invoke-RestMethod "http://localhost:48884/revit_mcp/model_info/"

# List families
Invoke-RestMethod "http://localhost:48884/revit_mcp/list_families/?contains=Window&limit=10"
```

### Test via MCP Inspector

```bash
mcp dev main.py
```

Access http://127.0.0.1:6274 to test tools interactively.

## Project Structure

```
revit-mcp-python/
├── main.py                     # FastMCP server entry point
├── tools/                      # MCP tool modules (34 tools)
│   ├── __init__.py             # Tool registration system
│   ├── utils.py                # Response formatting
│   ├── status_tools.py         # Status & connectivity
│   ├── model_tools.py          # Model information
│   ├── view_tools.py           # View export & listing
│   ├── family_tools.py         # Family placement & listing
│   ├── selection_tools.py      # Element selection & inspection
│   ├── parameter_tools.py      # Parameter get/set operations
│   ├── modification_tools.py   # Batch operations & modifications
│   ├── colors_tools.py         # Color visualization
│   ├── ifc_tools.py            # IFC model queries
│   └── code_execution_tools.py # Custom code execution
├── pyproject.toml              # Project configuration
├── requirements.txt            # Python dependencies
├── LLM.txt                     # Development context for LLMs
├── CHANGELOG.md                # Version history
├── LESSONS_LEARNED.md          # Threading & IronPython patterns
└── SKILL.md                    # Claude skill definition
```

## Key Concepts

### Thread Safety

All write operations use pyRevit's `IExternalEventHandler` mechanism. When a route handler includes `doc` as a parameter, pyRevit automatically executes it on Revit's main UI thread.

### Transaction Control

The `execute_revit_code` tool supports explicit transaction control:

```python
# Read-only operations (faster)
execute_revit_code(code="...", use_transaction=False)

# Model modifications (default)
execute_revit_code(code="...", use_transaction=True)
```

### Units

Revit uses **feet** internally. All MCP tools accept **millimeters** and handle conversion automatically.

## Documentation

| Document | Description |
|----------|-------------|
| [LLM.txt](LLM.txt) | Development context for LLMs building on this project |
| [CHANGELOG.md](CHANGELOG.md) | Version history |
| [LESSONS_LEARNED.md](LESSONS_LEARNED.md) | Threading patterns & IronPython compatibility |
| [SKILL.md](SKILL.md) | Claude skill definition |
| [README_UV.md](README_UV.md) | UV package manager setup |

## Notes

- pyRevit Routes runs on port **48884** (first Revit instance)
- The Routes API has **no authentication** - use only on trusted networks
- Extension code must be **IronPython 2.7** compatible (no f-strings)
- All routes use the `/revit_mcp/` URL prefix

## Credits

Based on work by [Juan D. Rodriguez](https://github.com/juandr89) and [Jean-Marc Couffin](https://github.com/jmcouffin).

## License

See [LICENSE](LICENSE) for details.
