# 用户生词本

## 状态

implemented

## 功能摘要

提供当前用户维度的生词列表、添加、更新和删除能力。

## 最终实现范围

- `GET /api/v1/vocabulary-items`：列出当前用户生词。
- `POST /api/v1/vocabulary-items`：添加生词，若本地词典缓存不存在，会触发单词详情构建。
- `PATCH /api/v1/vocabulary-items/{item_id}`：更新 `status`、`note`、`familiarity_score` 和 `next_review_at`。
- `DELETE /api/v1/vocabulary-items/{item_id}`：删除当前用户生词。
- 通过 `user_id + dictionary_entry_id` 唯一约束避免同一用户重复添加同一词典条目。
- 查询和更新均以当前用户隔离。

## 关键文件

- `app/api/v1/routes/vocabulary.py`
- `app/services/vocabulary_service.py`
- `app/repositories/vocabulary_repository.py`
- `app/db/models/vocabulary.py`
- `app/schemas/vocabulary.py`
- `tests/test_vocabulary_api.py`

## 使用方式

1. 使用认证接口取得 Bearer token。
2. 调用 `POST /api/v1/vocabulary-items` 添加单词。
3. 使用 `GET /api/v1/vocabulary-items` 获取当前用户生词列表。
4. 使用 `PATCH` 更新学习状态或笔记。
5. 使用 `DELETE` 删除条目。

## 测试结果

- `tests/test_vocabulary_api.py` 覆盖用户隔离、更新、删除和词典缓存引导。
- 测试需要可用数据库。

## 已知限制

- 当前没有分页、排序或筛选参数。
- 当前没有复习记录写入 API。
- `last_reviewed_at` 尚未通过当前 API 更新。

## 后续改进方向

- 增加分页、状态筛选和复习计划查询。
- 与复习记录 API 打通，自动更新复习时间和熟悉度。
