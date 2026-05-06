# 编码规范

## 语言和框架约定

- 使用 Python 3.12 类型标注风格，例如 `str | None` 和 `list[str]`。
- FastAPI route 使用 `response_model=APIResponse[...]`。
- 请求和响应数据结构放在 `app/schemas/`。
- 数据表模型使用 SQLModel，放在 `app/db/models/`。
- 配置通过 `pydantic-settings` 和环境变量读取，不硬编码环境相关值。

## 文件组织

- HTTP route：`app/api/v1/routes/`。
- 业务逻辑：`app/services/`。
- 数据访问：`app/repositories/`。
- 外部服务调用：`app/clients/`。
- 数据库模型：`app/db/models/`。
- 共享基础设施：`app/core/`。
- 测试：`tests/`，按能力命名为 `test_*_api.py` 或具体模块测试。

## 命名规则

- API route 函数使用动作语义，例如 `register_user`、`create_translation`、`get_vocabulary_items`。
- service 函数使用业务语义，例如 `translate_text`、`build_word_detail`、`create_vocabulary_item`。
- 数据库表使用复数 snake_case，例如 `users`、`dictionary_entries`、`user_vocabulary_items`。
- 环境变量使用 `APP_` 前缀；第三方 provider 凭证使用 provider 前缀，例如 `YOUDAO_`。

## 错误处理

- 业务错误抛出 `AppError(status_code, code, message)`。
- `app.main` 将 `AppError` 统一转换为 `{"code": ..., "message": ..., "data": null}`。
- FastAPI 请求校验错误统一返回 `422`，业务 code 为 `40001`，并在 `data.errors` 中携带字段错误列表。
- 未处理异常统一返回 `50000` 和 `internal server error`。

## 日志

- 使用 `app.core.logging.get_logger()` 获取 logger。
- provider 请求应记录 provider、耗时、失败原因或状态码。
- 认证依赖会将 `user_id` 绑定到请求上下文。
- 日志配置支持文本或 JSON 格式，由 `APP_LOG_JSON` 控制。

## 依赖规则

- 不新增依赖，除非有明确需求和理由。
- 外部 HTTP 调用当前使用标准库 `urllib.request`。
- 密码哈希使用 `passlib` 的 `pbkdf2_sha256`。
- JWT 使用 `pyjwt`。

## 待确认问题

- TODO: 仓库中尚未定义 formatter、linter 或静态类型检查工具。
