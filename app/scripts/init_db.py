from app.db.session import create_db_and_tables
from app.core.config import get_settings
from app.core.logging import get_logger, setup_logging


settings = get_settings()
setup_logging(
    level=settings.log_level,
    json_enabled=settings.log_json,
    access_log_enabled=settings.log_access_enabled,
)
logger = get_logger(__name__)


def main() -> None:
    create_db_and_tables()
    logger.info("database tables created successfully")


if __name__ == "__main__":
    main()
