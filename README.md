# Image Hosting Server

A simple image hosting web application built with Python, Nginx, PostgreSQL, and Docker.
This is a study project for practicing Python, Docker, HTTP, PostgreSQL, and SQL.  
The technical requirements are described in `python-1-docker.md` and `python-2-sql.md`.
https://www.figma.com/design/ivhGgfIBMDsA2xF3qospb6/image-hosting?node-id=0-1&p=f was used as a website layout. 
Several modifications were made to meet the project requirements.


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
- Uploaded images are stored in the local `images/` directory mounted into the Docker container.
- Images are served through Nginx
- Image metadata is stored in PostgreSQL
- Uploaded images can be displayed on the images page
- Images page supports pagination
- Image list displays:
  - generated filename with the integrated link
  - original filename
  - file size in KB
  - upload date and time
  - file type
- Images can be deleted from storage and database
- Application actions are logged to `logs/*.log`
- PostgreSQL database backups are created automatically using a Python script and the `schedule` library by running `pg_dump` inside the PostgreSQL Docker container
- Backup files are stored in the local `backups/` directory


## Technologies

- Python 3.13
- PostgreSQL
- psycopg3
- Pillow
- Nginx
- Docker
- Docker Compose
- uv
- schedule
- python-dotenv

## Project Structure

```text
project/
├── app/
│   ├── __init__.py
│   ├── backup.py
│   ├── base_handler.py
│   ├── db_manager.py
│   ├── image_hosting_handler.py
│   ├── QUERIES.py
│   └── settings.py
├── backups/
│   └── .gitkeep
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
python main.py
```

then the backend is available at:

```text
http://localhost:8000
```
## Main Routes

| Method | Route | Description                                                                 |
| ------ | ----- |-----------------------------------------------------------------------------|
| `GET` | `/` | Displays the main page                                                      |
| `GET` | `/upload` | Displays the image upload page                                              |
| `GET` | `/images` | Displays the uploaded images page                                           |
| `POST` | `/api/upload` | Uploads an image, validates it, saves it, and stores metadata in PostgreSQL |
| `GET` | `/api/images` | Returns a list of uploaded image names                                      |
| `GET` | `/api/images-data` | Returns paginated image metadata from PostgreSQL                            |
| `DELETE` | `/api/images/<filename>` | Deletes an image from storage and database                                  |
| `GET` | `/images/<filename>` | Serves uploaded images through Nginx                                        |

## API Examples

### Upload Image

`POST /api/upload`

The backend checks the file extension, file size, and validates that the uploaded file is a real image.

Example response:

```json
{
  "message": "File uploaded successfully",
  "filename": {
    "filename": "a1b2c3d4",
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
      "filename": "a1b2c3d4",
      "original_name": "photo.png",
      "size": 245,
      "upload_time": "2025-01-24 15:30:00",
      "file_type": "png"
    }
  ],
  "has_next": true
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


## Local and Docker Volumes

The project uses Docker volumes for persistent data:

- `images` — stores uploaded images
- `logs` — stores application logs
- `backups/` — local project directory for database backups
- `db_data` — Docker volume for PostgreSQL data

This means images, logs, and database data are saved between container restarts.

## Database Backup

The project supports automatic PostgreSQL backups every day at 02:00 using `pg_dump`.

The backup script is located at:

```text
app/backup.py
```

## Stopping the Project

To stop the containers, run:

```bash
docker compose down


To stop the containers and remove volumes:

```bash
docker compose down -v
```

Be careful: docker compose down -v removes the PostgreSQL Docker volume.
Uploaded images, logs, and backups are stored in local project folders and are not removed unless deleted manually.