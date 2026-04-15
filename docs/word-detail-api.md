# 单词详情查询接口文档

本文档定义 `english-learning-server` 中“前后端对接单词详情展示”的接口设计，用于支持浏览器插件将单词信息发送给后端，由后端返回结构化结果，前端再展示详细词条内容。

该接口面向当前 MVP 场景：

- 前端划词后获取单词文本
- 前端将单词及上下文提交给后端
- 后端调用词典/翻译能力补充数据
- 后端返回结构化单词详情
- 前端在独立页面中展示音标、词性、翻译、搭配、例句等信息

## 1. 设计目标

该接口的职责是：

- 接收前端提交的单词或短语
- 可选接收来源句子和页面信息
- 查询或生成该词的详细信息
- 返回适合前端直接渲染的结构化数据

本接口不直接负责：

- 将单词加入用户生词本
- 修改用户学习状态
- 发起 AI 教师问答

这些能力建议由独立接口负责。

## 2. RESTful 设计

该功能建议建模为“创建一次单词详情查询结果”，因此推荐接口如下：

- Method: `POST`
- Path: `/api/v1/word-details`
- Auth: 是

说明：

- 使用 `POST` 是因为前端提交的是一次查询请求，且请求体中可能包含上下文信息。
- 路径使用资源名词 `word-details`，符合当前项目的 RESTful 规范。

## 3. 请求信息

### 3.1 请求头

```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

### 3.2 请求体

```json
{
  "text": "commit",
  "source_language": "en",
  "target_language": "zh-CHS",
  "context_sentence": "She committed herself to learning English every day.",
  "source_url": "https://example.com/article",
  "source_title": "English Learning Article"
}
```

### 3.3 字段说明

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| text | string | 是 | 用户划词得到的原始文本，例如 `commit`、`committed` |
| source_language | string | 否 | 源语言，默认可为 `en` |
| target_language | string | 否 | 目标语言，默认可为 `zh-CHS` |
| context_sentence | string | 否 | 来源句子，用于辅助解释当前语境含义 |
| source_url | string | 否 | 来源网页 URL |
| source_title | string | 否 | 来源网页标题 |

说明：

- `text` 是核心字段。
- 后端收到请求后，可先进行文本清洗与词形归一，例如将 `committed` 归一到 `commit`。
- `context_sentence` 建议尽量上传，便于后端在同形异义时做更准确的解释。

## 4. 响应信息

### 4.1 成功响应示例

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "query_text": "commit",
    "normalized_text": "commit",
    "lemma": "commit",
    "source_language": "en",
    "target_language": "zh-CHS",
    "entry": {
      "word": "commit",
      "phonetic": "/kəˈmɪt/",
      "audio_url": "https://example.com/audio/commit.mp3",
      "cefr_level": "B1",
      "senses": [
        {
          "part_of_speech": "verb",
          "definition_en": "to promise or devote oneself to something",
          "definition_zh": "承诺；投入；提交",
          "short_definition": "承诺；投入"
        }
      ],
      "examples": [
        {
          "sentence_en": "She committed herself to learning English every day.",
          "sentence_zh": "她承诺每天学习英语。"
        }
      ],
      "collocations": [
        {
          "phrase": "commit to doing something",
          "translation_zh": "承诺做某事",
          "note": "常用于正式语境"
        }
      ]
    },
    "source": {
      "provider": "youdao",
      "cached": true
    }
  }
}
```

### 4.2 响应字段说明

#### 顶层字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| query_text | string | 前端原始查询文本 |
| normalized_text | string | 规范化后的文本 |
| lemma | string | 词元 |
| source_language | string | 源语言 |
| target_language | string | 目标语言 |
| entry | object | 单词详情主体 |
| source | object | 数据来源信息 |

#### `entry` 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| word | string | 展示词形 |
| phonetic | string | 音标 |
| audio_url | string \| null | 发音音频地址 |
| cefr_level | string \| null | 词汇等级 |
| senses | array | 义项列表 |
| examples | array | 例句列表 |
| collocations | array | 搭配/短语列表 |

#### `senses` 元素字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| part_of_speech | string | 词性 |
| definition_en | string \| null | 英文释义 |
| definition_zh | string \| null | 中文释义 |
| short_definition | string \| null | 简明释义 |

#### `examples` 元素字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| sentence_en | string | 英文例句 |
| sentence_zh | string \| null | 中文例句 |

#### `collocations` 元素字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| phrase | string | 搭配或短语 |
| translation_zh | string \| null | 中文解释 |
| note | string \| null | 用法说明 |

#### `source` 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| provider | string | 数据来源，例如 `youdao` |
| cached | boolean | 是否来自本地缓存 |

## 5. 失败响应示例

### 5.1 参数错误

```json
{
  "code": 40001,
  "message": "text is required",
  "data": null
}
```

### 5.2 未登录

```json
{
  "code": 40100,
  "message": "unauthorized",
  "data": null
}
```

### 5.3 上游词典/翻译服务失败

```json
{
  "code": 50010,
  "message": "dictionary provider request failed",
  "data": null
}
```

### 5.4 未查询到结果

```json
{
  "code": 40400,
  "message": "word detail not found",
  "data": null
}
```

## 6. 后端处理流程建议

建议后端按以下顺序处理该请求：

1. 校验 JWT，识别当前用户。
2. 校验 `text` 是否存在。
3. 对 `text` 进行清洗与归一化。
4. 优先查询本地缓存表，如 `dictionary_entries` 及其关联表。
5. 如果缓存未命中，则调用第三方翻译/词典接口。
6. 将结果转换为统一结构。
7. 按需回填数据库缓存。
8. 返回结构化响应给前端。

## 7. 前端使用建议

前端建议使用流程：

1. 用户在网页中划词。
2. 前端提取单词和上下文句子。
3. 前端调用 `POST /api/v1/word-details`。
4. 前端接收结构化响应。
5. 在详情页中分区展示：
   - 单词与音标
   - 词性与翻译
   - 例句
   - 搭配/短语

## 8. 与其他接口的边界

该接口只负责“查询并返回单词详情”，建议与以下接口分离：

- 加入生词本：`POST /api/v1/vocabulary-items`
- 更新学习状态：`PATCH /api/v1/vocabulary-items/{id}`
- AI 教师问答：`POST /api/v1/teacher-messages` 或其他对话资源接口

这样接口职责更清晰，也更利于后续维护。

## 9. 推荐错误码

| 错误码 | 含义 |
| --- | --- |
| 0 | 成功 |
| 40001 | 参数校验失败 |
| 40100 | 未登录或 token 无效 |
| 40400 | 未查询到词条 |
| 50010 | 第三方词典或翻译服务调用失败 |
| 50011 | 第三方服务响应异常 |

## 10. MVP 落地建议

如果你当前已经打通后端翻译能力，这个接口建议先支持以下最小字段：

- `word`
- `phonetic`
- `senses[].part_of_speech`
- `senses[].definition_zh`
- `examples`
- `collocations`

即便部分字段暂时为空，也建议先保持响应结构稳定，让前端先按统一字段渲染。

这样后续你接入更完整的词典 API 时，前端基本无需改动。
