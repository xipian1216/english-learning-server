## English Learning Server

### Environment Variables

Copy `.env.example` to `.env` and adjust it as needed:

```bash
cp .env.example .env
```

Key variables:

- `DATABASE_URL`: PostgreSQL connection string, required
- `APP_SECRET_KEY`: JWT signing key, required
- `APP_AUTO_CREATE_TABLES`: disabled by default; enable only for local debugging
- `APP_DATABASE_ECHO`: print SQL statements for debugging
- `APP_DICTIONARY_API_BASE_URL`: dictionaryapi.dev base URL
- `APP_ACCESS_TOKEN_EXPIRE_MINUTES`: access token expiration time in minutes
- `YOUDAO_APP_KEY` / `YOUDAO_APP_SECRET`: Youdao provider credentials

### Run The App

```bash
uv run fastapi dev main.py
```

If `APP_SECRET_KEY` or `DATABASE_URL` is missing, the app now fails fast during startup.

### Initialize Database Tables

```bash
uv run python -m app.scripts.init_db
```

`APP_AUTO_CREATE_TABLES` is disabled by default. For normal development and production flows, initialize and evolve schema through migrations instead of relying on automatic table creation.

### Database Migration

This repository now includes an Alembic skeleton configuration.

Recommended workflow:

```bash
alembic revision --autogenerate -m "describe your change"
alembic upgrade head
```

If you haven't installed Alembic yet in your local environment, install project dependencies first, then run the commands.

### Password Hashing

The project uses `pbkdf2_sha256` via `passlib` for password hashing.

### Auth API

- `POST /api/v1/users`: register and receive an access token
- `POST /api/v1/sessions`: login and receive an access token
- `GET /api/v1/users/me`: get current user profile via Bearer token
- `PATCH /api/v1/users/me/password`: update current user password

### Dictionary API

- `GET /api/v1/dictionary/entries/{word}`: query word definitions from `dictionaryapi.dev`

### Translation API

- `POST /api/v1/translations`: translate text with Youdao Cloud

### Word Detail API

- `POST /api/v1/word-details`: aggregate dictionary and translation data for word detail pages

### Vocabulary API

- `GET /api/v1/vocabulary-items`: list current user's vocabulary items
- `POST /api/v1/vocabulary-items`: add a word to current user's vocabulary book
- `PATCH /api/v1/vocabulary-items/{item_id}`: update status, note, or familiarity score
- `DELETE /api/v1/vocabulary-items/{item_id}`: remove a word from current user's vocabulary book
