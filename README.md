# Image Hosting Server

A simple image hosting web application built with Python, Nginx, PostgreSQL, and Docker.

The application allows users to upload images, stores image metadata in a PostgreSQL database, and serves uploaded images through Nginx.

## Features

- Upload images through a web page
- Supported formats:
  - `.jpg`
  - `.jpeg`
  - `.png`
  - `.gif`
- Maximum file size: 5 MB
- Validation of uploaded files using Pillow
- Automatic generation of unique filenames
- Uploaded images are stored in a Docker volume
- Images are served through Nginx
- Image metadata is stored in PostgreSQL
- Uploaded images can be displayed on the images page
- Images can be deleted from storage and database
- Application actions are logged to `app.log`

## Not Implemented Yet

The following features are planned but not finished yet:

- Pagination for the images list
- Database backup script

## Technologies

- Python 3.13
- PostgreSQL
- psycopg3
- Pillow
- Nginx
- Docker
- Docker Compose

## Project Structure

```text
project/
├── app/
│   ├── __init__.py
│   ├── base_handler.py
│   ├── db_manager.py
│   ├── image_hosting_handler.py
│   ├── QUERIES.py
│   └── settings.py
├── images/
│   └── .gitkeep
├── logs/
│   └── .gitkeep
├── static/
│   └── image-uploader/
│       ├── css/
│       ├── img/
│       ├── js/
│       │   ├── images.js
│       │   ├── index.js
│       │   └── upload.js
│       ├── images.html
│       ├── index.html
│       └── upload.html
├── .dockerignore
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── Dockerfile-poetry
├── main.py
├── nginx.conf
├── pyproject.toml
├── README.md
├── requirements.txt
└── uv.lock
```

## Running the Project

Make sure Docker and Docker Compose are installed.

Start the full project with:

```bash
docker compose up --build
```

After startup, the application is available through Nginx at:

```text
http://localhost:8080
```
## Image Access

Uploaded images are served by Nginx at:

```text
http://localhost:8080/images/<filename>
```

## Local Backend Development

If you run only the Python backend without Docker and Nginx:

```bash
python app.py
```

then the backend is available at:

```text
http://localhost:8000
```
## Main Routes

| Method | Route | Description |
| ------ | ----- | ----------- |
| `GET` | `/` | Displays the main page |
| `GET` | `/upload` | Displays the image upload page |
| `GET` | `/images` | Displays the uploaded images page |
| `POST` | `/api/upload` | Uploads an image, validates it, saves it, and stores metadata in PostgreSQL |
| `GET` | `/api/images` | Returns a list of uploaded image names |
| `GET` | `/api/images-data` | Returns full image metadata from PostgreSQL |
| `DELETE` | `/api/images/<filename>` | Deletes an image from storage and database |
| `GET` | `/images/<filename>` | Serves uploaded images through Nginx |

## API Examples

### Upload Image

`POST /api/upload`

The backend checks the file extension, file size, and validates that the uploaded file is a real image.

Example response:

```json
{
  "message": "File uploaded successfully",
  "filename": {
    "filename": "a1b2c3d4.png",
    "original_name": "photo.png",
    "size": 245,
    "file_type": "png"
  }
}
```

### Get Image Metadata

`GET /api/images-data`

Example response:

```json
{
  "images": [
    {
      "id": 1,
      "filename": "a1b2c3d4.png",
      "original_name": "photo.png",
      "size": 245,
      "upload_time": "2025-01-24 15:30:00",
      "file_type": "png"
    }
  ]
}
```


## Database

The project uses PostgreSQL to store image metadata.

Main table:

```sql
CREATE TABLE images (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    original_name TEXT NOT NULL,
    size INTEGER NOT NULL,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_type TEXT NOT NULL
);
```

Stored metadata:

- generated filename
- original filename
- file size
- upload date and time
- file type

## Logs

Application and server logs are stored in the `logs/` directory.

Log messages include information about requests, successful uploads, validation errors, and image deletion.


## Volumes

The project uses Docker volumes for persistent data:

- `images` — stores uploaded images
- `logs` — stores application logs
- database volume — stores PostgreSQL data

This means images, logs, and database data are saved between container restarts.


## Stopping the Project

To stop the containers, run:

```bash
docker compose down
```

To stop the containers and remove volumes:

```bash
docker compose down -v
```

Be careful: removing volumes deletes uploaded images, logs, and database data.