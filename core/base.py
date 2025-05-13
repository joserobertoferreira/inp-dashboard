import streamlit as st
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

db_schema = st.secrets['database'].get('schema')

metadata_obj = MetaData(schema=db_schema)


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    This class uses a custom metadata object to set the schema for all models.
    """

    metadata = metadata_obj
