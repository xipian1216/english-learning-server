# API 设计

## API 范围

所有业务 API 当前挂载在 `/api/v1` 下。健康检查 `GET /healthz` 不在版本前缀下。

## 请求约定

- JSON 请求体使用 Pydantic schema 校验。
- 受保护接口使用 `Authorization: Bearer <access_token>`。
- OAuth2 token URL 配置为 `/api/v1/sessions`。
- CORS 来源根据 `APP_ENV` 区分 development 和 production。

## 响应约定

成功业务响应统一为：

```json
{
  "code": 0,
  "message": "ok",
  "data": {}
}
```

删除生词本条目成功时返回 HTTP `204`，无 `APIResponse` body。

## 错误处理

- 业务错误由 `AppError` 映射为对应 HTTP 状态码和 `code`。
- 请求校验错误返回 HTTP `422`，响应包含 `data.errors`。
- 未处理异常返回 HTTP `500`、业务 code `50000`。
- provider 失败通常映射为 HTTP `502`。

## 鉴权与授权

- 注册和登录不需要 token。
- `GET /users/me`、修改密码、单词详情和生词本接口需要 Bearer token。
- JWT payload 需要 `sub` 和 `type="access"`。
- 当前用户必须存在且 `status == "active"`。

## 当前端点

- `GET /healthz`：健康检查。
- `POST /api/v1/users`：注册并返回 access token。
- `POST /api/v1/sessions`：登录并返回 access token。
- `GET /api/v1/users/me`：获取当前用户资料。
- `PATCH /api/v1/users/me/password`：修改当前用户密码。
- `GET /api/v1/dictionary/entries/{word}`：查询英文词典。
- `POST /api/v1/translations`：调用有道翻译。
- `POST /api/v1/word-details`：聚合单词详情，需认证。
- `GET /api/v1/vocabulary-items`：列出当前用户生词。
- `POST /api/v1/vocabulary-items`：添加生词。
- `PATCH /api/v1/vocabulary-items/{item_id}`：更新生词状态、笔记、熟悉度或下次复习时间。
- `DELETE /api/v1/vocabulary-items/{item_id}`：删除生词。

## 版本与兼容性

- 当前 API 前缀为 `/api/v1`。
- Schema 演进规则尚未正式定义。

## 待确认问题

- TODO: 是否需要 OpenAPI 文档导出、错误码表和 API 兼容性策略。
