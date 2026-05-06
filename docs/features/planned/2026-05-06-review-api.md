# 复习记录 API

## 状态

planned

## 功能目标

基于已有 `review_records` 数据模型，为用户生词本提供复习记录写入、复习历史和下次复习计划能力。

## 用户价值

用户可以跟踪单词复习结果，服务端可根据复习结果更新熟悉度和下次复习时间。

## 需求范围

- TODO: 定义创建复习记录 API。
- TODO: 定义按用户或生词条目查询复习历史 API。
- TODO: 定义 `result`、`score` 和 `next_review_at` 的业务规则。
- TODO: 定义复习记录如何更新 `user_vocabulary_items.last_reviewed_at`、`next_review_at` 和 `familiarity_score`。

## 非目标范围

- TODO: 是否实现完整间隔重复算法待确认。

## 设计草案

当前数据库已有 `review_records` 表，字段包括用户、生词条目、结果、分数、复习时间、下次复习时间和创建时间。

## 影响模块

- `app/api/v1/routes/`
- `app/services/`
- `app/repositories/review_repository.py`
- `app/db/models/review.py`
- `app/db/models/vocabulary.py`
- `app/schemas/`

## 测试计划

- TODO: 认证、用户隔离、复习记录写入、生词状态更新和查询测试。

## 待确认问题

- TODO: 复习结果枚举、分数范围和调度算法。
- TODO: 是否需要每日复习队列接口。
