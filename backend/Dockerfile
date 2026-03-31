FROM python:3.12-slim

WORKDIR /app

# Copy backend code
COPY backend/app ./app
COPY backend/pyproject.toml .

# Copy harnesses and domains (needed at runtime)
COPY harnesses ./harnesses
COPY domains ./domains

# Install dependencies
RUN pip install --no-cache-dir fastapi uvicorn anthropic sqlalchemy aiosqlite python-jose passlib bcrypt pydantic pydantic-settings pyyaml python-multipart sse-starlette httpx

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
