from app.state import mcp
from app.orchaestrator import embed_and_ask


@mcp.tool()
def ask(question: str) -> str:
    return embed_and_ask(question)
