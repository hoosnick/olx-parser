import sys
import time
from contextlib import suppress

import schedule
from loguru import logger

from .core.app_factory import ApplicationFactory
from .core.config import LOG_TO_FILE, LOGGING_LEVEL, SCHEDULER_INTERVAL_SECONDS
from .utils.logging_utils import handle_exception, setup_logging


def main() -> None:
    setup_logging(LOGGING_LEVEL, LOG_TO_FILE)
    sys.excepthook = handle_exception

    logger.info("Starting OLX Parser application")

    olx_service, database = ApplicationFactory.create_services()

    schedule.every(SCHEDULER_INTERVAL_SECONDS).seconds.do(
        olx_service.fetch_and_process_offers
    )
    logger.info("Scheduled scraping every %d second(s)" % SCHEDULER_INTERVAL_SECONDS)

    try:
        # Run initial scrape
        logger.info("Running initial offer fetch")
        olx_service.fetch_and_process_offers()

        while True:
            schedule.run_pending()
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Shutting down gracefully")

    except Exception as e:
        logger.critical("Fatal error in main loop: %s" % e)
        raise

    finally:
        with suppress(Exception):
            olx_service.close()

        with suppress(Exception):
            database.close()

        logger.info("Application shutdown complete")


if __name__ == "__main__":
    main()
