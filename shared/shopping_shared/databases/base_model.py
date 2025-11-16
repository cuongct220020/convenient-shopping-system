# shared/shopping_shared/databases/base_model.py
from sqlalchemy.orm import declarative_base
from sqlalchemy import MetaData

# Define a naming convention for constraints to ensure Alembic works smoothly.
# See: https://alembic.sqlalchemy.org/en/latest/naming.html
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

# Create a metadata object with the naming convention
metadata = MetaData(naming_convention=convention)

# Create a base class for declarative models that all models in this service will inherit from.
Base = declarative_base(metadata=metadata)
