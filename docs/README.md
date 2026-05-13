# English Learning Server 文档总入口

本目录是 `english-learning-server` 的项目文档库，用于记录后端重写期间的项目状态、架构边界、开发流程、功能计划、测试策略、部署方式和技术决策。

## 推荐阅读顺序

1. [`../DEVELOPMENT_GUIDE.md`](../DEVELOPMENT_GUIDE.md)：后端重写的长期开发指南。
2. [`01-project-status.md`](01-project-status.md)：当前项目状态和下一步重点。
3. [`02-architecture.md`](02-architecture.md)：目标架构和模块边界。
4. [`03-development-workflow.md`](03-development-workflow.md)：开发流程和 feature plan 规则。
5. [`features/README.md`](features/README.md)：功能计划索引。

## 目录说明

- [`00-overview.md`](00-overview.md)：项目概览。
- [`01-project-status.md`](01-project-status.md)：当前状态。
- [`02-architecture.md`](02-architecture.md)：架构说明。
- [`03-development-workflow.md`](03-development-workflow.md)：开发流程。
- [`04-coding-standards.md`](04-coding-standards.md)：编码规范。
- [`05-testing.md`](05-testing.md)：测试策略。
- [`06-api-design.md`](06-api-design.md)：API 约定。
- [`07-deployment.md`](07-deployment.md)：部署与配置。
- [`08-troubleshooting.md`](08-troubleshooting.md)：排障说明。
- [`09-decisions.md`](09-decisions.md)：技术决策记录。
- [`10-glossary.md`](10-glossary.md)：术语表。
- [`features/`](features/)：功能文档。
- [`releases/`](releases/)：版本文档。

## 维护原则

- 本目录记录 server 项目事实，不记录 web、plugin、agents 的内部实现细节。
- 每个业务功能开发前必须有独立 feature plan。
- 旧 `app/` 已删除，不应把旧实现文档当作当前已实现事实。
- 文档移动或状态流转必须基于真实实现、测试结果或用户明确确认。
