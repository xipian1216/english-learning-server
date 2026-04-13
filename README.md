## English Learning Server

### Environment Variables

Copy `.env.example` to `.env` and adjust it as needed:

```bash
cp .env.example .env
```

Key variables:

- `DATABASE_URL`: PostgreSQL connection string
- `APP_AUTO_CREATE_TABLES`: auto-create tables on app startup
- `APP_DATABASE_ECHO`: print SQL statements for debugging
- `APP_SECRET_KEY`: JWT signing key
- `APP_ACCESS_TOKEN_EXPIRE_MINUTES`: access token expiration time in minutes

### Run The App

```bash
uv run fastapi dev main.py
```

### Initialize Database Tables

```bash
uv run python -m app.scripts.init_db
```

### Auth API

- `POST /api/v1/users`: register and receive an access token
- `POST /api/v1/sessions`: login and receive an access token
- `GET /api/v1/users/me`: get current user profile via Bearer token
- `PATCH /api/v1/users/me/password`: update current user password
