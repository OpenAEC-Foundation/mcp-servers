# UV Package Manager Setup

## Installation

### Windows (PowerShell)
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Add to PATH if needed:
```powershell
$env:Path = "C:\Users\$env:USERNAME\.local\bin;$env:Path"
```

### Mac
```bash
brew install uv
```

### Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Project Setup

### Option 1: Using existing venv (recommended for this project)

This project can use a dedicated venv outside the project directory.

```bash
# Activate existing venv
<path-to-venv>\Scripts\activate

# Install/update dependencies
uv pip install -r requirements.txt
```

### Option 2: Create new venv with uv

```bash
# Create venv in project folder
uv venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt
```

## Running the MCP Server

### Development/Testing
```bash
# With MCP Inspector
mcp dev main.py
```

### Production (Claude Desktop)
Configure in `%APPDATA%\Claude\claude_desktop_config.json`:

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

## Dependencies

Current requirements:
- `mcp[cli]` - Model Context Protocol SDK
- `httpx` - Async HTTP client

Install all:
```bash
uv pip install -r requirements.txt
```

## Troubleshooting

### uv not found after install
Restart terminal or add to PATH manually.

### Permission errors on Windows
Run PowerShell as Administrator for initial install.

### Venv activation issues
Use full path to python.exe instead of activating venv.
