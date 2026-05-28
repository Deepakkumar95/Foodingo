
# Foodingo Live

Production-inspired Swiggy/Zomato style food delivery platform.

## Features

- FastAPI Backend
- Real-time Order Tracking
- WebSocket Support
- Restaurant Listing
- Live Delivery Simulation
- Modern API Architecture

## Run Backend

```bash
pip install -r requirements_live.txt
DATABASE_URL=sqlite:///./foodingo.db uvicorn live_app:app --reload --host 0.0.0.0 --port 8000
```

### Optional: Redis for admin rate-limiting and audit

The project includes a Redis-backed rate limiter for admin routes with an in-process fallback. For production deployments (multi-worker), configure Redis and set the `REDIS_URL` environment variable.

Start a quick Redis instance with Docker:

```bash
docker run -d --name foodingo-redis -p 6379:6379 redis:7
```

Then run the app with:

```bash
REDIS_URL=redis://localhost:6379/0 DATABASE_URL=sqlite:///./foodingo.db uvicorn live_app:app --host 0.0.0.0 --port 8000
```

Install the runtime Redis dependency (already in `requirements_live.txt`):

```bash
pip install -r requirements_live.txt
```

If Redis is not available, the limiter falls back to an in-memory limiter (not multi-worker safe).

### Run with Docker Compose (recommended for local dev)

This compose file starts Redis and a Python container that runs the app. It mounts the repository into the container so code changes are reflected immediately.

```bash
docker compose up --build
```

Notes:
- The app container runs `pip install -r requirements_live.txt` at startup; this is convenient for dev but not ideal for production images. For production, build a dedicated image with pinned dependencies.
- The `REDIS_URL` is automatically set to `redis://redis:6379/0` for the app service.



> To use PostgreSQL instead of the default SQLite file, set `DATABASE_URL` to a PostgreSQL connection string, for example:
>
> ```bash
> DATABASE_URL=postgresql://user:password@localhost:5432/foodingo uvicorn live_app:app --reload --host 0.0.0.0 --port 8000
> ```

## Open Frontend

Open `frontend_demo.html` in a browser after the backend starts.

If your browser blocks direct access from `file://`, serve the folder with a simple local server:

```bash
python -m http.server 8080
```

Then visit:

http://127.0.0.1:8080/frontend_demo.html

## Authentication

A demo admin user is created on startup:

- username: `admin`
- password: `admin123`

Use the token endpoint:

```bash
curl -X POST "http://127.0.0.1:8000/token" -H "Content-Type: application/x-www-form-urlencoded" -d "username=admin&password=admin123"
```

Then use the bearer token for protected endpoints like `/users/me` and admin routes:

- `GET /admin/orders`
- `POST /admin/orders/{order_id}/status`

Example:

```bash
curl -H "Authorization: Bearer <ACCESS_TOKEN>" http://127.0.0.1:8000/admin/orders
```

## API Docs

http://127.0.0.1:8000/docs

## WebSocket Endpoint

ws://127.0.0.1:8000/ws/orders
