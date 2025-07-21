# AICMS

AI-powered Content Management System

## PostgreSQL Setup with Docker Compose

This project now uses PostgreSQL instead of SQLite to avoid "database is locked" errors that can occur with SQLite when multiple processes (like Django Q workers) try to access the database simultaneously.

### Prerequisites

- Docker and Docker Compose installed on your system
- Python 3.13 or higher

### Setup Instructions

1. **Start the PostgreSQL database**:

   ```bash
   docker compose up -d
   ```

   This will start a PostgreSQL database in a Docker container.

2. **Install dependencies**:

   ```bash
   uv sync
   ```

   This will install all required dependencies, including the newly added `psycopg2-binary` for PostgreSQL support.

3. **Run migrations**:

   ```bash
   python manage.py migrate
   ```

   This will create all necessary database tables in PostgreSQL.

4. **Create a superuser**:

   ```bash
   python manage.py createsuperuser
   ```

5. **Run the development server**:

   ```bash
   python manage.py runserver
   ```

### Environment Variables

The project now uses environment variables for configuration. These are stored in a `.env` file in the project root. The following variables are available:

- `DEBUG`: Set to `True` for development, `False` for production
- `SECRET_KEY`: Django secret key
- `DATABASE_URL`: PostgreSQL connection URL
- `AI_BASE_URL`: URL for the AI API
- `AI_API_KEY`: API key for the AI service
- `AI_API_MODEL`: Model name for the AI service

### Troubleshooting

- If you encounter connection issues, make sure the PostgreSQL container is running:
  ```bash
  docker compose ps
  ```

- To view PostgreSQL logs:
  ```bash
  docker compose logs postgres
  ```

- To reset the database:
  ```bash
  docker compose down -v
  docker compose up -d
  python manage.py migrate
  ```