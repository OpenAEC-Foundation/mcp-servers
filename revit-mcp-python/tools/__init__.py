# -*- coding: utf-8 -*-
"""Tool registration system for Revit MCP Server"""


def register_tools(mcp_server, revit_get_func, revit_post_func, revit_image_func):
    """Register all tools with the MCP server"""
    from .status_tools import register_status_tools
    from .view_tools import register_view_tools
    from .family_tools import register_family_tools
    from .model_tools import register_model_tools
    from .colors_tools import register_colors_tools
    from .code_execution_tools import register_code_execution_tools
    from .selection_tools import register_selection_tools
    from .parameter_tools import register_parameter_tools
    from .ifc_tools import register_ifc_tools
    from .modification_tools import register_modification_tools

    register_status_tools(mcp_server, revit_get_func)
    register_view_tools(mcp_server, revit_get_func, revit_post_func, revit_image_func)
    register_family_tools(mcp_server, revit_get_func, revit_post_func)
    register_model_tools(mcp_server, revit_get_func)
    register_colors_tools(mcp_server, revit_get_func, revit_post_func)
    register_code_execution_tools(
        mcp_server, revit_get_func, revit_post_func, revit_image_func
    )
    register_selection_tools(mcp_server, revit_get_func, revit_post_func)
    register_parameter_tools(mcp_server, revit_get_func, revit_post_func)
    register_ifc_tools(mcp_server, revit_get_func, revit_post_func)
    register_modification_tools(mcp_server, revit_get_func, revit_post_func)
