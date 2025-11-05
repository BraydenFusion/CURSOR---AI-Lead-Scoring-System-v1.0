from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Import sys path to ensure app module can be imported
import sys
import os
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

# Set environment variable for dotenv
os.environ.setdefault("ENV_FILE", str(backend_dir / ".env"))

# Create Base directly to avoid import issues
from sqlalchemy.orm import declarative_base
Base = declarative_base()

# Import models after Base is defined
# Import models directly to avoid circular dependencies
from app.models.lead import Lead  # noqa: F401
from app.models.activity import LeadActivity  # noqa: F401
from app.models.score_history import LeadScoreHistory  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.assignment import LeadAssignment  # noqa: F401
from app.models.ai_scoring import LeadScore, LeadEngagementEvent, LeadInsight  # noqa: F401
from app.models.note import LeadNote  # noqa: F401
from app.models.notification import Notification  # noqa: F401

# Now we need to attach the models to this Base
# But actually, the models already use Base from database.py
# So we need to import the real Base from database
# Let's use a workaround - import database after setting up env
import sys
sys.path.insert(0, str(backend_dir))

# Actually, let's just use the models' Base
# Re-import Base from the actual database module after all models are loaded
from app.database import Base as RealBase
Base.metadata = RealBase.metadata

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Get database URL from environment or config
from dotenv import load_dotenv
load_dotenv(backend_dir / ".env")
# Use app.config to get the database URL
from app.config import get_settings
settings = get_settings()
database_url = str(settings.database_url)
# SQLAlchemy 2.0 with psycopg3 supports postgresql+psycopg:// directly
# Keep the psycopg driver - don't remove it
# Note: Alembic uses SQLAlchemy's engine, which will use psycopg3 automatically
config.set_main_option("sqlalchemy.url", database_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Use the app's database engine directly to avoid driver issues
    from app.database import engine
    connectable = engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
