# 部署

## 当前状态

server 正处于重写准备阶段，部署方式需要在应用结构恢复后重新验证。

## 本地运行目标

README 中记录的历史运行方式：

```bash
uv run fastapi dev main.py
```

当前旧 `app/` 已删除，因此该命令需要在重写应用入口后重新验证。

## 配置

关键配置默认来自环境变量：

- `DATABASE_URL`
- `APP_SECRET_KEY`
- CORS 相关配置
- OIDC/OAuth provider 配置
- 词典、翻译和 agents 服务配置

真实密钥不得写入源码或文档。

## 数据库迁移

使用 Alembic 管理迁移。重写阶段如果决定重建干净 schema，必须在对应 feature plan 中明确。

## 待确认问题

- 是否继续使用现有 Dockerfile。
- 是否需要 Docker Compose 管理 server、database、agents。
- 生产环境 server 与 agents 的网络和鉴权方式。
