# 翻译

## 状态

implemented

## 功能摘要

提供文本翻译接口，当前使用有道智云 provider。

## 最终实现范围

- `POST /api/v1/translations`。
- 使用有道 v3 签名，签名内容基于 app key、截断后的文本、salt、curtime 和 app secret。
- 支持 `source_language`、`target_language` 和可选 `vocab_id`。
- 缺少有道凭证时返回服务端配置错误。
- provider 错误、HTTP 错误、超时、网络错误和非法 JSON 会转换为 `AppError`。

## 关键文件

- `app/api/v1/routes/translation.py`
- `app/services/translation_service.py`
- `app/clients/youdao_client.py`
- `app/schemas/translation.py`
- `tests/test_translation_api.py`

## 使用方式

调用 `POST /api/v1/translations`，示例请求体：

```json
{
  "text": "commit",
  "source_language": "en",
  "target_language": "zh-CHS"
}
```

## 测试结果

- `tests/test_translation_api.py` 覆盖文本截断、签名生成、翻译成功、timeout 和 HTTP error。

## 已知限制

- 当前只有有道 provider。
- 翻译接口未要求用户认证。

## 后续改进方向

- 增加 provider fallback 或缓存。
- 增加调用频率限制和认证要求评估。
