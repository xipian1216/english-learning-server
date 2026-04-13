# 认证与会话接口文档

本文档定义 `english-learning-server` 的第一版认证与会话接口，适用于浏览器插件前端与后端 API 的用户身份识别场景。

目标：

- 支持用户注册
- 支持用户创建登录会话
- 使用 JWT access token 进行接口鉴权
- 通过 Bearer Token 识别当前用户
- 为后续 refresh token、多端会话管理预留扩展空间

## 1. 设计约定

### 1.1 RESTful 约定

本项目后续接口默认遵循以下规范：

- 路径优先使用资源名词，而不是动作动词
- 通过 HTTP Method 表达操作语义
- 资源创建使用 `POST`
- 资源读取使用 `GET`
- 资源局部更新使用 `PATCH`
- 资源删除使用 `DELETE`
- 认证相关接口尽量建模为“用户资源”和“会话资源”

示例：

- 创建用户：`POST /api/v1/users`
- 创建登录会话：`POST /api/v1/sessions`
- 获取当前用户：`GET /api/v1/users/me`
- 修改当前用户密码：`PATCH /api/v1/users/me/password`

### 1.2 当前认证方案

当前阶段建议采用：

- 邮箱 + 密码注册/登录
- JWT access token 鉴权
- 受保护接口统一使用 `Authorization: Bearer <access_token>`

说明：

- 当前文档先以 access token 为核心。
- refresh token 可在后续版本中补充。
- token 不是静态字符串，而是由后端在登录成功后动态签发的、带过期时间的身份令牌。

## 2. 基础信息

### 2.1 Base URL

开发环境示例：

```text
http://localhost:8000
```

API 前缀：

```text
/api/v1
```

### 2.2 请求与响应格式

- 请求体：`application/json`
- 响应体：`application/json`
- 字符编码：`UTF-8`
- 时间格式：ISO 8601

### 2.3 统一响应结构

成功响应示例：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "access_token": "<token>",
    "token_type": "bearer"
  }
}
```

失败响应示例：

```json
{
  "code": 40100,
  "message": "invalid email or password",
  "data": null
}
```

## 3. JWT 说明

JWT 全称为 `JSON Web Token`，用于在用户登录成功后标识用户身份。

后端签发的 access token 建议包含以下信息：

- `sub`：用户 ID
- `type`：token 类型，建议为 `access`
- `iat`：签发时间
- `exp`：过期时间

说明：

- JWT 用于身份识别，不应存放密码等敏感信息。
- access token 建议设置较短有效期，例如 `30 分钟` 到 `2 小时`。

## 4. 接口列表

### 4.1 创建用户

- Method: `POST`
- Path: `/api/v1/users`
- Auth: 否

说明：

- 该接口用于用户注册。
- 创建成功后可直接返回 access token，减少前端额外登录一次的成本。

#### 请求体

```json
{
  "email": "user@example.com",
  "password": "your_password",
  "display_name": "pian xi"
}
```

#### 字段说明

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| email | string | 是 | 用户邮箱，需唯一 |
| password | string | 是 | 用户密码，后端仅存哈希值 |
| display_name | string | 否 | 显示名称 |

#### 成功响应

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "user": {
      "id": "user_123",
      "email": "user@example.com",
      "display_name": "pian xi",
      "created_at": "2026-04-13T10:00:00Z"
    },
    "access_token": "<token>",
    "token_type": "bearer",
    "expires_in": 3600
  }
}
```

#### 失败场景

- 邮箱格式不合法
- 密码不符合规则
- 邮箱已被注册

#### 建议错误码

- `40001`：参数校验失败
- `40900`：邮箱已存在

### 4.2 创建登录会话

- Method: `POST`
- Path: `/api/v1/sessions`
- Auth: 否

说明：

- 该接口用于用户登录。
- 登录成功后返回 access token。

#### 请求体

```json
{
  "email": "user@example.com",
  "password": "your_password"
}
```

#### 字段说明

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| email | string | 是 | 用户邮箱 |
| password | string | 是 | 用户密码 |

