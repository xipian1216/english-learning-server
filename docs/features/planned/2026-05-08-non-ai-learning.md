# 非 AI 学习功能

## 状态

planned

## 功能目标

实现不依赖 AI agents 的学习业务能力，为 web 和 plugin 提供稳定 API。

## 非目标范围

- 不实现 AI 解释、AI 造句、AI 评测等 agents 内部能力。
- 不在本初始文档中确定完整复习算法。

## 初步范围

- 词典查询。
- 翻译。
- 单词详情聚合。
- 用户词本。
- 复习记录。

## 影响模块

- `api`
- `schemas`
- `models`
- `repositories`
- `services`
- `integrations`

## 测试计划

- 词典查询成功和 provider 失败。
- 翻译成功、超时和 provider 错误。
- 单词详情聚合。
- 词本增删改查。
- 用户数据隔离。
- 第三方服务 mock。

## 待确认问题

- 字典缓存策略。
- 翻译 provider 失败时的降级方式。
- plugin 本地词本与 server 词本同步策略。
- 复习记录第一阶段做到什么程度。
