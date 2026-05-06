# 词典查询

## 状态

implemented

## 功能摘要

提供英文单词词典查询接口，从 `dictionaryapi.dev` 获取音标、音频、词性、英文释义、例句和来源 URL。

## 最终实现范围

- `GET /api/v1/dictionary/entries/{word}`。
- 输入单词会 trim 并转小写。
- 空单词返回业务错误 `40001`。
- provider `404` 映射为 `word not found`。
- provider HTTP、网络、超时或非法 JSON 错误映射为 `502` 类错误。

## 关键文件

- `app/api/v1/routes/dictionary.py`
- `app/services/dictionary_service.py`
- `app/clients/dictionary_api_client.py`
- `app/schemas/dictionary.py`
- `tests/test_dictionary_api.py`

## 使用方式

调用 `GET /api/v1/dictionary/entries/hello`，返回 `APIResponse[list[DictionaryEntryPayload]]`。

## 测试结果

- `tests/test_dictionary_api.py` 使用 mock `urlopen` 覆盖成功路径。

## 已知限制

- 该接口本身不写入本地缓存；缓存写入发生在单词详情聚合流程中。
- 当前主要依赖 provider 返回的英文释义，中文释义来自翻译聚合能力。

## 后续改进方向

- 增加 provider 错误路径测试。
- 支持本地缓存优先查询或多 provider fallback。
