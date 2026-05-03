import html
import urllib.parse
from os import environ
from urllib import parse
import uuid

import logging
import multipart

from app.settings import MEDIA_PATH
from app.base_handler import BaseHandler

logger = logging.getLogger(__name__)


class ImageHostingHandler(BaseHandler):

    def do_GET(self):
        logger.info(f'GET {self.client_address[0]}:{self.path}')

        if self.path.startswith('/api/'):
            # images list /api/images
            # image /api/images/<id>
            if self.path == '/api/images':
                self.get_images()
            elif self.path.startswith('/api/images/'):
                name = self.path.split('/')[-1]
                self.send_media_file(name)

        elif self.path == '/':
            self.template_response('index.html')
        elif self.path == '/upload':
            self.template_response('upload.html')
        elif self.path == '/images':
            self.template_response('images.html')

        # elif any((self.path.endswith(ext) for ext in ['.css', '.js', '.png'])):
        #     self.send_static_file(self.path)
        else:
            self.template_response('Not found', 404)

    def do_POST(self):
        logger.info(f'POST {self.client_address[0]}:{self.path}')
        if self.path == '/api/upload':
            unique_id = uuid.uuid4()
            filename = self.upload_file(str(unique_id)[:8])
            if filename:
                self.json_response({
                    'message': 'File uploaded successfully',
                    'filename': filename,
                }, status_code=201)
            else:
                self.json_response({
                    'message': 'Invalid file type or file size',
                })
            self.json_response({
                'message': 'File uploaded successfully',
                'file': filename
            }, 201)
        else:
            html.response('Not found', 405)

    def do_DELETE(self):
        # delete image by name
        logger.info(f'DELETE {self.client_address[0]}:{self.path}')
        if self.path.startswith('/api/images/'):
            name = self.path.split('/')[-1]
            self.delete_image(name)

    def get_images(self):
        self.json_response({
            'images': [f.name for f in MEDIA_PATH.iterdir() if
                       f.name != '.gitkeep']
        })

    def delete_image(self, name):
        try:
            (MEDIA_PATH / name).unlink()
            logger.info(f'Image {name} deleted successfully')
            self.json_response({'message': 'Image deleted'}, status_code=204)
        except FileNotFoundError:
            logger.info(f'Image {name} not found (on delete)')
            self.json_response({'message': 'Image not found'}, status_code=404)
