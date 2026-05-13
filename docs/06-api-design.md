# API 设计

## API 范围

本文件记录 server 业务 API 的通用约定。具体接口应写入对应 feature plan。

## 路径约定

所有业务 API 默认使用：

```text
/api/v1
```

## 响应约定

统一响应结构：

```json
{
  "code": 0,
  "message": "ok",
  "data": {}
}
```

约定：

- 成功响应 `code` 为 `0`。
- 错误响应必须包含稳定错误码和可读消息。
- `data` 无返回数据时可以为 `null`。
- 字段命名默认使用 `snake_case`。

## 鉴权约定

- 涉及当前用户数据的接口必须鉴权。
- 用户数据查询和修改必须按当前用户隔离。
- 第三方登录、token 生命周期和账号绑定规则在认证 feature plan 中定义。

## 兼容性

- 修改公开 API 前必须更新对应 feature plan。
- 影响 web 或 plugin 的接口变更必须同步通知或更新调用方。

## 待确认问题

- Web 当前 `/v1` 调用是否统一迁移到 `/api/v1`。
- Plugin 接入 server 后的认证方式。
