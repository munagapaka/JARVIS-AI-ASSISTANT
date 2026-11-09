# tool_executor.py

from tool_registry import get_tool_function


def execute_tool(tool_name, tool_args):
    """Execute a registered J.A.R.V.I.S. tool safely."""
    try:
        function = get_tool_function(tool_name)
        if function is None:
            return f"Unknown tool: {tool_name}"
        if tool_args is None:
            tool_args = {}
        return function(**dict(tool_args))
    except TypeError as e:
        return f"Invalid arguments for '{tool_name}': {e}"
    except Exception as e:
        return f"Tool '{tool_name}' failed: {e}"
