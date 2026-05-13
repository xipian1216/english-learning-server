# 认证基础功能

## 状态

implemented

## 功能目标

建立 `english-learning-server` 的基础认证能力，为后续非 AI 学习功能和 AI agents 接入提供统一的用户身份、登录态和用户数据隔离基础。

首版需要支持：

- 邮箱密码注册。
- 邮箱密码登录。
- 获取当前用户。
- 修改当前用户密码。
- 密码重置 API 形状预留。
- OIDC/Authentik API 形状预留，但不接入真实 Authentik 配置。

## 非目标范围

- 不实现前端页面。
- 不兼容 `/v1` API 前缀。
- 不实现 refresh token。
- 不实现 cookie session。
- 不实现完整密码重置邮件或验证码发送链路。
- 不真实联调 Authentik、Google、GitHub 或其它第三方 provider。
- 不设计复杂角色权限系统。
- 不实现用户资料的复杂编辑流程；用户 profile 扩展留到后续功能。

## 关键决策

- API 前缀统一使用 `/api/v1`。
- 登录态首版只使用 access token。
- 认证基础设施默认采用 FastAPI Users。
- 对外业务 API 不直接暴露 FastAPI Users 默认路由，而是封装为项目自己的 API 契约。
- OIDC provider 首个预留名为 `authentik`，但当前 Authentik 未配置，因此首版只预留接口、配置和模型方向。
- 密码重置只预留接口，返回明确的未配置或未实现响应，后续单独计划邮件/验证码能力。

## API 设计

所有响应使用统一结构：

```json
{
  "code": 0,
  "message": "ok",
  "data": {}
}
```

### `POST /api/v1/users`

注册邮箱密码用户，并返回 access token。

请求字段：

- `email`
- `password`
- `display_name`

成功响应 `data`：

- `user`
- `access_token`
- `token_type`
- `expires_in`

关键错误：

- 邮箱已存在。
- 邮箱格式不合法。
- 密码不符合规则。

### `POST /api/v1/sessions`

邮箱密码登录，并返回 access token。

请求字段：

- `email`
- `password`

成功响应 `data`：

- `user`
- `access_token`
- `token_type`
- `expires_in`

关键错误：

- 邮箱或密码错误。
- 账号不可用。

### `GET /api/v1/users/me`

获取当前登录用户。

鉴权：

- Bearer access token。

成功响应 `data`：

- `id`
- `email`
- `display_name`
- `status`
- `created_at`
- 最小 profile 字段。

关键错误：

- 缺少 token。
- token 无效或过期。
- 账号不可用。

### `PATCH /api/v1/users/me/password`

修改当前用户密码。

鉴权：

- Bearer access token。

请求字段：

- `old_password`
- `new_password`

成功响应 `data`：

```json
{
  "updated": true
}
```

关键错误：

- 旧密码错误。
- 新密码不符合规则。
- token 无效或账号不可用。

### `POST /api/v1/users/password-reset-requests`

预留发送密码重置请求接口。

请求字段：

- `email`

首版行为：

- 不发送真实邮件或验证码。
- 返回明确的未配置或未实现响应。

### `POST /api/v1/users/password-resets`

预留密码重置提交接口。

请求字段：

- `email`
- `code` 或 `reset_token`
- `new_password`

首版行为：

- 不执行真实密码重置。
- 返回明确的未配置或未实现响应。

### `GET /api/v1/auth/oidc/{provider}/login`

预留 OIDC 登录跳转入口。

首版行为：

- 支持识别 `authentik` provider 名。
- provider 未配置时返回明确错误。
- 不访问真实 Authentik。

### `GET /api/v1/auth/oidc/{provider}/callback`

预留 OIDC 回调入口。

首版行为：

- provider 未配置时返回明确错误。
- 不创建真实第三方登录会话。

### `POST /api/v1/auth/oidc/{provider}/sessions`

预留使用一次性 `login_code` 换取 access token 的接口。

