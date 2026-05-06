# 排障

## 常见问题

- 启动时报缺少 `APP_SECRET_KEY` 或 `DATABASE_URL`：检查 `.env` 或进程环境变量，这两个变量在 `Settings` 校验中为必填。
- 翻译接口返回 `youdao credentials are not configured`：检查 `YOUDAO_APP_KEY` 和 `YOUDAO_APP_SECRET`。
- provider 返回 `502`：检查外部网络、有道或 dictionaryapi.dev 响应、日志中的 provider、reason、status_code 和 duration_ms。
- CORS 请求失败：确认 `APP_ENV`，开发环境读取 `APP_CORS_DEV_ALLOW_ORIGINS`，生产环境读取 `APP_CORS_PROD_ALLOW_ORIGINS`。
- 测试导入 `app.main` 失败：确认测试进程能读取有效 `.env` 或已设置必填环境变量。

## 调试检查清单

- 先请求 `GET /healthz` 确认应用存活。
- 检查 `.env` 是否存在且未把示例值用于生产。
- 检查数据库迁移是否执行：`uv run alembic upgrade head`。
- 检查当前 token 是否包含 `sub` 和 `type="access"`。
- 检查用户 `status` 是否为 `active`。

## 日志与诊断

- 使用 `APP_LOG_LEVEL` 控制日志级别。
- 使用 `APP_LOG_JSON=true` 输出 JSON 日志。
- 使用 `APP_LOG_ACCESS_ENABLED` 控制访问日志相关行为。
- provider client 会记录请求耗时和失败原因。

## 恢复步骤

- provider 临时不可用时，可以重试请求或改为使用已缓存的单词详情。
- 数据库 schema 不匹配时，优先检查 Alembic 当前版本并执行迁移。
- 配置错误时先修正环境变量，再重启服务。

## 待确认问题

- TODO: 需要补充生产日志采集、告警和数据库恢复流程。
