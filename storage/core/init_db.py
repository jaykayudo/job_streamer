from loguru import logger
from storage.core.engine import engine, BaseModel
from storage.core.models import *


def init_db():
    logger.info("Initializing database")
    BaseModel.metadata.create_all(bind=engine)
    logger.info("Database initialized")


if __name__ == "__main__":
    init_db()
