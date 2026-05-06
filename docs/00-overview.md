# 项目概览

## 目的

English Learning Server 是英语学习应用的后端服务，提供用户认证、词典查询、翻译、单词详情聚合和用户生词本能力。

## 主要能力

- 用户注册、登录、当前用户资料查询和密码修改。
- 基于 `dictionaryapi.dev` 的英文词典查询。
- 基于有道智云的文本翻译。
- 面向单词详情页的词典与翻译聚合，并将结果缓存到数据库。
- 当前用户生词本的列表、添加、更新和删除。
- 统一 API 响应、统一业务异常处理、请求日志和 CORS 配置。

## 目标用户 / 使用场景

- 面向英语学习前端应用，为学习者提供账户、生词、查词和翻译服务。
- 支持前端在阅读或查词场景中保存生词，并复用缓存的词典详情。

## 技术栈

- Python `>=3.12`。
- FastAPI。
- SQLModel / SQLAlchemy。
- PostgreSQL，使用 `psycopg` 驱动。
- Alembic 数据库迁移。
- Pydantic Settings 配置管理。
- PyJWT 与 Passlib `pbkdf2_sha256`。
- pytest 与 FastAPI TestClient。
- Docker 与 `uv`。

## 主要入口

- `main.py`：从 `app.main` 导出 FastAPI app，用于 `uv run fastapi dev main.py`。
- `app/main.py`：应用创建、生命周期、异常处理、日志中间件、CORS 和路由注册。
- `app/api/v1/router.py`：`/api/v1` 路由聚合入口。
- `app/core/config.py`：环境变量配置入口。
- `app/db/session.py`：数据库 engine、session 和自动建表函数。

## 快速开始

1. 复制环境变量模板：`cp .env.example .env`。
2. 配置至少 `DATABASE_URL` 和 `APP_SECRET_KEY`。
3. 安装依赖：`uv sync`。
4. 初始化或迁移数据库：`uv run alembic upgrade head`。
5. 启动开发服务：`uv run fastapi dev main.py`。

## 待确认问题

- TODO: 项目未在仓库中提供 `docker-compose.yml`，但部署脚本会在远端执行 `docker compose up --build -d`。
- TODO: `app/clients/openai_client.py` 目前是占位文件，AI 会话数据模型存在，但未暴露 API。
