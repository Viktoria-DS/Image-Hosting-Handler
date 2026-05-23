"""
PostgreSQL backup scheduler: this script creates PostgreSQL database backups using pg_dump.
Backups are saved to the local backups/ directory.
Run: uv run python app/backup.py
Important: the script must keep running for scheduled backups to work.
"""

import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import subprocess
import time
import schedule


PROJECT_DIR = Path(__file__).resolve().parent.parent
BACKUP_DIR = PROJECT_DIR / "backups"
load_dotenv(PROJECT_DIR / ".env")
CONTAINER_NAME = "postgres_container"
DB = {
    "user": os.getenv("POSTGRES_USER"),
    "dbname": os.getenv("POSTGRES_DB"),
}


def create_backup():
    if not DB["user"] or not DB["dbname"]:
        print("Backup failed: POSTGRES_USER or POSTGRES_DB is missing in .env")
        return

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup_file = BACKUP_DIR / f"backup_{timestamp}.sql"

    command = [
        "docker",
        "exec",
        "-t",
        CONTAINER_NAME,
        "pg_dump",
        "-U",
        DB["user"],
        DB["dbname"],
    ]

    with open(backup_file, "wb") as file:
        result = subprocess.run(
            command,
            stdout=file,
            stderr=subprocess.PIPE,
        )

    if result.returncode == 0:
        print(f"Backup created successfully: {backup_file}")
    else:
        print("Backup failed")
        print(result.stderr.decode("utf-8", errors="ignore"))

schedule.every().day.at("02:00").do(create_backup)

if __name__ == "__main__":
    print("Backup scheduler started. Backups will be created every day at 02:00")
    while True:
        schedule.run_pending()
        time.sleep(30)