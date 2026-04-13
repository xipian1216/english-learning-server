# 数据库表设计文档

本文档用于定义 `english-learning-server` 的第一版 PostgreSQL 表结构，服务于以下核心能力：

- 用户注册与登录
- 用户英语学习画像
- 个人生词本
- 词典结果缓存
- AI 英语老师对话
- 学习记录与复习计划

当前设计以 MVP 为目标，优先支持浏览器插件的划词查词、加入生词本、查看词条详情等基础流程，同时为后续的个性化教师、RAG、学习统计与多端同步预留扩展空间。

## 1. 设计原则

- 用户数据隔离：所有用户私有学习数据都按 `user_id` 隔离。
- 公共数据复用：词典词条缓存与知识数据尽量全局复用，避免重复请求第三方 API。
- 先结构化，后智能化：基础词典事实与用户学习状态优先结构化存储，AI 输出作为增强层。
- 可扩展：字段设计兼顾短期 MVP 与后续版本演进。
- 查询友好：为常见查询场景预留索引，如按用户查生词、按词元查缓存、按复习时间拉取待复习列表。

## 2. 总体分层

建议将表分为四类：

- 账号与身份：`users`、`user_profiles`
- 公共词典数据：`dictionary_entries`、`dictionary_senses`、`dictionary_examples`、`dictionary_collocations`
- 用户学习数据：`user_vocabulary_items`、`review_records`
- AI 与扩展能力：`ai_sessions`、`ai_messages`

## 3. 表设计

### 3.1 users

用途：存储用户账号基础信息。

| 字段名 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | uuid | PK | 用户主键 |
| email | varchar(255) | UNIQUE NOT NULL | 用户邮箱 |
| password_hash | varchar(255) | NOT NULL | 密码哈希 |
| display_name | varchar(100) | NULL | 显示名称 |
| status | varchar(20) | NOT NULL DEFAULT 'active' | 账号状态，建议值：`active`、`disabled` |
| created_at | timestamptz | NOT NULL DEFAULT now() | 创建时间 |
| updated_at | timestamptz | NOT NULL DEFAULT now() | 更新时间 |

索引建议：

- 唯一索引：`email`

说明：

- 如果后续要支持第三方登录，可增加 `auth_provider`、`provider_user_id` 等字段，或拆出单独认证表。

### 3.2 user_profiles

用途：存储用户学习画像与偏好配置。

| 字段名 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | uuid | PK | 主键 |
| user_id | uuid | UNIQUE NOT NULL FK -> users.id | 关联用户 |
| english_level | varchar(20) | NULL | 英语水平，例如 `A1`、`B1`、`C1` |
| learning_goal | varchar(255) | NULL | 学习目标 |
| preferred_explanation_language | varchar(20) | NOT NULL DEFAULT 'zh-CN' | 讲解语言偏好 |
| teacher_style | varchar(100) | NULL | 老师风格偏好 |
| daily_target | integer | NULL | 每日目标词数 |
| created_at | timestamptz | NOT NULL DEFAULT now() | 创建时间 |
| updated_at | timestamptz | NOT NULL DEFAULT now() | 更新时间 |

索引建议：

- 唯一索引：`user_id`

说明：

- 这是用户长期偏好表，适合在 AI 教学接口中作为 prompt 上下文的一部分。

### 3.3 dictionary_entries

用途：缓存公共词典词条，避免重复请求第三方词典 API。

| 字段名 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | uuid | PK | 词条主键 |
| lemma | varchar(100) | NOT NULL | 词元，例如 `commit` |
| normalized_word | varchar(100) | NOT NULL | 归一化查询词，通常为小写 |
| display_word | varchar(100) | NOT NULL | 展示词形 |
| phonetic | varchar(120) | NULL | 主音标 |
| audio_url | text | NULL | 发音音频地址 |
| cefr_level | varchar(10) | NULL | 词汇难度等级，例如 `A2`、`B1` |
| frequency_rank | integer | NULL | 可选词频排名 |
| source_provider | varchar(50) | NOT NULL | 数据来源，例如 `dictionaryapi`、`oxford` |
| raw_payload | jsonb | NULL | 原始第三方响应，便于追溯 |
| cached_at | timestamptz | NOT NULL DEFAULT now() | 首次缓存时间 |
| updated_at | timestamptz | NOT NULL DEFAULT now() | 最近更新时间 |

索引建议：

- 普通索引：`lemma`
- 普通索引：`normalized_word`
- 联合索引：`(lemma, source_provider)`

说明：

- 这是全局共享表，不包含任何用户私有学习状态。
- 一个词条可以关联多个义项、多个例句、多个搭配。

### 3.4 dictionary_senses

用途：存储词条义项与词性信息。

