import html

from urllib.parse import urlsplit

import logging
from psycopg import DatabaseError

from app.db_manager import DBManager
from app.settings import MEDIA_PATH
from app.base_handler import BaseHandler

logger = logging.getLogger(__name__)


class ImageHostingHandler(BaseHandler):
    """
    HTTP handler for the image hosting application. It manages page rendering, image upload, image listing, pagination,
        and image deletion.
    """
    def __init__(self, *args, **kwargs):
        self.db: DBManager = DBManager()
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handles GET requests: it renders HTML pages and returns image data for the frontend API."""
        logger.info(f"GET {self.client_address[0]}: {self.path}")

        if self.path == '/':
            self.template_response('index.html')
        elif self.path == '/upload':
            self.template_response('upload.html')
        elif self.path.startswith('/images'):
            self.template_response('images.html')
        elif self.path.startswith('/api/images-data'):
            path = urlsplit(self.path)
            page = int(path.query.split('=')[1]) if path.query else 1
            self.get_images(page)
        elif self.path.startswith('/api/images'):
            self.get_images_names()
        else:
            self.html_response('Not Found', 404)

    def do_POST(self):
        """Handles POST requests: it processes image upload requests and saves image metadata to the database."""
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
        """Handles DELETE requests: it deletes an image file from the media directory and removes its database record."""
        logger.info(f'DELETE {self.client_address[0]}:{self.path}')
        if self.path.startswith('/api/images/'):
            name = self.path.split('/')[-1]
            name, file_type = name.rsplit('.', 1)
            self.delete_image(name, file_type)
            # delete from db

    def get_images_names(self, *args, **kwargs):
        """Return uploaded image filenames as a JSON response."""
        self.json_response({
            'images': self.db.get_images_names()}) # get names from db

    def get_images(self, page: int):
        """Returns paginated image metadata as JSON to be used by the frontend to render the image list."""
        images = self.db.get_images(page)
        has_next = self.db.has_next(page)
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
            'images': res_images,
            'has_next': has_next
        })

    def delete_image(self, name: str, file_type: str):
        """Deletes an image from the database and from the media directory."""
        try:
            self.db.delete_image(name)
            (MEDIA_PATH / (name + '.' + file_type)).unlink()
            logger.info(f'Image {name} deleted successfully')
            self.json_response({'message': 'Image deleted'}, status_code=200)
        except FileNotFoundError:
            logger.info(f'File {name} not found (on delete)')
            self.json_response({'message': 'Image not found'}, status_code=404)
        except DatabaseError:
            logger.info(f' {name} not found in database (on delete)')
            self.json_response({'message': 'Image not found'}, status_code=404)
