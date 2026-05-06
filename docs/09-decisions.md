# 技术决策

## 2026-05-06 - 使用 FastAPI 与分层后端结构

### 背景

项目需要为英语学习前端提供认证、词典、翻译、单词详情和生词本等 HTTP API，同时保持后续扩展 AI 会话和复习能力的空间。

### 决策

使用 FastAPI 作为 Web 框架，并按 route、service、repository、model、schema、client 和 core 基础设施分层组织代码。

### 影响

该结构使 HTTP 协议、业务编排、数据库访问和外部 provider 调用边界清晰。后续新增功能应优先沿用现有分层，而不是把业务逻辑直接写入 route。

## 2026-05-06 - 使用 Alembic 管理数据库 schema

### 背景

项目使用 PostgreSQL 和 SQLModel，需要可控地演进用户、词典、生词本、复习记录和 AI 会话等表结构。

### 决策

默认关闭 `APP_AUTO_CREATE_TABLES`，使用 Alembic 迁移管理 schema。自动建表仅适合本地调试。

### 影响

开发者在修改模型后需要创建并运行迁移。生产和常规开发流程不应依赖应用启动时自动建表。
