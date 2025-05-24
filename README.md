# Energy App Backend

Backend API for an application to perform photovoltaic system dimensioning using AI.

## Setup

1.  **Prerequisites:**

    - Python 3.x
    - PostgreSQL
    - Poetry (or pip)

2.  **Clone the repository:**

    ```bash
    git clone https://github.com/asbilim/energy-app-backend.git
    cd energy-app-backend
    ```

3.  **Environment Variables:**
    Create a `.env` file in the project root and add the following variables:

    ```
    SECRET_KEY='your_django_secret_key'
    DEBUG=True
    DB_NAME='your_db_name'
    DB_USER='your_db_user'
    DB_PASSWORD='your_db_password'
    DB_HOST='localhost'
    DB_PORT='5432'
    OPENROUTER_APIKEY='your_openrouter_api_key'
    AI_MODEL='your_preferred_ai_model (e.g., deepseek/deepseek-chat-v3-0324:free)'
    ```

4.  **Install dependencies:**
    Using Poetry:

    ```bash
    poetry install
    ```

    Or using pip:

    ```bash
    pip install -r requirements.txt
    ```

    (Note: You may need to generate a `requirements.txt` file from `pyproject.toml` if one isn't present: `poetry export -f requirements.txt --output requirements.txt --without-hashes`)

5.  **Apply migrations:**

    ```bash
    python manage.py migrate
    ```

6.  \*\*Create a superuser (optional, for admin access):

    ```bash
    python manage.py createsuperuser
    ```

7.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```

## API Documentation

Once the server is running, API documentation is available via Swagger UI and Redoc:

- Swagger: `http://127.0.0.1:8000/api/docs/`
- Redoc: `http://127.0.0.1:8000/api/redoc/`

## Running Tests

To run the test suite:

```bash
python manage.py test
```
