# 单词详情聚合与缓存

## 状态

implemented

## 功能摘要

提供受保护的单词详情聚合接口，将词典查询和翻译结果组合成单词详情页所需数据，并写入本地词典缓存。

## 最终实现范围

- `POST /api/v1/word-details`，需要 Bearer token。
- 输入文本会 trim 并转小写。
- 优先按 normalized text 查询 `dictionary_entries` 缓存。
- 缓存命中时从数据库构造 senses 和 examples。
- 缓存未命中时查询 `dictionaryapi.dev`，再调用有道翻译生成中文释义。
- 若提供 `context_sentence`，会额外翻译上下文例句并放入 examples 首位。
- 新聚合结果通过 repository 写入本地词典缓存。

## 关键文件

- `app/api/v1/routes/word_detail.py`
- `app/services/word_detail_service.py`
- `app/repositories/dictionary_repository.py`
- `app/db/models/dictionary.py`
- `app/schemas/word_detail.py`
- `tests/test_word_detail_api.py`

## 使用方式

调用 `POST /api/v1/word-details`，示例请求体：

```json
{
  "text": "commit",
  "source_language": "en",
  "target_language": "zh-CHS",
  "context_sentence": "She committed herself to learning English every day."
}
```

## 测试结果

- `tests/test_word_detail_api.py` 覆盖未认证返回 `401`、聚合成功和缓存写入。
- 缓存写入测试需要可用数据库。

## 已知限制

- 当前只使用词典 provider 返回的第一个 entry。
- `collocations` 当前返回空列表。
- 中文释义是将翻译结果用 `；` 拼接，不是逐 sense 的专业释义。

## 后续改进方向

- 增加更精细的 sense 翻译和 collocation 数据来源。
- 增加缓存失效策略和 provider fallback。
