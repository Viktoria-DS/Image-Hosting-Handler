import html
import urllib.parse
from os import environ
from urllib import parse
import uuid

import logging
import multipart
from psycopg import DatabaseError

from app.db_manager import DBManager
from app.settings import MEDIA_PATH
from app.base_handler import BaseHandler

logger = logging.getLogger(__name__)


class ImageHostingHandler(BaseHandler):
    def __init__(self, *args, **kwargs):
        self.db: DBManager = DBManager()
        super().__init__(*args, **kwargs)

    def do_GET(self):
        logger.info(f'GET {self.client_address[0]}:{self.path}')

        api_handlers = {
            '/api/images': self.get_images_names,
            '/api/images-data': self.get_images,
        }
        templates = {
            '/': 'index.html',
            '/upload': 'upload.html',
            '/images': 'images.html',
        }
        if self.path in templates:
            self.template_response(templates[self.path])
            return
        elif self.path in api_handlers:
            api_handlers[self.path]()
            return
        else:
            self.template_response('Not found', 404)

    def do_POST(self):
        logger.info(f'POST {self.client_address[0]}:{self.path}')
        if self.path == '/api/upload':
            image_dict = self.upload_file()
            if image_dict:
                self.db.add_image(image_dict)
                self.json_response({
                    'message': 'File uploaded successfully',
                    'filename': image_dict,
                }, status_code=201)
            else:
                self.json_response({
                    'message': 'Invalid file type or file size',
                })
        else:
            html.response('Not found', 405)

    def do_DELETE(self):
        logger.info(f'DELETE {self.client_address[0]}:{self.path}')
        if self.path.startswith('/api/images/'):
            name = self.path.split('/')[-1]
            name, file_type = name.rsplit('.', 1)
            self.delete_image(name, file_type)
            # delete from db

    def get_images_names(self):
        self.json_response({
            'images': self.db.get_images_names()}) # get names from db

    def get_images(self):
        images = self.db.get_images()
        res_images = [
            {
                'id': i[0],
                'filename': i[1],
                'original_name': i[2],
                'size': i[3],
                'upload_time': i[4].strftime("%Y-%m-%d %H:%M:%S"),
                'file_type': i[5],
            } for i in images]
        self.json_response({
            'images': res_images
        })

    def delete_image(self, name: str, file_type: str):
        try:
            self.db.delete_image(name)
            (MEDIA_PATH / (name + '.' + file_type)).unlink()
            logger.info(f'Image {name} deleted successfully')
            self.json_response({'message': 'Image deleted'}, status_code=204)
        except FileNotFoundError:
            logger.info(f'File {name} not found (on delete)')
            self.json_response({'message': 'Image not found'}, status_code=404)
        except DatabaseError:
            logger.info(f' {name} not found in database (on delete)')
            self.json_response({'message': 'Image not found'}, status_code=404)