| 字段名 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | uuid | PK | 义项主键 |
| entry_id | uuid | NOT NULL FK -> dictionary_entries.id | 关联词条 |
| part_of_speech | varchar(50) | NOT NULL | 词性，例如 `verb`、`noun` |
| definition_en | text | NULL | 英文释义 |
| definition_zh | text | NULL | 中文释义 |
| short_definition | text | NULL | 简明释义 |
| sense_order | integer | NOT NULL DEFAULT 1 | 义项顺序 |
| created_at | timestamptz | NOT NULL DEFAULT now() | 创建时间 |

索引建议：

- 普通索引：`entry_id`
- 普通索引：`part_of_speech`

说明：

- 详情页的词性、释义核心来自这里。
- 如果后续要支持更复杂的义项层级，可增加 `parent_sense_id`。

### 3.5 dictionary_examples

用途：存储词条或义项的例句。

| 字段名 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | uuid | PK | 主键 |
| entry_id | uuid | NOT NULL FK -> dictionary_entries.id | 关联词条 |
| sense_id | uuid | NULL FK -> dictionary_senses.id | 可选关联义项 |
| sentence_en | text | NOT NULL | 英文例句 |
| sentence_zh | text | NULL | 中文翻译 |
| example_order | integer | NOT NULL DEFAULT 1 | 排序 |
| created_at | timestamptz | NOT NULL DEFAULT now() | 创建时间 |

索引建议：

- 普通索引：`entry_id`
- 普通索引：`sense_id`

说明：

- 如果第三方词典没有中译，可以后续通过翻译服务补充 `sentence_zh`。

### 3.6 dictionary_collocations

用途：存储词条搭配、短语、常见表达。

| 字段名 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | uuid | PK | 主键 |
| entry_id | uuid | NOT NULL FK -> dictionary_entries.id | 关联词条 |
| phrase | varchar(255) | NOT NULL | 搭配或短语 |
| translation_zh | text | NULL | 中文解释 |
| note | text | NULL | 用法说明 |
| collocation_type | varchar(50) | NULL | 类型，例如 `phrase`、`collocation`、`derivative` |
| sort_order | integer | NOT NULL DEFAULT 1 | 排序 |
| created_at | timestamptz | NOT NULL DEFAULT now() | 创建时间 |

索引建议：

- 普通索引：`entry_id`
- 普通索引：`phrase`

说明：

- 你提到的“组词”更建议在产品上表达为“常见搭配/短语”。

### 3.7 user_vocabulary_items

用途：存储用户个人生词本条目，是 MVP 的核心表之一。

| 字段名 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | uuid | PK | 主键 |
| user_id | uuid | NOT NULL FK -> users.id | 所属用户 |
| dictionary_entry_id | uuid | NOT NULL FK -> dictionary_entries.id | 关联公共词条 |
| selected_text | varchar(100) | NULL | 用户当时划选的原始文本 |
| source_sentence | text | NULL | 来源句子 |
| source_url | text | NULL | 来源网页地址 |
| source_title | varchar(255) | NULL | 来源网页标题 |
| note | text | NULL | 用户备注 |
| status | varchar(20) | NOT NULL DEFAULT 'new' | 学习状态，建议值：`new`、`learning`、`mastered`、`archived` |
| familiarity_score | integer | NULL | 熟悉度，可约定 1-5 |
| first_added_at | timestamptz | NOT NULL DEFAULT now() | 首次加入时间 |
| last_reviewed_at | timestamptz | NULL | 最近复习时间 |
| next_review_at | timestamptz | NULL | 下次复习时间 |
| created_at | timestamptz | NOT NULL DEFAULT now() | 创建时间 |
| updated_at | timestamptz | NOT NULL DEFAULT now() | 更新时间 |

索引建议：

- 联合唯一索引：`(user_id, dictionary_entry_id)`
- 普通索引：`user_id`
- 普通索引：`status`
- 联合索引：`(user_id, next_review_at)`

说明：

- 这是用户与公共词条的关系表。
- 一个用户对同一词元通常只保留一条主记录，因此建议 `(user_id, dictionary_entry_id)` 唯一。
- 如果你后续希望允许同一单词按不同语境重复收藏，再调整唯一约束策略。

### 3.8 review_records

用途：记录每次复习行为，用于学习历史与复习算法。

| 字段名 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | uuid | PK | 主键 |
| user_id | uuid | NOT NULL FK -> users.id | 所属用户 |
| vocabulary_item_id | uuid | NOT NULL FK -> user_vocabulary_items.id | 关联生词本条目 |
| result | varchar(20) | NOT NULL | 复习结果，建议值：`correct`、`wrong`、`hard` |
| score | integer | NULL | 评分，可约定 1-5 |
| reviewed_at | timestamptz | NOT NULL DEFAULT now() | 复习时间 |
| next_review_at | timestamptz | NULL | 复习算法计算出的下次时间 |
| created_at | timestamptz | NOT NULL DEFAULT now() | 创建时间 |

索引建议：

- 普通索引：`user_id`
- 普通索引：`vocabulary_item_id`
- 联合索引：`(user_id, reviewed_at)`

