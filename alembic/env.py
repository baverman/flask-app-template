import sys
sys.path.insert(0, '.')

from logging.config import fileConfig
from alembic import context
from sqlalchemy.engine.reflection import Inspector

config = context.config
fileConfig(config.config_file_name)

from my_project import db
db.import_all()
target_metadata = db.Base.metadata


def run_migrations_offline():
    context.configure(url=db.engine.url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    # restrict automigrations to defined models only
    get_table_names = Inspector.get_table_names
    Inspector.get_table_names = (lambda *args, **kwargs:
        set(get_table_names(*args, **kwargs)).intersection(target_metadata.tables))

    with db.engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
