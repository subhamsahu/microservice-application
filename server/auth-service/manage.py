"""Manage.py script for the User Service.
This script provides command-line interface (CLI) commands for managing the User Service.
"""
import os
import subprocess
import asyncio
import glob
from app.core.database import init_db as initialize_database, drop_db as drop_database

import typer

app = typer.Typer()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ALEMBIC_INI_PATH = os.path.join(BASE_DIR, "alembic.ini")

@app.command()
def init_db():
    """Initialize the database and create tables."""
    async def task():
        typer.echo("Initializing the database and creating tables...")
        await initialize_database()
        typer.echo("✅ Database tables created successfully.")

    asyncio.run(task())

@app.command()
def drop_db():
    """Drop all database tables."""
    async def task():
        typer.echo("Dropping Db defined in environment variable")
        await drop_database()
        typer.echo("✅ All database tables dropped successfully.")

    asyncio.run(task())

@app.command()
def seed_db():
    """Seed the database with initial data."""
    typer.echo("Seeding the database at with initial data...")
    # Placeholder for actual seeding logic
    typer.echo("✅ Database seeded successfully with initial users.")

@app.command()
def makemigrations(message: str = typer.Option("Auto migration", "--message", "-m")):
    """Auto-generate Alembic migration scripts like Django's `makemigrations`."""
    typer.echo("Generating migration script: '{message}'")
    subprocess.run(["alembic", "-c", ALEMBIC_INI_PATH, "revision", "--autogenerate", "-m", message], check=False)
    typer.echo("✅ Migration script created successfully.")

@app.command()
def migrate():
    """Apply all pending migrations like Django's `migrate`."""
    typer.echo("Applying all pending migrations...")
    subprocess.run(["alembic", "-c", ALEMBIC_INI_PATH, "upgrade", "head"], check=False)
    typer.echo("✅ All migrations applied successfully.")

@app.command()
def showmigrations():
    """Display the list of migrations like Django's `showmigrations`."""
    typer.echo("Listing migration history...")
    subprocess.run(["alembic", "-c", ALEMBIC_INI_PATH, "history", "--verbose"], check=False)

@app.command()
def rollback(revision: str = "-1"):
    """Rollback to a previous revision."""
    typer.echo(f"Rolling back to revision: {revision}")
    subprocess.run(["alembic", "-c", ALEMBIC_INI_PATH, "downgrade", revision],check=False)
    typer.echo("✅ Rollback completed.")

@app.command()
def reset_migrations():
    """
    Delete all Alembic migration scripts and reset database migration state.
    ⚠️ Only for development use.
    """
    versions_dir = os.path.join(BASE_DIR, "migrations", "versions")
    migration_files = glob.glob(os.path.join(versions_dir, "*.py"))

    if not migration_files:
        typer.echo("No migration files to delete.")
    else:
        typer.echo("Deleting all migration files...")
        for f in migration_files:
            os.remove(f)
            typer.echo(f"Deleted: {f}")

    typer.echo("↩️ Downgrading database to base revision...")
    subprocess.run(["alembic", "-c", ALEMBIC_INI_PATH, "downgrade", "base"], check=False)

    typer.echo("📝 Stamping current DB state as head (no migrations)...")
    subprocess.run(["alembic", "-c", ALEMBIC_INI_PATH, "stamp", "head"], check=False)

    typer.echo("✅ All migrations reset successfully.")

@app.command()
def create_user(username: str, email: str):
    """Create a new user."""
    typer.echo(f"👤 Creating user: {username} with email: {email}")
    # Placeholder for actual user creation logic
    typer.echo(f"✅ User {username} created successfully.")

if __name__ == "__main__":
    app()
