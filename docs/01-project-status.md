# 项目状态

## 当前阶段

当前项目处于后端 MVP / 早期功能完善阶段。认证、词典、翻译、单词详情缓存和生词本核心 API 已实现；AI 会话与复习记录存在数据模型，但当前代码未暴露对应 API。

## 当前版本

当前包版本为 `0.1.0`，来源于 `pyproject.toml`。

## 当前开发重点

- 维护现有 FastAPI 后端 API 的稳定性。
- 使用 Alembic 管理 PostgreSQL schema，而不是依赖自动建表。
- 为后续复习、AI 教师聊天或更完整的词典数据能力保留模型基础。

## 已完成关键能力

- [用户认证](features/implemented/2026-05-06-auth-api.md)。
- [词典查询](features/implemented/2026-05-06-dictionary-api.md)。
- [翻译](features/implemented/2026-05-06-translation-api.md)。
- [单词详情聚合与缓存](features/implemented/2026-05-06-word-detail-api.md)。
- [用户生词本](features/implemented/2026-05-06-vocabulary-api.md)。

## 开发中功能

当前没有已确认处于开发中的功能文档。

## 计划中功能

- [AI 教师会话 API](features/planned/2026-05-06-ai-teacher-session-api.md)。
- [复习记录 API](features/planned/2026-05-06-review-api.md)。

## 风险与阻塞

- 部分测试需要可用的 `DATABASE_URL` 和已迁移的 PostgreSQL 数据库。
- 翻译与单词详情聚合依赖有道凭证 `YOUDAO_APP_KEY` / `YOUDAO_APP_SECRET`。
- 部署脚本依赖远端主机别名、远端路径和远端 `docker compose` 配置，仓库中未包含 compose 文件。
- `tests/test_pg_connection.py` 在模块导入时会直接建表并写入示例数据，不是标准 pytest 隔离测试。

## 下一次会话建议阅读

- `docs/00-overview.md`
- `docs/02-architecture.md`
- `docs/03-development-workflow.md`
- `docs/05-testing.md`
- `docs/06-api-design.md`
- 具体任务相关的 `docs/features/` 文档。
