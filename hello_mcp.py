from fastmcp import FastMCP
import os

mcp = FastMCP("Hello MCP")

@mcp.tool()
def greet(name: str) -> str:
    return f"Hello, {name}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))

    mcp.run(
    transport="http",
    host="0.0.0.0",
    port=port
    )