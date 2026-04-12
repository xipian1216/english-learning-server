# english-learning-server API 文档

## 1. 项目目标

`english-learning-server` 是 `english-learning-plugin` 的后端服务，负责提供用户认证、个人生词本、AI 英语老师、学习记录与后续 RAG 能力支持。

当前阶段的目标是先提供一套清晰、可扩展的 API 设计，方便插件前端尽快联调，并为后续的个性化教学、知识检索、复习计划与多端同步预留空间。

## 2. 设计原则

- 面向插件优先：优先满足 Chrome/Edge 插件的调用场景。
- 先 MVP，后演进：先落地认证、生词本、AI 讲解等核心接口。
- 用户隔离：所有用户数据严格按用户维度隔离。
- 结构化输出：AI 接口尽量返回结构化字段，减少前端二次解析成本。
- 可扩展：为后续 RAG、复习算法、用户画像、长期记忆预留模型空间。

## 3. 基础信息

### 3.1 Base URL

开发环境示例：

```text
http://localhost:8000
```

API 前缀建议：

```text
/api/v1
```

完整调用示例：

```text
http://localhost:8000/api/v1/users/me
```

### 3.2 认证方式

除登录、注册等公开接口外，其余接口默认使用 Bearer Token：

```http
Authorization: Bearer <access_token>
```

### 3.3 数据格式

- 请求体：`application/json`
- 响应体：`application/json`
- 字符编码：`UTF-8`
- 时间格式：ISO 8601

### 3.4 响应约定

成功响应示例：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "id": "user_123"
  }
}
```

失败响应示例：

```json
{
  "code": 40001,
  "message": "invalid request",
  "data": null
}
```

## 4. 模块概览

当前建议接口按以下模块组织：

- 认证模块 `auth`
- 用户模块 `users`
- 生词本模块 `vocabulary`
- AI 教学模块 `ai`
- 学习记录模块 `review`

## 5. 认证模块

### 5.1 用户注册

- Method: `POST`
- Path: `/api/v1/auth/register`
- Auth: 否

请求体：

```json
{
  "email": "user@example.com",
  "password": "your_password",
  "display_name": "pian xi"
}
```

响应体：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "user": {
      "id": "user_123",
      "email": "user@example.com",
      "display_name": "pian xi",
      "created_at": "2026-04-12T10:00:00Z"
    },
    "access_token": "<token>",
    "token_type": "bearer"
  }
}
```

### 5.2 用户登录

- Method: `POST`
- Path: `/api/v1/auth/login`
- Auth: 否

请求体：

```json
{
  "email": "user@example.com",
  "password": "your_password"
}
```

响应体：

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

### 5.3 获取当前用户信息

- Method: `GET`
- Path: `/api/v1/users/me`
- Auth: 是

响应体：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "id": "user_123",
    "email": "user@example.com",
    "display_name": "pian xi",
    "english_level": "B1",
    "learning_goal": "提升阅读与写作能力",
    "preferred_explanation_language": "zh-CN",
    "daily_target": 20
  }
}
```

## 6. 用户画像模块

### 6.1 更新用户学习画像

- Method: `PATCH`
- Path: `/api/v1/users/profile`
- Auth: 是

请求体：

```json
{
  "english_level": "B1",
  "learning_goal": "提升阅读与写作能力",
  "preferred_explanation_language": "zh-CN",
  "teacher_style": "鼓励式、简明讲解",
  "daily_target": 20
}
```

响应体：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "updated": true
  }
}
```

## 7. 生词本模块

### 7.1 获取生词列表

- Method: `GET`
- Path: `/api/v1/vocabulary`
- Auth: 是

查询参数：

- `page`: 页码，默认 `1`
- `page_size`: 每页数量，默认 `20`
- `status`: `new | learning | mastered | archived`
- `keyword`: 按单词或释义搜索

响应体：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "items": [
      {
        "id": "word_001",
        "word": "commit",
        "lemma": "commit",
        "phonetic": "/kəˈmɪt/",
        "part_of_speech": "verb",
        "meaning_cn": "承诺；投入；提交",
        "meaning_en": "to promise or devote oneself to something",
        "status": "learning",
        "source_text": "She committed herself to learning English.",
        "created_at": "2026-04-12T10:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 1
    }
  }
}
```

### 7.2 新增生词

- Method: `POST`
- Path: `/api/v1/vocabulary`
- Auth: 是

请求体：

```json
{
  "word": "commit",
  "lemma": "commit",
  "phonetic": "/kəˈmɪt/",
  "part_of_speech": "verb",
  "meaning_cn": "承诺；投入；提交",
  "meaning_en": "to promise or devote oneself to something",
  "example_sentence": "She committed herself to learning English.",
  "source_type": "webpage",
  "source_text": "She committed herself to learning English.",
  "source_url": "https://example.com/article"
}
```

响应体：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "id": "word_001",
    "created": true
  }
}
```

### 7.3 更新生词状态或内容

- Method: `PATCH`
- Path: `/api/v1/vocabulary/{vocabulary_id}`
- Auth: 是

请求体：

```json
{
  "status": "mastered",
  "meaning_cn": "承诺；致力于；提交"
}
```

响应体：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "updated": true
  }
}
```

### 7.4 删除生词

- Method: `DELETE`
- Path: `/api/v1/vocabulary/{vocabulary_id}`
- Auth: 是

响应体：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "deleted": true
  }
}
```

