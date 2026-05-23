import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import logging
from app import settings
from app.image_hosting_handler import ImageHostingHandler

"""
Application entry point.
This module configures logging and starts the HTTP server
for the image hosting application.
"""

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] - %(name)s - %(levelname)s: %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(settings.LOG_PATH / 'server.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


def run(server_address=('', 8000), server_class=HTTPServer, handler_class=ImageHostingHandler):
    """
    Starts the HTTP server. The server listens on the given address and uses ImageHostingHandler
        to process incoming HTTP requests.
    """
    logger.info(f'Starting HTTP server on {server_address}')
    try:
        httpd = server_class(server_address, handler_class)  # noqa
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info('Server stopped by user')
        httpd.server_close()
    except Exception as e:
        logger.error(f'Exception occurred: {e}')


if __name__ == '__main__':
    run()
