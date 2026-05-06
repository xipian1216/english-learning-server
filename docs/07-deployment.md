# 部署

## 运行时要求

- Python 3.12。
- PostgreSQL。
- `uv`。
- Docker 镜像基于 `python:3.12-slim`。

## 环境变量

核心变量来自 `.env.example`：

- `APP_NAME`：应用名称。
- `APP_ENV`：`development` 或 `production`。
- `APP_DEBUG`：FastAPI debug 开关。
- `DATABASE_URL`：PostgreSQL 连接字符串，必填。
- `APP_DATABASE_ECHO`：SQL 输出开关。
- `APP_AUTO_CREATE_TABLES`：是否启动时自动建表，默认关闭。
- `APP_SECRET_KEY`：JWT 签名密钥，必填。
- `APP_JWT_ALGORITHM`：JWT 算法，默认 `HS256`。
- `APP_ACCESS_TOKEN_EXPIRE_MINUTES`：access token 过期分钟数。
- `APP_CORS_*`：CORS 配置。
- `APP_DICTIONARY_API_BASE_URL`：词典 provider 地址。
- `YOUDAO_APP_KEY` / `YOUDAO_APP_SECRET` / `YOUDAO_API_BASE_URL`：有道 provider 配置。

## 构建流程

- Docker 构建会复制整个仓库，执行 `uv sync --no-dev`。
- 容器默认暴露 `8000`。
- 容器启动命令为 `uv run uvicorn app.main:app --host 0.0.0.0 --port 8000`。

## 部署目标

- `deploy.sh` 默认远端为 `frp-pi:/home/pi/deploy/english-learning/english-learning-server`。
- `dev.sh` 默认远端为 `frp-pi:/home/pi/dev/english-learning-server`。
- 可通过 `REMOTE_NAME` 和 `REMOTE_PATH` 覆盖默认值。

## CI/CD

当前仓库未发现 `.github/` CI 配置。

## 回滚与恢复

- TODO: 仓库未记录回滚流程。
- TODO: 仓库未记录数据库备份、迁移回滚或恢复手册。

## 待确认问题

- TODO: 远端 `docker-compose.yml` 是否由其他仓库或服务器维护。
- TODO: 生产环境是否应在容器启动前执行 `alembic upgrade head`。
