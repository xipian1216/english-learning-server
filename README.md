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
- `APP_CORS_DEV_ALLOW_ORIGINS`: comma-separated dev origins
- `APP_CORS_PROD_ALLOW_ORIGINS`: comma-separated production origins
- `APP_DICTIONARY_API_BASE_URL`: dictionaryapi.dev base URL
- `APP_ACCESS_TOKEN_EXPIRE_MINUTES`: access token expiration time in minutes
- `YOUDAO_APP_KEY` / `YOUDAO_APP_SECRET`: Youdao provider credentials

### Run The App

```bash
uv run fastapi dev main.py
```

If `APP_SECRET_KEY` or `DATABASE_URL` is missing, the app now fails fast during startup.

### CORS Configuration

The backend now separates development and production CORS origins by environment:

- when `APP_ENV=development`, it uses `APP_CORS_DEV_ALLOW_ORIGINS`
- when `APP_ENV=production`, it uses `APP_CORS_PROD_ALLOW_ORIGINS`

Example:

```env
APP_ENV=development
APP_CORS_DEV_ALLOW_ORIGINS=http://localhost:5173
APP_CORS_PROD_ALLOW_ORIGINS=https://your-frontend-domain.com
```

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
- `POST /api/v1/users/password-reset-requests`: reserved password reset request API; returns `501` until reset delivery is configured
- `POST /api/v1/users/password-resets`: reserved password reset submit API; returns `501` until reset delivery is configured
- `GET /api/v1/auth/oidc/authentik/login`: reserved Authentik OIDC login API; returns `503` until provider configuration is implemented
- `GET /api/v1/auth/oidc/authentik/callback`: reserved Authentik OIDC callback API; returns `503` until provider configuration is implemented
- `POST /api/v1/auth/oidc/authentik/sessions`: reserved Authentik login-code exchange API; returns `503` until provider configuration is implemented

### Dictionary API

- `GET /api/v1/dictionary/entries/{word}`: query word definitions from `dictionaryapi.dev`

### Translation API

- `POST /api/v1/translations`: translate text with Youdao Cloud

### Word Detail API

- `POST /api/v1/word-details`: authenticated lookup that returns `word_detail`, `lookup_status`, and `cache_status`, reusing cached dictionary entries when available

### Vocabulary API

- `GET /api/v1/vocabulary-items`: list current user's vocabulary items
- `POST /api/v1/vocabulary-items`: add a word to current user's vocabulary book, automatically lookup dictionary/translation detail, cache successful results, and return `item`, `word_detail`, and `lookup_status`
- `PATCH /api/v1/vocabulary-items/{item_id}`: update status, note, or familiarity score
- `DELETE /api/v1/vocabulary-items/{item_id}`: remove a word from current user's vocabulary book
