#   Title: log_config.py
#    Authors: Casey Rose, Darreon Tolen and Jennifer Hoitenga
#    Date: 03/02/2025
#    Description: Logging connection shared file.

import logging  # for logging errors

# Configure Logging
LOG_FILE = "error_log.txt"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Create a logger instance
logger = logging.getLogger(__name__)
