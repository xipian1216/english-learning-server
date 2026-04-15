# DictionaryAPI 接口文档

本文档整理 `DictionaryAPI` 英语词典接口 `https://api.dictionaryapi.dev/api/v2/entries/en/<word>` 的典型用法与返回结构，供 `english-learning-server` 后端在接入、比对和调试时参考。

说明：

- 该文档基于公开接口路径 `https://api.dictionaryapi.dev/api/v2/entries/en` 的常见使用方式整理。
- `DictionaryAPI` 适合作为英语单词基础词典数据源，用于补充音标、词性、释义、例句等字段。
- 后端应自行封装并转换为项目内部统一结构，不建议前端直接依赖上游原始响应。

## 1. 接口用途

该接口用于根据英文单词查询英语词典信息，典型可获得以下内容：

- 单词原文
- 音标
- 发音音频链接
- 词性
- 英文释义
- 例句
- 同义词
- 反义词

适合的项目场景：

- 划词后查词
- 详情页展示基础词条信息
- 为后端缓存词典数据提供原始来源

## 2. 接口信息

- Provider: DictionaryAPI
- Method: `GET`
- URL Pattern: `https://api.dictionaryapi.dev/api/v2/entries/en/<word>`
- Auth: 无需鉴权
- Content-Type: `application/json`

示例：

```text
GET https://api.dictionaryapi.dev/api/v2/entries/en/commit
```

说明：

- `<word>` 为英文单词，通常建议使用 URL 编码后的查询词。
- 如果输入不是标准词形，例如 `committed`、`studies`，建议后端先进行词形归一，再调用上游接口。

## 3. 请求参数

该接口通常通过 URL 路径传参，不使用 JSON 请求体。

| 参数位置 | 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| path | word | string | 是 | 待查询英文单词 |

示例：

```text
/entries/en/commit
```

## 4. 成功响应结构

该接口成功时通常返回一个数组，数组中每个元素代表一个词条对象。

典型响应结构如下：

```json
[
  {
    "word": "commit",
    "phonetic": "/kəˈmɪt/",
    "phonetics": [
      {
        "text": "/kəˈmɪt/",
        "audio": "https://..."
      }
    ],
    "meanings": [
      {
        "partOfSpeech": "verb",
        "definitions": [
          {
            "definition": "To give in trust.",
            "example": "She committed herself to learning English.",
            "synonyms": [],
            "antonyms": []
          }
        ],
        "synonyms": [],
        "antonyms": []
      }
    ],
    "license": {
      "name": "CC BY-SA 3.0",
      "url": "https://creativecommons.org/licenses/by-sa/3.0"
    },
    "sourceUrls": [
      "https://en.wiktionary.org/wiki/commit"
    ]
  }
]
```

## 5. 响应字段说明

### 5.1 词条层字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| word | string | 词条文本 |
| phonetic | string \| null | 主音标 |
| phonetics | array | 发音信息列表 |
| meanings | array | 词义列表 |
| license | object \| null | 许可信息 |
| sourceUrls | array | 来源链接 |

### 5.2 `phonetics` 元素字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| text | string \| null | 音标文本 |
| audio | string \| null | 发音音频链接 |
| sourceUrl | string \| null | 音频来源地址 |
| license | object \| null | 许可信息 |

说明：

- 有时 `phonetic` 为空，但 `phonetics` 中有可用音标。
- 后端应优先挑选首个有效的 `text` 和 `audio` 作为主展示字段。

### 5.3 `meanings` 元素字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| partOfSpeech | string | 词性 |
| definitions | array | 释义列表 |
| synonyms | array | 同义词列表 |
| antonyms | array | 反义词列表 |

### 5.4 `definitions` 元素字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| definition | string | 英文释义 |
| example | string \| null | 示例句 |
| synonyms | array | 同义词 |
| antonyms | array | 反义词 |

## 6. 失败响应

当未查询到词条时，接口通常返回错误对象，而不是数组。

典型结构如下：

