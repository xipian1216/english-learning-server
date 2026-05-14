# 生词本自动查询

## 状态

implemented

## 功能目标

用户把单词加入生词本后，server 自动查询词典与翻译，缓存查询结果，并返回可展示的词条详情。

首版以后端能力为主：

- 插件展示简版。
- Web 生词本或详情页展示详版。
- Server 返回统一详情数据，由前端按场景裁剪展示。

## 非目标范围

- 不调用 AI agents。
- 不要求插件划词后立刻弹出完整词典卡片。
- 不设计复杂复习算法。
- 不实现多 provider 切换策略。
- 不要求外部查询失败时阻止用户收藏单词。

## 关键决策

- 自动查询由“加入生词本”触发。
- 加入生词本优先成功，查询失败不阻止收藏。
- Server 返回一套统一详情结构，插件和 web 自行裁剪展示。
- 外部词典和翻译 provider 必须可 mock，测试不依赖真实网络。
- 单独 `POST /api/v1/word-details` 作为复用查询入口保留，但核心验收以 `POST /api/v1/vocabulary-items` 自动查询闭环为准。

## API 设计

所有响应继续使用统一结构：

```json
{
  "code": 0,
  "message": "ok",
  "data": {}
}
```

### `POST /api/v1/vocabulary-items`

创建当前用户的生词本条目，并自动触发 lookup。

鉴权：

- Bearer access token。

请求字段：

- `text`：必填，用户加入的单词或短语。
- `source_sentence`：可选，来源句子。
- `source_url`：可选，来源页面 URL。
- `source_title`：可选，来源页面标题。
- `note`：可选，用户备注。

成功响应 `data` 至少包含：

- `item`：词本条目。
- `word_detail`：词条详情；查询完全失败时可以为 `null` 或只包含最小词条信息。
- `lookup_status`：查询状态。

`lookup_status` 建议枚举：

- `success`：词典和翻译查询均成功，或已从缓存得到完整详情。
- `partial_failed`：部分 provider 失败，但仍得到可展示的部分详情。
- `failed`：外部查询完全失败，但词本条目仍保存成功。

关键错误：

- 未登录或 token 无效。
- `text` 为空或格式不合法。
- 当前用户账号不可用。

### `POST /api/v1/word-details`

单独查询单词详情，用于详情页、搜索框或后续手动重试查询。

鉴权：

- 首版建议需要登录，避免第三方查询能力被开放滥用。

请求字段：

- `text`：必填，待查询单词或短语。

成功响应 `data` 至少包含：

- `word_detail`
- `lookup_status`
- `cache_status`

首版说明：

- 该接口作为复用查询入口保留。
- 核心验收仍以加入生词本时自动查询为准。

## 数据模型与迁移

重写后使用 PostgreSQL、SQLAlchemy 2 async 和 Alembic。

### 词典缓存模型方向

`dictionary_entries`：

- `id`
- `normalized_word`
- `display_word`
- `phonetic`
- `audio_url`
- `source_provider`
- `raw_payload`
- `cached_at`
- `updated_at`

`dictionary_senses`：

- `entry_id`
- `part_of_speech`
- `definition_en`
- `definition_zh`
- `short_definition`
- `sense_order`

`dictionary_examples`：

- `entry_id`
- `sense_id`
- `sentence_en`
- `sentence_zh`
- `example_order`

### 生词本模型方向

`user_vocabulary_items`：

- `user_id`
- `dictionary_entry_id`：查询成功或部分成功时关联；完全失败时允许为空或关联最小占位词条，具体实现时二选一并写入迁移。
- `text`
- `normalized_text`
- `source_sentence`
- `source_url`
- `source_title`
- `note`
- `status`
- `lookup_status`
- `created_at`
- `updated_at`

约束方向：

- 同一用户同一 `normalized_text` 不创建重复词本条目。
- 不同用户可复用同一词典缓存。
- 查询状态必须可持久化，便于后续重试。

## 服务流程

### 加入生词本自动查询

1. 校验当前用户。
2. 规范化 `text`，生成 `normalized_text`。
3. 检查当前用户是否已有该词本条目。
4. 查询本地词典缓存。
5. 缓存命中时直接组装 `word_detail`。
6. 缓存未命中时调用词典 provider 和翻译 provider。
7. 将成功查询到的结果写入词典缓存表。
8. 创建或返回当前用户的词本条目。
9. 返回 `item`、`word_detail` 和 `lookup_status`。

### 查询失败处理

1. 如果词典或翻译部分失败，保存已成功的部分，返回 `partial_failed`。
2. 如果两个 provider 都失败，仍创建词本条目，返回 `failed`。
3. 错误详情只记录安全、可诊断的信息，不暴露 provider secret 或内部异常栈。

### 单独查询入口

1. 校验当前用户。
2. 规范化 `text`。
3. 优先查询缓存。
4. 缓存未命中时调用 provider。
5. 返回统一 `word_detail` 与查询状态。

## 错误处理

建议错误类型：

- `400`：`text` 为空或格式不合法。
- `401`：未登录或 token 无效。
- `403`：账号不可用。
- `409`：如果实现选择对重复添加返回冲突，则使用该状态；推荐首版返回已有条目而不是报错。
- `502`：provider 返回不可解析响应时，仅用于单独查询接口。
- `503`：provider 全部不可用时，仅用于单独查询接口。

加入生词本接口中，provider 失败不应导致整体失败，除非数据库写入或鉴权失败。

## 测试场景

- 添加新单词到词本，缓存未命中时自动调用词典和翻译 provider。
- 添加新单词后写入缓存，并返回 `lookup_status = success`。
- 缓存命中时不重复调用外部 provider。
- 同一用户重复添加同一单词时返回稳定结果，不创建重复词本项。
- 不同用户添加同一单词时词典缓存复用，但词本条目用户隔离。
- 词典 provider 失败、翻译 provider 成功时仍保存，返回 `partial_failed`。
- 两个 provider 都失败时仍保存，返回 `failed`。
- 未登录用户不能添加词本或自动查询。
- `text` 为空或无效时返回参数错误。
- 外部 provider 全部 mock，测试不依赖真实网络。

## 验收标准

- `POST /api/v1/vocabulary-items` 能完成“保存生词 + 自动查询 + 返回详情”闭环。
- 查询成功时写入或复用缓存。
- 查询失败时仍能保存生词并返回明确 `lookup_status`。
- 用户词本数据严格按当前用户隔离。
- 插件和 web 可使用同一响应结构展示不同粒度信息。
- 数据库结构变化包含 Alembic migration。
- README、`.env.example`、测试和相关 docs 与实现保持一致。

## 待确认问题

- 完全失败时，`dictionary_entry_id` 是允许为空，还是创建最小占位词条。
- `lookup_status` 是否需要记录 provider 级别的失败详情。
- 缓存过期策略和手动重试策略。
- 首版支持单词还是也支持短语。
- 翻译 provider 失败时，中文释义是否可以用词典结果兜底。
