# 测试

## 测试策略

当前测试以 pytest 为入口，覆盖配置校验、认证 API、词典 API、翻译 API、单词详情 API、生词本 API 和 PostgreSQL 连接。外部 provider 请求在多数 API 测试中通过 `unittest.mock.patch` 替换 `urlopen`。

## 测试结构

- `tests/test_settings.py`：配置必填项和默认值。
- `tests/test_auth_api.py`：注册、登录、当前用户和修改密码流程。
- `tests/test_dictionary_api.py`：词典查询成功路径。
- `tests/test_translation_api.py`：有道签名、文本截断、翻译成功和 provider 错误。
- `tests/test_word_detail_api.py`：认证要求、单词详情聚合和缓存写入。
- `tests/test_vocabulary_api.py`：用户隔离、创建、更新、删除和词典缓存引导。
- `tests/test_pg_connection.py`：PostgreSQL 连接实验性脚本。

## 命令

- 全部测试：`uv run pytest`。
- 单文件测试：`uv run pytest tests/test_vocabulary_api.py`。
- 手动执行部分测试文件：部分文件包含 `if __name__ == "__main__"` 入口，可用 `uv run python tests/test_translation_api.py`。

## 必要检查

- 修改 API 行为后运行对应 `tests/test_*_api.py`。
- 修改配置后运行 `uv run pytest tests/test_settings.py`。
- 修改数据库模型或 repository 后运行相关 API 测试，并检查是否需要 Alembic 迁移。
- 修改 Docker 或部署脚本后至少检查命令和路径是否仍与 `Dockerfile`、`exclude.list` 一致。

## 手动验证

- 启动服务：`uv run fastapi dev main.py`。
- 健康检查：`GET /healthz`，应返回 `{"status":"ok","environment":"..."}`。
- 认证接口可通过注册获得 Bearer token 后验证受保护接口。

## 待确认问题

- TODO: `tests/test_pg_connection.py` 在导入时会直接连接数据库、建表并写入数据，不适合作为普通自动化测试长期保留。
- TODO: 部分测试依赖真实 PostgreSQL，当前没有测试数据库隔离或 fixture 清理规范。
- TODO: 当前没有 CI 配置记录测试矩阵。