```json
{
  "title": "No Definitions Found",
  "message": "Sorry pal, we couldn't find definitions for the word you were looking for.",
  "resolution": "You can try the search again at later time or head to the web instead."
}
```

后端接入时应注意：

- 成功是数组结构
- 失败是对象结构
- 不能只按 HTTP 200 判断业务成功，必须同时检查响应 JSON 结构

## 7. 后端接入建议

建议在 `english-learning-server` 中将该上游接口封装为内部词典提供者，而不是直接暴露给前端。

推荐内部处理流程：

1. 接收前端的单词查询请求。
2. 对文本做清洗和词形归一。
3. 先查本地缓存表 `dictionary_entries`。
4. 若缓存未命中，则请求 `DictionaryAPI`。
5. 解析 `word`、`phonetic`、`phonetics`、`meanings`、`definitions`、`example` 等字段。
6. 转为内部统一结构后回填数据库。
7. 返回给前端稳定的响应格式。

## 8. 推荐字段映射

建议将上游字段映射到你自己的内部结构：

| 上游字段 | 内部字段 | 说明 |
| --- | --- | --- |
| word | lemma / word | 展示词与词元 |
| phonetic | phonetic | 主音标 |
| phonetics[].audio | audio_url | 发音链接 |
| meanings[].partOfSpeech | senses[].part_of_speech | 词性 |
| definitions[].definition | senses[].definition_en | 英文释义 |
| definitions[].example | examples[].sentence_en | 英文例句 |
| definitions[].synonyms | synonyms | 同义词 |
| definitions[].antonyms | antonyms | 反义词 |

说明：

- `DictionaryAPI` 本身主要提供英英词典数据。
- 如果你需要中文翻译，建议由：
  - 其他翻译 API 补充，或
  - LLM/翻译服务生成 `definition_zh`

## 9. 在你项目中的定位

对于当前的 `english-learning-server`，`DictionaryAPI` 更适合承担：

- 英文词典基础数据来源
- 音标与发音来源
- 英文释义来源
- 例句来源

而以下能力不建议完全依赖它：

- 中文释义主来源
- 用户个性化讲解
- 学习建议
- 近义词辨析型教学内容

因此推荐组合策略：

- `DictionaryAPI`：基础英英词典
- 有道或其他翻译服务：中文翻译补充
- 你自己的数据库：缓存与统一结构
- LLM：教学增强

## 10. 风险与注意事项

后端使用时建议关注以下事项：

- 上游是公共接口，稳定性和限流策略需自行评估
- 字段并不一定每次都完整，尤其是音频、例句、同义词
- 某些词可能返回多个词条对象，需要自行合并或择优
- 未命中时返回对象结构，不能按成功数组逻辑解析
- 如果要长期用在正式产品中，建议评估服务可用性与授权边界

## 11. 推荐的最小可用策略

如果你当前只是为了支撑“划词后详情页展示”，建议最少提取这些字段：

- `word`
- `phonetic`
- `phonetics[].audio`
- `meanings[].partOfSpeech`
- `definitions[].definition`
- `definitions[].example`

再结合你自己的翻译服务补出：

- `definition_zh`
- `example_zh`

这样就能快速构成前端详情页所需的主要信息。

## 12. 推荐的内部统一响应示例

```json
{
  "query_text": "commit",
  "lemma": "commit",
  "entry": {
    "word": "commit",
    "phonetic": "/kəˈmɪt/",
    "audio_url": "https://...",
    "senses": [
      {
        "part_of_speech": "verb",
        "definition_en": "to promise or devote oneself to something",
        "definition_zh": "承诺；投入"
      }
    ],
    "examples": [
      {
        "sentence_en": "She committed herself to learning English every day.",
        "sentence_zh": "她承诺每天学习英语。"
      }
    ]
  },
  "source": {
    "provider": "dictionaryapi.dev",
    "cached": false
  }
}
```

这样可以让前端不依赖上游结构，同时方便你后续切换到别的词典数据源。
