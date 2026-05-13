# 编码规范

## 核心原则

- 先理解，再修改。
- 优先最小、聚焦的变更。
- 不做无关重构。
- 不硬编码密钥、令牌、环境地址。
- 保持代码、测试和文档一致。

## Python 与 FastAPI

- 路由层保持薄，只处理 HTTP 语义和依赖注入。
- 业务流程写在 service 层。
- 数据库读写写在 repository 层。
- 外部服务调用放在 integration 层。
- 请求响应结构使用 Pydantic schema。
- 错误通过统一异常和响应结构返回。

## 数据库

- 使用 SQLAlchemy 2 async 作为重写目标。
- 使用 Alembic 管理 schema 变化。
- 不依赖自动建表作为正常开发流程。
- 索引、唯一约束、外键、可空性必须在 feature plan 中说明。

## 配置

- 使用 pydantic-settings 读取环境变量。
- 缺少关键配置时应 fail fast。
- `.env.example` 应随配置变化同步更新。

## 第三方服务

- OIDC、词典、翻译、agents 调用都应封装为可替换 client。
- 测试中使用 mock 或 fake client。
- 日志不得输出 secret、token、密码或隐私敏感内容。
