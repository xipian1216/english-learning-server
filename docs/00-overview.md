# 项目概览

## 目的

`english-learning-server` 是英语学习产品的主后端服务，负责用户、认证、非 AI 学习业务数据，以及未来对 `english-learning-agents` 的接入编排。

## 主要能力方向

- 注册登录与第三方认证。
- 非 AI 学习功能，例如词典、翻译、单词详情、用户词本和复习数据。
- AI agents 调用边界，例如请求编排、鉴权、限流、错误映射和结果返回。

## 当前状态

项目正在准备重写后端 `app/` 代码。旧 `app/` 和旧 docs 已被删除，因此当前文档以重写目标和后续计划为准。

## 高层技术栈

- FastAPI
- PostgreSQL
- SQLAlchemy 2 async
- Alembic
- Pydantic / pydantic-settings
- pytest
- FastAPI Users 作为认证基础设施默认方向

## 重要入口

- 应用入口：`main.py`
- 开发指南：[`../DEVELOPMENT_GUIDE.md`](../DEVELOPMENT_GUIDE.md)
- 项目配置：[`../pyproject.toml`](../pyproject.toml)
- Alembic 配置：[`../alembic.ini`](../alembic.ini)

## 待确认问题

- Server 重写后的第一批代码结构尚未实现。
- 认证、非 AI 功能、AI agents 接入都需要单独 feature plan。
- 是否保留旧数据库数据，需要在具体功能计划中确认。
