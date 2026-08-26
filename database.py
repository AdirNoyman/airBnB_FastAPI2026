from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

import models.models  # Import the models module to ensure that the model is registered with SQLModel, BEFORE creating the database tables. This is necessary because SQLModel needs to know about the models in order to create the corresponding tables in the database. If the models are not imported before creating the tables, SQLModel will not be aware of them and will not create the necessary tables.

sqlite_file_name = "database.db"  # Name of the SQLite database file
sqlite_url = f"sqlite:///{sqlite_file_name}"  # SQLite connection URL

engine = create_engine(
    # connect_args={"check_same_thread": False} - This argument is necessary for SQLite to allow multiple threads to access the database simultaneously. So a single connection can be shared across multiple threads that were invoked serving the same request.
    sqlite_url,
    connect_args={"check_same_thread": False},
    echo=True,  # In development only, output SQL statements to the console for debugging purposes
)


def create_db_and_tables():
    # Create the database tables based on the models defined in the models module
    SQLModel.metadata.create_all(engine)


def get_session():
    # The 'with' keyword tells python to terminate the db connection after the session is no more needed. The 'yield' keyword tells the program that the session is being used as long as the FastAPI route handler needs it (meaning the function is not returning immediately)
    with Session(engine) as session:
        yield session


SessionDependency = Annotated[Session, Depends(get_session)]
