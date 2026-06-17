from app.state import mcp
from app.orchaestrator import embed_and_store


@mcp.tool()
def greet(name: str) -> str:
    embed_and_store(name)
    return f"Hello, {name}"