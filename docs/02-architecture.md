# 架构

## 高层摘要

项目是单体 FastAPI 后端服务。HTTP 请求进入 `app.main` 创建的 FastAPI 应用，经请求日志中间件、CORS、异常处理器和 `/api/v1` 路由后进入 route 层。route 层负责依赖注入和响应模型，业务逻辑主要在 service 层，数据库访问主要在 repository 层，外部服务访问集中在 client 层。

## 主要模块

- `app/api/v1/routes/`：HTTP API 入口，包含认证、词典、翻译、单词详情和生词本路由。
- `app/api/deps.py`：认证依赖，解析 Bearer token 并加载当前用户。
- `app/services/`：业务编排层，处理注册登录、词典查询转换、翻译、单词详情聚合和生词本操作。
- `app/repositories/`：数据库访问层，封装用户、词典缓存、生词本、复习记录和 AI 会话相关查询。
- `app/db/models/`：SQLModel 数据模型。
- `app/schemas/`：Pydantic 请求和响应 schema。
- `app/clients/`：外部 HTTP 客户端，包括 `dictionaryapi.dev` 和有道智云；OpenAI 客户端目前是占位文件。
- `app/core/`：配置、安全、异常和日志基础设施。
- `alembic/`：数据库迁移配置和版本脚本。
- `tests/`：API、配置、服务工具函数和数据库连接测试。

## 数据流

- 认证请求：route 接收注册或登录请求，service 校验用户状态并使用 repository 读写 `users`，通过 `app/core/security.py` 生成 JWT。
- 受保护请求：`get_current_user` 从 Bearer token 解析 `sub`，加载用户并检查 `status == "active"`。
- 词典查询：route 调用 `lookup_word`，service 调用 `dictionary_api_client` 请求 `dictionaryapi.dev` 并映射为响应 schema。
- 翻译：route 调用 `translate_text`，service 校验有道配置，client 使用有道 v3 签名发起请求。
- 单词详情：先按 normalized text 查询本地 `dictionary_entries` 缓存；未命中时请求词典和翻译，将首个词典 entry 聚合为单词详情并写入缓存。
- 生词本：受保护 route 以当前用户为边界读写 `user_vocabulary_items`；若词典缓存不存在，会先触发单词详情构建。

## 运行时流程

- 启动时 `get_settings()` 读取 `.env` 和环境变量；缺少 `APP_SECRET_KEY` 或 `DATABASE_URL` 会失败。
- `setup_logging()` 配置根 logger、app logger 和 uvicorn logger。
- FastAPI lifespan 记录启动信息；仅当 `APP_AUTO_CREATE_TABLES=true` 时调用 `create_db_and_tables()`。
- 默认通过 Alembic 初始化和演进数据库 schema。

## 外部集成

- `dictionaryapi.dev`：默认 `APP_DICTIONARY_API_BASE_URL=https://api.dictionaryapi.dev/api/v2/entries/en`。
- 有道智云：`YOUDAO_API_BASE_URL` 默认为 `https://openapi.youdao.com/api`，需要 `YOUDAO_APP_KEY` 和 `YOUDAO_APP_SECRET`。
- OpenAI：依赖已在 `pyproject.toml` 中声明，客户端文件为占位，当前无实际集成逻辑。

## 重要边界

- route 层不直接拼装复杂业务结果，优先委托 service。
- service 层不直接暴露外部 provider 原始错误给调用方，统一转为 `AppError`。
- API 响应统一使用 `APIResponse`：`code`、`message`、`data`。
- 用户生词本数据必须通过当前用户隔离。
- 密钥、数据库地址和第三方凭证必须来自环境变量，不写入代码或文档。

## 风险与约束

- `Settings` 在导入 `app.main` 时会初始化，测试环境也需要设置必要环境变量或 `.env`。
- 单词详情未命中缓存时依赖两个外部 provider，可用性和延迟受外部服务影响。
- 当前缓存只持久化 entry、sense 和 example，collocations 在聚合响应中仍为空。