说明：

- `user_vocabulary_items.next_review_at` 保存当前状态；`review_records` 保存历史轨迹。

### 3.9 ai_sessions

用途：存储 AI 英语老师对话会话。

| 字段名 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | uuid | PK | 主键 |
| user_id | uuid | NOT NULL FK -> users.id | 所属用户 |
| title | varchar(255) | NULL | 会话标题 |
| session_type | varchar(50) | NOT NULL DEFAULT 'teacher_chat' | 会话类型 |
| current_context | jsonb | NULL | 当前上下文，如选中单词、页面信息 |
| created_at | timestamptz | NOT NULL DEFAULT now() | 创建时间 |
| updated_at | timestamptz | NOT NULL DEFAULT now() | 更新时间 |

索引建议：

- 普通索引：`user_id`
- 联合索引：`(user_id, updated_at)`

### 3.10 ai_messages

用途：存储 AI 会话消息记录。

| 字段名 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | uuid | PK | 主键 |
| session_id | uuid | NOT NULL FK -> ai_sessions.id | 所属会话 |
| role | varchar(20) | NOT NULL | `user`、`assistant`、`system` |
| content | text | NOT NULL | 消息内容 |
| metadata | jsonb | NULL | 补充信息，如引用词条、模型名、token 消耗 |
| created_at | timestamptz | NOT NULL DEFAULT now() | 创建时间 |

索引建议：

- 普通索引：`session_id`
- 联合索引：`(session_id, created_at)`

说明：

- 如果后面需要做成本追踪，可在 `metadata` 中记录模型信息和 token 用量。

## 4. 关系概览

核心关系如下：

- `users` 1:1 `user_profiles`
- `dictionary_entries` 1:N `dictionary_senses`
- `dictionary_entries` 1:N `dictionary_examples`
- `dictionary_entries` 1:N `dictionary_collocations`
- `users` 1:N `user_vocabulary_items`
- `dictionary_entries` 1:N `user_vocabulary_items`
- `user_vocabulary_items` 1:N `review_records`
- `users` 1:N `ai_sessions`
- `ai_sessions` 1:N `ai_messages`

## 5. MVP 必选表

如果你要尽快支持“划词加入生词本 + 详情页展示”，建议第一阶段至少建这些表：

- `users`
- `user_profiles`
- `dictionary_entries`
- `dictionary_senses`
- `dictionary_examples`
- `dictionary_collocations`
- `user_vocabulary_items`
- `review_records`

如果当前不急着做 AI 对话，可先不建：

- `ai_sessions`
- `ai_messages`

## 6. 查询场景建议

### 6.1 划词查词

流程建议：

1. 前端传入用户划词文本。
2. 后端做归一化与词形还原。
3. 先查 `dictionary_entries`。
4. 命中后联查 `dictionary_senses`、`dictionary_examples`、`dictionary_collocations`。
5. 未命中时调用第三方词典 API，回填缓存表。

### 6.2 加入生词本

流程建议：

1. 确保 `dictionary_entries` 已存在该词条。
2. 在 `user_vocabulary_items` 中插入用户关联数据。
3. 如果已存在 `(user_id, dictionary_entry_id)`，则更新来源句子或时间，而不是重复插入。

### 6.3 详情页展示

详情页所需主要来自：

- `dictionary_entries`：单词、音标、发音、等级
- `dictionary_senses`：词性、翻译、释义
- `dictionary_examples`：例句
- `dictionary_collocations`：搭配/短语
- `user_vocabulary_items`：该用户的学习状态与来源信息

### 6.4 待复习列表

查询 `user_vocabulary_items` 中：

- `user_id = 当前用户`
- `status in ('new', 'learning')`
- `next_review_at <= now()`

## 7. 后续扩展建议

后续如要做个性化老师、RAG 与统计分析，可继续增加：

- `knowledge_documents`
- `knowledge_chunks`
- `user_learning_snapshots`
- `user_preferences`
- `api_call_logs`
- `model_usage_logs`

但这些不建议在 MVP 一开始就全部建设。

## 8. 命名与实现建议

- 表名统一使用复数蛇形命名，如 `dictionary_entries`。
- 主键统一使用 `uuid`。
- 时间统一使用 `timestamptz`。
- 状态字段优先使用明确的字符串枚举值，后期再视情况升级为 PostgreSQL enum。
- `raw_payload`、`metadata`、`current_context` 等可变字段优先使用 `jsonb`。
- 所有需要频繁查询的外键字段都应建立索引。

## 9. 当前推荐落地顺序

建议你按下面顺序建表：

1. `users`
2. `user_profiles`
3. `dictionary_entries`
4. `dictionary_senses`
5. `dictionary_examples`
6. `dictionary_collocations`
7. `user_vocabulary_items`
8. `review_records`
9. `ai_sessions`
10. `ai_messages`

这样可以先快速支撑插件的核心查词和生词本流程，再逐步扩展 AI 能力。
