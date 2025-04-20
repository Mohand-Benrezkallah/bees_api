# Bee API

A GraphQL API for tracking bee information built with Python, FastAPI, Strawberry GraphQL, SQLAlchemy, and PostgreSQL.

## Technology Stack

* Python 3.12+
* FastAPI & Strawberry GraphQL
* SQLAlchemy with PostgreSQL
* Alembic for migrations
* JWT authentication
* Docker & Docker Compose

## Project Structure

* `app/`: Core application code
  * `main.py`: FastAPI application
  * `schema.py`: GraphQL schema
  * `models.py`: Database models
  * `crud.py`: Database operations
  * `core/`: Configuration and security
  * `images/`: Uploaded bee images
* `alembic/`: Database migrations
* `tests/`: Unit and integration tests

## Database Schema

The main database table is `bee`:

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `name` | VARCHAR | Bee name |
| `origin` | VARCHAR | Geographic origin |
| `image_path` | VARCHAR | Path to image (optional) |
| `species` | VARCHAR | Bee species |
| `captured_date` | DATE | Capture date |

## API Endpoints

* GraphQL endpoint: `/graphql`
* Authentication: JWT tokens via `Authorization: Bearer {token}` header

### Main Operations

* **Queries**:
  * `bees`: List all bees (authenticated)
  * `bee(id)`: Get bee by ID (authenticated)
  * `me`: Get current user info (authenticated)

* **Mutations**:
  * `register(username, email, password)`: Create new account
  * `login(username, password)`: Get authentication token
  * `add_bee(name, origin, species, captured_date, image)`: Add new bee with optional image upload
  * `delete_bee(id)`: Remove a bee record

## Setup and Running

1. Clone the repository
2. Copy `.env.example` to `.env` and configure variables
3. Run `docker-compose build && docker-compose up -d`
4. Apply migrations: `docker-compose exec app alembic upgrade head`
5. Access GraphQL interface at `http://localhost:8000/graphql`

## Image Handling

* Images can be uploaded via the `add_bee` GraphQL mutation using `multipart/form-data`
* Files are stored in the `app/images` directory
* The application is configured to serve images via `/images` endpoint
* Images are accessible at `http://localhost:8000/images/<filename>`