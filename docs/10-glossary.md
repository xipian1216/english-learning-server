# 术语表

## APIResponse

项目统一 API 响应结构，包含 `code`、`message` 和 `data`。

## AppError

项目业务异常类型，由全局异常处理器转换为统一错误响应。

## Dictionary Entry

词典条目，对应 `dictionary_entries` 表，存储 lemma、normalized word、音标、音频和 provider 原始数据。

## Sense

词义，对应 `dictionary_senses` 表，包含词性、英文释义、中文释义和短释义。

## Vocabulary Item

用户生词本条目，对应 `user_vocabulary_items` 表，以用户和词典条目为唯一边界。

## Word Detail

单词详情聚合结果，结合词典释义、翻译、例句和缓存来源信息。

## Provider

外部服务供应方。当前实际使用 `dictionaryapi.dev` 和有道智云。

## Review Record

复习记录数据模型，对应 `review_records` 表。当前代码中未暴露 API。

## AI Session

AI 会话数据模型，对应 `ai_sessions` 和 `ai_messages` 表。当前代码中未暴露 API。
