# 技术决策

## 2026-05-08 - Server 重写采用新文档基线

### 背景

旧 `app/` 和旧 docs 已被删除，server 需要重新建立后端代码结构和项目知识库。

### 决策

以 `DEVELOPMENT_GUIDE.md` 和新的 `docs/` 作为重写基线。旧 README、旧测试和旧迁移可作为参考，但不直接代表当前实现事实。

### 影响

- 后续功能必须先写 feature plan。
- 已删除旧功能文档不会被自动恢复为 implemented 状态。
- 重写时需要同步修复测试和文档。

## 2026-05-08 - Server 文档保留在子项目内

### 背景

`english-learning` 是多项目工作区，server、agents、web、plugin 各自有不同职责和文档需求。

### 决策

server 的项目状态、架构、功能计划和测试策略写入 `english-learning-server/docs/`。根目录文档只作为通用规则或跨项目入口。

### 影响

- server 任务优先读取 server 内文档。
- 跨项目任务再读取根级和其它子项目文档。
