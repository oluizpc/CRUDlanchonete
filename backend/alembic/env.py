# alembic/env.py

from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
# from app.models import User, Produto, Cliente, Pedido, PedidoProduto, SituacaoMesa, Mesa, TipoPagamento, Pagamento # REMOVA ESTA LINHA
from alembic import context

# Adicione o seu diretório de projeto ao sys.path para que os imports funcionem
import sys
from os.path import abspath, dirname
sys.path.append(dirname(dirname(abspath(__file__))))

# Importe a sua 'Base' e todos os seus modelos para o Alembic "enxergá-los"
from app.database import Base
from app.models import User, Produto, Cliente, Pedido, PedidoProduto, SituacaoMesa, Mesa, Pagamento, TipoPagamento


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# O Alembic precisa saber onde encontrar os metadados dos seus modelos.
# Mude o 'target_metadata' para a sua 'Base.metadata' importada.
target_metadata = Base.metadata


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
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

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