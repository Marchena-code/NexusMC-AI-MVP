from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = None
import sys
import os

# Añadir la ruta 'app' al path para que Python encuentre los módulos
# Asumiendo que env.py está en alembic/ y app/ está en el nivel superior (backend/)
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

# Importar la Base de nuestros modelos SQLAlchemy
from app.core.db.database import Base
# Importar TODOS los modelos para que Alembic los detecte
# Necesitarás añadir una línea por cada archivo de modelo que crees
from app.core.db.models import user # ¡Importante importar los modelos aquí!

# Asignar los metadatos de la Base a target_metadata para que Alembic los detecte
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
        target_metadata = Base.metadata,
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
    # Usar el engine ya configurado en database.py
    # que lee la URL desde el archivo .env correctamente.
    from app.core.db.database import engine as connectable, Base

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=Base.metadata # Usar Base.metadata directamente
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
