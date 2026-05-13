# AI Agents 接入边界

## 状态

planned

## 功能目标

为 server 调用 `english-learning-agents` 预留稳定边界，但不在 server 中实现 agents 内部能力。

## 非目标范围

- 不实现 prompt。
- 不选择模型。
- 不实现 agents 内部评测、工具调用或多 Agent 协作。

## 初步方向

- 在 `integrations` 中封装 agents client。
- server 负责鉴权、限流、错误映射、请求上下文和业务编排。
- agents 负责 LLM 调用和结构化输出。

## 影响模块

- `integrations`
- `services`
- `schemas`
- `api`

## 测试计划

- mock agents client 的成功路径。
- agents 超时。
- agents 返回错误。
- agents 返回结构异常。
- 当前用户鉴权和请求隔离。

## 待确认问题

- agents 内部 API 鉴权方式。
- typed client 是否由 agents 项目生成或维护。
- 首批接入哪个 agents 能力。
