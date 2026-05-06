# AI 教师会话 API

## 状态

planned

## 功能目标

基于已有 `ai_sessions` 和 `ai_messages` 数据模型，为用户提供 AI 教师聊天或学习辅导会话 API。

## 用户价值

用户可以围绕单词、例句、阅读上下文或学习目标进行持续对话，并保留会话历史。

## 需求范围

- TODO: 定义创建会话、列出会话、读取消息、发送消息和删除会话等 API。
- TODO: 定义与 OpenAI 或其他 LLM provider 的集成方式。
- TODO: 定义消息角色、上下文结构和 token / 成本控制策略。

## 非目标范围

- TODO: 是否包含语音、图片或实时流式输出待确认。

## 设计草案

当前数据库已有：

- `ai_sessions`：用户、标题、会话类型、当前上下文、创建和更新时间。
- `ai_messages`：会话、角色、内容、metadata 和创建时间。

`app/clients/openai_client.py` 当前是占位文件。

## 影响模块

- `app/api/v1/routes/`
- `app/services/`
- `app/repositories/ai_session_repository.py`
- `app/db/models/ai_session.py`
- `app/clients/openai_client.py`
- `app/schemas/`

## 测试计划

- TODO: API 认证、用户隔离、会话 CRUD、消息写入和 provider mock 测试。

## 待确认问题

- TODO: 使用哪个 LLM provider、模型、流式协议和计费限制。
- TODO: 是否需要将单词详情、生词本或用户画像注入 prompt。
