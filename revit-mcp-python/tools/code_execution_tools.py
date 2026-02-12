# -*- coding: utf-8 -*-
"""Code execution tools for the MCP server."""

from fastmcp import Context
from .utils import format_response


def register_code_execution_tools(mcp, revit_get, revit_post, revit_image=None):
    """Register code execution tools with the MCP server."""
    # Note: revit_get and revit_image are unused but kept for interface consistency
    _ = revit_get, revit_image  # Acknowledge unused parameters

    @mcp.tool()
    async def execute_revit_code(
        code: str,
        description: str = "Code execution",
        use_transaction: bool = True,
        ctx: Context = None
    ) -> str:
        """
        Execute IronPython code directly in Revit context.

        This tool allows you to send IronPython 2.7.12 code to be executed inside Revit.
        The code has access to:
        - doc: The active Revit document
        - DB: Revit API Database namespace
        - revit: pyRevit module
        - print: Function to output text (returned in response)

        Use this when the existing MCP tools cannot accomplish what you need.

        Args:
            code: The IronPython code to execute (as a string)
            description: Optional description of what the code does
            use_transaction: Whether to wrap code in a Revit transaction (default: True)
                           Set to False for read-only operations to improve performance.
                           Set to True when modifying the model (creating/deleting elements,
                           changing parameters, etc.)
            ctx: MCP context for logging

        Returns:
            Execution results including any output or errors

        Example (read-only, no transaction needed):
            execute_revit_code(
                code='''
                    print("Document title:", doc.Title)
                    walls = DB.FilteredElementCollector(doc).OfCategory(
                        DB.BuiltInCategory.OST_Walls).WhereElementIsNotElementType()
                    print("Number of walls:", len(list(walls)))
                ''',
                description="Count walls",
                use_transaction=False
            )

        Example (modification, transaction required):
            execute_revit_code(
                code='''
                    # Find element and set parameter
                    elem = doc.GetElement(DB.ElementId(12345))
                    param = elem.LookupParameter("Comments")
                    if param:
                        param.Set("Updated via MCP")
                        print("Parameter updated")
                ''',
                description="Update element comment",
                use_transaction=True
            )
        """
        try:
            payload = {
                "code": code,
                "description": description,
                "use_transaction": use_transaction
            }

            if ctx:
                trans_info = "with transaction" if use_transaction else "without transaction"
                ctx.info("Executing code ({}): {}".format(trans_info, description))

            response = await revit_post("/execute_code/", payload, ctx, timeout=60.0)
            return format_response(response)

        except (ConnectionError, ValueError, RuntimeError) as e:
            error_msg = "Error during code execution: {}".format(str(e))
            if ctx:
                ctx.error(error_msg)
            return error_msg
