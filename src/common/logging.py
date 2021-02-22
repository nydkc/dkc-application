import os
import logging
import sys
import google.cloud.logging


def configure_logging():
    if os.getenv("GAE_ENV", "").startswith("standard"):
        # Production in the standard environment
        _configure_app_engine_logging()
    else:
        _configure_local_logging()


def _configure_app_engine_logging():
    # Instantiates a client
    client = google.cloud.logging.Client()

    # Retrieves a Cloud Logging handler based on the environment
    # you're running in and integrates the handler with the
    # Python logging module. By default this captures all logs
    # at INFO level and higher
    client.get_default_handler()
    client.setup_logging()


def _configure_local_logging():
    # Local execution.
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s.%(msecs)03d] %(name)s [%(levelname)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
