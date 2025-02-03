import logging
import sys

def configure_logging():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)

    root_logger.addHandler(console_handler)

    uvicorn_logger = logging.getLogger("uvicorn.access")
    uvicorn_logger.handlers = [console_handler]

    return root_logger 