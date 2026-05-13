# 开发流程

## 开发前阅读

非简单变更前，应优先阅读：

1. [`../INSTRUCTIONS.md`](../INSTRUCTIONS.md)
2. [`../DEVELOPMENT_GUIDE.md`](../DEVELOPMENT_GUIDE.md)
3. [`01-project-status.md`](01-project-status.md)
4. 与任务相关的 feature plan

## 标准流程

1. 明确任务目标和范围。
2. 阅读相关代码、配置、测试和文档。
3. 如果是业务功能，先确认或编写 feature plan。
4. 实现最小必要变更。
5. 更新或新增测试。
6. 运行相关验证。
7. 更新文档和功能状态。
8. 总结变更、验证方式和风险。

## Feature Plan 门禁

每个业务功能开发前必须有单独 feature plan。

feature plan 至少包含：

- 目标。
- 非目标。
- API 设计。
- 数据模型与迁移。
- 服务流程。
- 错误处理。
- 测试场景。
- 验收标准。

没有 feature plan 的业务功能不直接实现。

## 文档状态流转

推荐状态：

```text
planned -> in-progress -> implemented
```

移动文档或更新状态前必须确认：

- 用户明确要求维护 docs，或当前任务明确包含文档更新。
- 实现状态真实。
- 测试或验收结果来自真实执行或用户确认。

## 常用验证

```bash
uv run pytest
```

重写早期如果测试暂不可运行，应在任务总结中说明原因，并提供下一步恢复测试的路径。
