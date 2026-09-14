from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base

TEST_DATABASE_URL = (
    "postgresql://postgres:manaswin@localhost:5432/"
    "smart_inventory_test"
)

test_engine = create_engine(
    TEST_DATABASE_URL
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)


def setup_test_database():

    Base.metadata.create_all(
        bind=test_engine
    )


def teardown_test_database():

    Base.metadata.drop_all(
        bind=test_engine
    )


def get_test_db():

    db = TestingSessionLocal()

    try:

        yield db

    finally:

        db.close()