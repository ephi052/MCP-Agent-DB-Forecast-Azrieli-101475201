# agent_weather.py
# ---------------------------------------------------------------------
"""
Drives the FastMCP weather-db server and asks an OpenAI agent to
• fetch next-week forecast for NYC,
• store readings in SQLite,
• plot the last 7 days.
All secrets and flags come from .env.
"""

from __future__ import annotations
import asyncio, os
from dotenv import load_dotenv

load_dotenv()                         # 1) load .env into process env

# ------------------------------------------------------------------ #
# SDK imports
from agents import Agent, Runner
from agents.mcp.server import MCPServerStdio

# ------------------------------------------------------------------ #
# Environment helpers with sensible fall-backs
MCP_WEATHER_DB_CMD  = os.getenv("MCP_WEATHER_DB_CMD",  "python")
MCP_WEATHER_DB_ARGS = os.getenv("MCP_WEATHER_DB_ARGS", "server.py").split()
MODEL_NAME          = os.getenv("MODEL_NAME",          "gpt-4o-mini")

# ------------------------------------------------------------------ #
async def main() -> None:
    # spin up the server for this run only
    async with MCPServerStdio(
        name="weather-db",
        params={"command": MCP_WEATHER_DB_CMD, "args": MCP_WEATHER_DB_ARGS},
    ) as weather_db_srv:

        agent = Agent(
            name="Weather-DB-Agent",
            instructions=(
                "You can call the weather-db tools to fetch Open-Meteo forecasts, "
                "save / read / update / delete rows in SQLite, and plot the past week."
            ),
            mcp_servers=[weather_db_srv],
            model=MODEL_NAME,
        )

        user_input = (
            "Fetch the forecast for Tokyo, Japan from 2025-05-25 to 2025-05-31, "
            "store each day’s mean temperature in the database, then plot the past week."
        )

        result = await Runner.run(starting_agent=agent, input=user_input)
        # Runner returns a RunResult → use .final_output
        print("\n=== AGENT REPLY ===\n", result.final_output)

# ------------------------------------------------------------------ #
if __name__ == "__main__":
    # asyncio.run() creates the event-loop & waits for completion
    asyncio.run(main())
