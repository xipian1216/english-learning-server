# 当前版本

## 版本号 / 版本代号

`0.1.0`

## 版本目标

提供英语学习应用后端 MVP 能力，包括认证、查词、翻译、单词详情缓存和用户生词本。

## 已纳入功能

- [用户认证](../features/implemented/2026-05-06-auth-api.md)
- [词典查询](../features/implemented/2026-05-06-dictionary-api.md)
- [翻译](../features/implemented/2026-05-06-translation-api.md)
- [单词详情聚合与缓存](../features/implemented/2026-05-06-word-detail-api.md)
- [用户生词本](../features/implemented/2026-05-06-vocabulary-api.md)

## 开发中功能

当前没有已确认处于开发中的功能。

## 计划纳入功能

- [AI 教师会话 API](../features/planned/2026-05-06-ai-teacher-session-api.md)
- [复习记录 API](../features/planned/2026-05-06-review-api.md)

## 已知问题

- 部分测试需要真实 PostgreSQL 数据库和已迁移 schema。
- `tests/test_pg_connection.py` 在导入时会写入测试数据，不适合作为长期自动化测试模式。
- 部署脚本依赖远端 Docker Compose 配置，但仓库中未包含 compose 文件。
- OpenAI 客户端为占位，AI 会话数据模型尚未暴露 API。

## 发布前检查

- `uv run pytest`
- `uv run alembic upgrade head`
- 验证 `.env` 中 `DATABASE_URL`、`APP_SECRET_KEY`、CORS 和 provider 凭证。
- 验证 `GET /healthz`。
- TODO: 补充生产部署 smoke test 和回滚检查。

## 相关功能文档

- `docs/features/README.md`
- `docs/06-api-design.md`
- `docs/07-deployment.md`
