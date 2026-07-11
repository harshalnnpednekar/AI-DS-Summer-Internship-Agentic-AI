"""
run_backend.py — Windows-compatible launcher for the EduAgent backend.

On Windows with Python 3.12+, asyncio.run() creates a ProactorEventLoop by
default, which is incompatible with psycopg async. We use loop_factory to
force SelectorEventLoop.
"""
import asyncio
import selectors
import uvicorn


async def main():
    config = uvicorn.Config(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True
    )
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(
        main(),
        loop_factory=lambda: asyncio.SelectorEventLoop(selectors.SelectSelector()),
    )
