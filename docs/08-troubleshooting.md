# 排障

## 常见问题

### `ModuleNotFoundError: app`

当前旧 `app/` 已删除，server 处于重写准备阶段。需要先恢复新的应用结构，再运行旧测试或服务命令。

### README 与代码现状不一致

README 保留了旧 API 和旧运行方式，可能不代表当前可运行状态。以代码现状、`DEVELOPMENT_GUIDE.md` 和本 docs 为准。

### 数据库连接失败

检查：

- `DATABASE_URL` 是否存在。
- PostgreSQL 是否启动。
- Alembic migration 是否已执行。

### 外部服务测试失败

普通测试不应依赖真实外部服务。优先检查是否应该 mock OIDC、词典、翻译或 agents client。

## 调试检查清单

1. 确认当前分支和工作区状态。
2. 读取 `01-project-status.md`。
3. 确认任务是否已有 feature plan。
4. 运行最小相关测试。
5. 检查环境变量和依赖。