#### 成功响应

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "access_token": "<token>",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
      "id": "user_123",
      "email": "user@example.com",
      "display_name": "pian xi"
    }
  }
}
```

#### 失败场景

- 用户不存在
- 密码错误
- 账号被禁用

#### 建议错误码

- `40100`：邮箱或密码错误
- `40300`：账号不可用

### 4.3 获取当前登录用户信息

- Method: `GET`
- Path: `/api/v1/users/me`
- Auth: 是

#### 请求头

```http
Authorization: Bearer <access_token>
```

#### 成功响应

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "id": "user_123",
    "email": "user@example.com",
    "display_name": "pian xi",
    "status": "active",
    "english_level": "B1",
    "learning_goal": "提升阅读与写作能力",
    "preferred_explanation_language": "zh-CN"
  }
}
```

#### 失败场景

- 未传 token
- token 格式错误
- token 已过期
- token 无效或签名校验失败

#### 建议错误码

- `40100`：未登录或 token 无效

### 4.4 修改当前用户密码

- Method: `PATCH`
- Path: `/api/v1/users/me/password`
- Auth: 是

说明：

- 该接口用于修改当前登录用户的密码。
- 这是对当前用户密码子资源的局部更新。

#### 请求头

```http
Authorization: Bearer <access_token>
```

#### 请求体

```json
{
  "old_password": "old_password",
  "new_password": "new_password"
}
```

#### 字段说明

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| old_password | string | 是 | 当前密码 |
| new_password | string | 是 | 新密码 |

#### 成功响应

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "updated": true
  }
}
```

#### 失败场景

- 原密码错误
- 新密码不符合规则
- token 无效

#### 建议错误码

- `40001`：参数校验失败
- `40100`：未登录或密码错误

## 5. 鉴权规则

除以下公开接口外，其余用户私有接口默认都需要 Bearer Token：

- `POST /api/v1/users`
- `POST /api/v1/sessions`

以下接口属于受保护接口示例：

- `GET /api/v1/users/me`
- `PATCH /api/v1/users/me/password`
- `POST /api/v1/vocabulary`
- `GET /api/v1/vocabulary`
- `PATCH /api/v1/vocabulary/{id}`
- `DELETE /api/v1/vocabulary/{id}`
- `POST /api/v1/ai/explain-word`
- `POST /api/v1/ai/chat-teacher`

## 6. Token 使用方式

前端在创建会话成功后，应保存 `access_token`，并在后续请求头中带上：

```http
Authorization: Bearer <access_token>
```

插件前端建议：

- 将 token 保存到扩展存储中
- 请求封装层统一注入 `Authorization` 请求头
- 当收到 `40100` 时，引导用户重新登录

## 7. 安全建议

### 7.1 密码存储

- 不允许明文存储密码
- 数据库仅存 `password_hash`
- 使用安全哈希算法，例如 `bcrypt`

### 7.2 Token 配置

- 使用环境变量配置 `SECRET_KEY`
- 不要在代码仓库中写死生产密钥
- access token 必须设置过期时间

### 7.3 传输安全

- 生产环境必须使用 HTTPS
- 避免在日志中打印完整 token

### 7.4 插件场景建议

- 前端只存 access token，不保存用户明文密码
- 用户退出登录时，清除本地 token
- 如果后续增加 refresh token，再单独设计续期接口

## 8. 后续扩展建议

当前版本先不强制实现，但后续建议补充：

- `POST /api/v1/session-refreshes`：使用 refresh token 获取新的 access token
- `DELETE /api/v1/sessions/current`：退出当前会话
- `POST /api/v1/password-reset-requests`：发起找回密码请求
- `POST /api/v1/password-resets`：执行密码重置
- 第三方登录：Google / GitHub / Apple
- 多设备登录管理

## 9. MVP 最小实现建议

如果你现在只想先把登录功能跑通，建议最少实现这四个接口：

1. `POST /api/v1/users`
2. `POST /api/v1/sessions`
3. `GET /api/v1/users/me`
4. `PATCH /api/v1/users/me/password`

只要这四步打通，后续所有用户私有接口就都可以基于 JWT Bearer 鉴权继续开发。
