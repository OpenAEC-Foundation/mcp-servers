# -*- coding: utf-8 -*-
"""Utility functions for MCP tools"""

import json


def format_response(response):
    """Helper function to format API responses consistently for MCP tools.

    Args:
        response: The response from a revit_get or revit_post call, can be dict or string

    Returns:
        str: Formatted string response suitable for MCP tool return values
    """
    # Handle string responses (usually errors from httpx)
    if not isinstance(response, dict):
        return str(response)

    # Check if response is wrapped in a "data" key (pyRevit routes behavior)
    # If so, unwrap it for processing
    if "data" in response and isinstance(response["data"], dict) and len(response) <= 2:
        response = response["data"]

    # Check for explicit error
    if "error" in response:
        error_msg = response.get("error", "Unknown error occurred")
        traceback_info = response.get("traceback", "")

        error_parts = ["=== ERROR ==="]
        error_parts.append("Error: {}".format(error_msg))

        if traceback_info:
            error_parts.append("\n=== TRACEBACK ===")
            error_parts.append(traceback_info)

        return "\n".join(error_parts)

    # Get status for special handling
    status = response.get("status", "").lower()
    health = response.get("health", "").lower()

    # Code execution with output - return raw output
    if "output" in response:
        return response["output"]

    # Status check response - special human-readable formatting
    if status == "active" and health == "healthy":
        status_parts = ["=== REVIT STATUS ==="]
        status_parts.append("Status: {}".format(response.get("status", "Unknown")))
        status_parts.append("Health: {}".format(response.get("health", "Unknown")))
        if "api_name" in response:
            status_parts.append("API: {}".format(response["api_name"]))
        if "document_title" in response:
            status_parts.append("Document: {}".format(response["document_title"]))
        return "\n".join(status_parts)

    # All other responses (including data-rich responses) - return as formatted JSON
    # This ensures selection tools, quick_count, inspect_element, etc. return their full data
    return json.dumps(response, indent=2, ensure_ascii=False, default=str)
