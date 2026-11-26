import asyncio
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

params = StdioServerParameters(
    command=sys.executable,                          # le python de ton .venv
    args=["-m", "complia.mcp_server.server"],
    env=dict(os.environ),                            # transmet OPENAI_API_KEY au serveur
)


async def main():
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            outils = await session.list_tools()
            print("Outils disponibles :")
            for t in outils.tools:
                print(f"- {t.name} : {t.description.splitlines()[0]}")

            print("\nAppel de poser_question...\n")
            res = await session.call_tool(
                "poser_question", {"question": "Qu'est-ce qu'un système d'IA à haut risque ?"}
            )
            print(res.content[0].text)


asyncio.run(main())