请求字段：

- `login_code`

首版行为：

- provider 未配置时返回明确错误。
- 不生成真实 access token。

## 数据模型与迁移

重写后使用 PostgreSQL、SQLAlchemy 2 async 和 Alembic。

首版认证需要最小用户模型：

- `id`
- `email`
- `hashed_password`
- `display_name`
- `status`
- `created_at`
- `updated_at`

最小用户 profile 可包含：

- `user_id`
- `english_level`
- `learning_goal`
- `preferred_explanation_language`

OIDC 预留模型方向：

- `user_id`
- `provider`
- `provider_subject`
- `email`
- `email_verified`
- `raw_profile`

一次性 OIDC login code 预留模型方向：

- `code_hash`
- `user_id`
- `provider`
- `redirect_uri`
- `expires_at`
- `used_at`

迁移要求：

- 认证相关表结构必须通过 Alembic migration 创建。
- 是否保留旧数据不在本计划中处理；如果需要迁移旧数据，必须单独确认。

## 服务流程

### 邮箱注册

1. 校验请求字段。
2. 检查邮箱是否已存在。
3. 创建用户和最小 profile。
4. 生成 access token。
5. 返回用户信息和 token。

### 邮箱登录

1. 按邮箱查找用户。
2. 校验密码。
3. 校验用户状态。
4. 生成 access token。
5. 返回用户信息和 token。

### 获取当前用户

1. 从 Bearer token 解析用户身份。
2. 校验 token 类型、过期时间和用户状态。
3. 返回用户与最小 profile。

### 修改密码

1. 校验当前用户 token。
2. 校验旧密码。
3. 校验新密码规则。
4. 更新密码哈希。
5. 返回更新结果。

### OIDC 预留

1. 校验 provider 名。
2. 检查 provider 是否已启用且配置完整。
3. 未启用或配置不完整时返回稳定错误。
4. 不访问真实外部 provider。

## 错误处理

必须返回统一响应结构。

建议错误类型：

- `400`：请求参数错误。
- `401`：认证失败、token 无效、密码错误、login_code 无效。
- `403`：账号不可用。
- `404`：provider 不存在。
- `409`：邮箱已存在。
- `501`：密码重置或 OIDC 能力已预留但尚未实现。
- `503`：provider 未配置或不可用。

错误响应必须包含稳定 `code` 和可读 `message`。不得暴露密码哈希、token secret、provider secret 或内部异常细节。

## 测试场景

- 注册成功，返回用户信息和 access token。
- 重复邮箱注册失败。
- 邮箱格式错误注册失败。
- 密码不符合规则注册失败。
- 邮箱密码登录成功。
- 错误密码登录失败。
- 不存在邮箱登录失败。
- 非 active 用户无法登录。
- Bearer token 获取当前用户成功。
- 缺少 token 获取当前用户失败。
- 无效 token 获取当前用户失败。
- 修改密码成功。
- 旧密码错误时修改密码失败。
- 修改密码后旧密码失效，新密码可登录。
- 密码重置预留接口返回明确的未配置或未实现响应。
- OIDC provider 未配置时返回明确错误。
- OIDC 预留接口不访问真实外部网络。

## 验收标准

- 认证 feature plan 已完整写入本文件。
- 后续实现时，所有公开认证 API 均使用 `/api/v1`。
- 后续实现时，响应结构统一为 `{ code, message, data }`。
- 后续实现时，认证测试不依赖真实 Authentik 或外部网络。
- 后续实现时，数据库结构变化必须包含 Alembic migration。
- 后续实现时，README、`.env.example`、测试和相关 docs 与实现保持一致。

## 待确认问题

- access token 的默认过期时间。
- 密码强度规则。
- `status` 支持哪些枚举值。
- 密码重置后续使用邮件、验证码还是一次性 token。
- OIDC 真实接入时 Authentik 的 issuer、client、redirect URI 和 scopes。
