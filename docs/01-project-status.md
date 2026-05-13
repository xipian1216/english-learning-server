# 项目状态

## 当前阶段

后端重写准备阶段。

## 当前开发重点

1. 以 [`../DEVELOPMENT_GUIDE.md`](../DEVELOPMENT_GUIDE.md) 作为 server 重写长期指导。
2. 建立新的 `docs/` 文档体系。
3. 为注册登录、非 AI 功能、AI agents 接入分别编写 feature plan。
4. 继续补全重写后的业务 API、集成边界和测试基线。

## 已完成关键能力

- Server 总体开发指南：[`../DEVELOPMENT_GUIDE.md`](../DEVELOPMENT_GUIDE.md)
- Alembic 基础配置文件仍存在。
- README 中保留了旧 API 和运行方式参考，但不代表当前代码已可运行。
- 认证基础接口已实现：邮箱注册、邮箱登录、当前用户、修改密码、密码重置预留和 Authentik OIDC 预留接口。

## 开发中功能

- 非 AI 学习功能和 AI agents 接入仍处于计划或后续实现阶段。

## 计划中功能

- [`features/planned/2026-05-08-auth-foundation.md`](features/planned/2026-05-08-auth-foundation.md)
- [`features/planned/2026-05-08-non-ai-learning.md`](features/planned/2026-05-08-non-ai-learning.md)
- [`features/planned/2026-05-08-agents-integration-boundary.md`](features/planned/2026-05-08-agents-integration-boundary.md)

## 风险与阻塞

- 旧 `app/` 已删除，当前 server 不能按旧 README 的方式完整运行。
- 旧测试仍引用 `app.*`，重写后需要同步更新。
- `pyproject.toml` 仍包含旧实现依赖，例如 `sqlmodel`、`passlib`、`pyjwt`，重写时需要根据最终技术选型清理。
- Web 当前部分 API 调用路径可能与目标 `/api/v1` 不一致。

## 下一次会话建议阅读

- [`../DEVELOPMENT_GUIDE.md`](../DEVELOPMENT_GUIDE.md)
- [`02-architecture.md`](02-architecture.md)
- [`03-development-workflow.md`](03-development-workflow.md)
- 对应功能的 planned 文档
