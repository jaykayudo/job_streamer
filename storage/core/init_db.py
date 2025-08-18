from storage.core.engine import engine, BaseModel
from storage.core.models import *
from utils.logging import JobStreamerLogger

logger = JobStreamerLogger().get_logger()


def init_db():
    logger.info("Initializing database")
    BaseModel.metadata.create_all(bind=engine)
    logger.info("Database initialized")


if __name__ == "__main__":
    init_db()