## 8. AI 教学模块

### 8.1 解释单词

- Method: `POST`
- Path: `/api/v1/ai/explain-word`
- Auth: 是

请求体：

```json
{
  "word": "commit",
  "context_sentence": "She committed herself to learning English.",
  "user_level": "B1",
  "explanation_language": "zh-CN"
}
```

响应体：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "word": "commit",
    "pronunciation": "/kəˈmɪt/",
    "part_of_speech": "verb",
    "core_meanings": [
      {
        "language": "zh-CN",
        "text": "承诺；投入；提交"
      }
    ],
    "usage_notes": [
      "commit to 常表示致力于、承诺去做某事"
    ],
    "examples": [
      {
        "sentence": "She committed herself to learning English every day.",
        "translation": "她承诺每天学习英语。"
      }
    ],
    "memory_tip": "可以联想为把自己投入某件事中。",
    "difficulty": "B1"
  }
}
```

### 8.2 解释句子

- Method: `POST`
- Path: `/api/v1/ai/explain-sentence`
- Auth: 是

请求体：

```json
{
  "sentence": "She committed herself to learning English every day.",
  "user_level": "B1",
  "explanation_language": "zh-CN"
}
```

响应体：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "translation": "她承诺自己每天都学习英语。",
    "grammar_points": [
      "commit oneself to doing something 表示承诺去做某事",
      "learning English every day 在句中作介词 to 的宾语"
    ],
    "key_vocabulary": [
      {
        "word": "commit",
        "meaning": "承诺；投入"
      }
    ],
    "difficulty": "B1",
    "learning_tip": "记住 commit to doing 这一搭配，常用于正式表达。"
  }
}
```

### 8.3 AI 英语老师对话

- Method: `POST`
- Path: `/api/v1/ai/chat-teacher`
- Auth: 是

请求体：

```json
{
  "message": "请帮我解释 commit 和 promise 的区别，并给我两个例句。",
  "session_id": "session_001",
  "context": {
    "current_page": "popup",
    "selected_word": "commit"
  }
}
```

响应体：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "session_id": "session_001",
    "reply": "commit 更强调正式承诺、投入或提交，而 promise 更强调口头或书面的许诺。",
    "follow_up_suggestions": [
      "要不要我再给你总结 commit 常见搭配？",
      "要不要顺便比较 pledge 和 guarantee？"
    ],
    "referenced_vocabulary_ids": [
      "word_001"
    ]
  }
}
```

## 9. 学习记录与复习模块

### 9.1 提交复习结果

- Method: `POST`
- Path: `/api/v1/review/records`
- Auth: 是

请求体：

```json
{
  "vocabulary_id": "word_001",
  "result": "correct",
  "score": 5,
  "reviewed_at": "2026-04-12T12:00:00Z"
}
```

响应体：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "next_review_at": "2026-04-15T12:00:00Z",
    "status": "learning"
  }
}
```

### 9.2 获取待复习列表

- Method: `GET`
- Path: `/api/v1/review/today`
- Auth: 是

响应体：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "items": [
      {
        "vocabulary_id": "word_001",
        "word": "commit",
        "meaning_cn": "承诺；投入；提交",
        "next_review_at": "2026-04-15T12:00:00Z"
      }
    ]
  }
}
```

## 10. 未来规划接口

以下接口或能力暂不一定在第一阶段实现，但建议在后续版本中考虑：

- `POST /api/v1/ai/generate-quiz`：根据用户生词本生成练习题
- `POST /api/v1/ai/summarize-progress`：生成阶段学习总结
- `POST /api/v1/rag/search`：检索知识库或用户历史学习资料
- `POST /api/v1/ai/rewrite-sentence`：按用户水平改写句子
- `GET /api/v1/stats/overview`：获取学习统计概览

## 11. 错误码建议

| code | 含义 |
| --- | --- |
| 0 | 成功 |
| 40000 | 通用请求错误 |
| 40001 | 参数校验失败 |
| 40100 | 未登录或 token 无效 |
| 40300 | 无权限访问 |
| 40400 | 资源不存在 |
| 40900 | 资源冲突，例如重复添加生词 |
| 42900 | 请求过于频繁 |
| 50000 | 服务内部错误 |
| 50010 | AI 服务调用失败 |
| 50020 | 向量检索服务失败 |

## 12. 第一阶段实现建议

建议优先实现以下接口：

1. `POST /api/v1/auth/register`
2. `POST /api/v1/auth/login`
3. `GET /api/v1/users/me`
4. `GET /api/v1/vocabulary`
5. `POST /api/v1/vocabulary`
6. `PATCH /api/v1/vocabulary/{vocabulary_id}`
7. `DELETE /api/v1/vocabulary/{vocabulary_id}`
8. `POST /api/v1/ai/explain-word`
9. `POST /api/v1/ai/explain-sentence`
10. `POST /api/v1/ai/chat-teacher`

## 13. 后续技术建议

- 数据库优先使用 PostgreSQL。
- 用户认证建议采用 JWT access token，并为 refresh token 预留设计空间。
- AI 输出建议使用结构化 JSON，减少前端解析复杂度。
- 后续如需做个性化老师，可基于用户画像、生词本、学习记录与知识库检索共同构建提示上下文。
- 如需引入 RAG，建议优先为知识切片、embedding、检索结果引用设计独立数据模型。
