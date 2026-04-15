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
- `APP_DICTIONARY_API_BASE_URL`: dictionaryapi.dev base URL
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
