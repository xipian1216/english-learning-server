# 架构

## 高层摘要

`english-learning-server` 是主业务后端。目标架构采用清晰分层：

```text
api -> services -> repositories -> models -> database
          |
          v
     integrations
```

## 目标分层

- `api`
  - FastAPI 路由、依赖注入、请求响应边界。

- `schemas`
  - API 请求、响应和公共响应结构。

- `models`
  - SQLAlchemy 数据库模型。

- `repositories`
  - 数据库读写封装。

- `services`
  - 业务流程和用例编排。

- `integrations`
  - OIDC、词典、翻译、agents 等外部服务客户端。

- `core`
  - 配置、错误、日志、安全和基础依赖。

## 主要业务边界

### 用户与认证

负责本地用户、邮箱密码登录、第三方 OAuth/OIDC 登录、用户状态、鉴权和用户数据隔离。

### 非 AI 学习功能

负责词典、翻译、单词详情、用户词本、复习记录等不依赖 agents 内部实现的业务。

### AI Agents 接入

server 只负责调用和保护 agents 能力，不实现 prompt、模型调用、评测或 agent 内部工具逻辑。

## 外部依赖

- PostgreSQL
- OIDC/OAuth provider
- dictionaryapi.dev
- Youdao Cloud
- `english-learning-agents`

## 约束

- 所有业务 API 默认使用 `/api/v1`。
- 响应统一 `{ code, message, data }`。
- 数据库结构变化必须通过 Alembic migration。
- 第三方服务必须可 mock。
