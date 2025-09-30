"""Manage.py script for the Chat Service.
This script provides command-line interface (CLI) commands for managing the Chat Service.
"""
import os
import subprocess
import asyncio
from app.core.database import init_db as initialize_database, drop_db as drop_database

import typer

app = typer.Typer()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.command()
def init_db():
    """Initialize the database and create collections."""
    async def task():
        typer.echo("Initializing the database and creating collections...")
        await initialize_database()
        typer.echo("✅ Database collections created successfully.")

    asyncio.run(task())

@app.command()
def drop_db():
    """Drop all database collections."""
    async def task():
        typer.echo("Dropping all database collections...")
        await drop_database()
        typer.echo("✅ Database collections dropped successfully.")

    asyncio.run(task())

@app.command()
def test():
    """Run tests for the Chat Service."""
    typer.echo("Running tests...")
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/", "-v"],
        cwd=BASE_DIR,
        capture_output=False
    )
    if result.returncode == 0:
        typer.echo("✅ All tests passed!")
    else:
        typer.echo("❌ Some tests failed!")
        raise typer.Exit(1)

@app.command()
def lint():
    """Run linting for the Chat Service."""
    typer.echo("Running pylint...")
    result = subprocess.run(
        ["python", "-m", "pylint", "app/"],
        cwd=BASE_DIR,
        capture_output=False
    )
    if result.returncode == 0:
        typer.echo("✅ Linting passed!")
    else:
        typer.echo("❌ Linting issues found!")

@app.command()
def format_code():
    """Format code using black."""
    typer.echo("Formatting code with black...")
    subprocess.run(["python", "-m", "black", "app/"], cwd=BASE_DIR)
    typer.echo("✅ Code formatted!")

@app.command()
def run():
    """Run the Chat Service in development mode."""
    typer.echo("Starting Chat Service...")
    subprocess.run(["python", "server.py"], cwd=BASE_DIR)

@app.command()
def health():
    """Check service health."""
    import requests
    try:
        response = requests.get("http://localhost:4004/api/v1/chat/health", timeout=5)
        if response.status_code == 200:
            typer.echo("✅ Chat Service is healthy!")
        else:
            typer.echo(f"❌ Chat Service returned status: {response.status_code}")
    except requests.RequestException as e:
        typer.echo(f"❌ Chat Service is not responding: {e}")

if __name__ == "__main__":
    app()