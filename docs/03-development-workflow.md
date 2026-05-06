# 开发流程

## 本地环境准备

1. 安装 Python `>=3.12`。
2. 安装 `uv`。
3. 执行 `uv sync` 安装依赖。
4. 执行 `cp .env.example .env` 并设置本地值。
5. 确保 PostgreSQL 可访问，且 `DATABASE_URL` 指向目标数据库。

## 常用命令

- 启动开发服务：`uv run fastapi dev main.py`。
- 初始化或升级数据库：`uv run alembic upgrade head`。
- 创建迁移：`uv run alembic revision --autogenerate -m "describe your change"`。
- 运行全部测试：`uv run pytest`。
- 运行单个测试文件：`uv run pytest tests/test_translation_api.py`。
- Docker 镜像运行入口：`uv run uvicorn app.main:app --host 0.0.0.0 --port 8000`。

## 开发过程

1. 先阅读 `docs/01-project-status.md` 和任务相关文档。
2. 检查受影响 route、schema、service、repository、model 和测试。
3. 优先做最小聚焦变更，不进行无关重构。
4. 修改公共 API、数据模型、配置或部署流程时同步更新 docs。
5. 行为变化应新增或更新相关测试。
6. 完成前运行最相关验证命令，并记录无法验证的限制。

## 功能文档流转

- 计划功能放入 `docs/features/planned/`。
- 开始开发时移动到 `docs/features/in-progress/` 并记录开发步骤、涉及文件和测试计划。
- 功能实现且验证完成后移动到 `docs/features/implemented/`。
- 功能状态变化时同步更新 `docs/features/README.md`、`docs/01-project-status.md` 和 `docs/releases/current.md`。

## 文档维护过程

- 只记录从代码、配置、README 或测试中确认的事实。
- 不确定内容使用 `TODO:` 标记。
- 避免在多个文档重复详细实现；使用链接指向具体功能文档。
- 重要技术选择或架构取舍写入 `docs/09-decisions.md`。

## 发布过程

- 当前仓库没有 CI/CD 配置。
- `deploy.sh` 会将本地文件 rsync 到远端 `REMOTE_NAME` / `REMOTE_PATH`，然后在远端执行 `sudo docker compose down && sudo docker compose up --build -d`。
- `dev.sh` 使用类似流程同步到远端开发路径。
- TODO: 明确远端 `docker-compose.yml` 的来源和生产发布检查清单。

## 待确认问题

- TODO: 是否需要统一 lint、format 或 type check 命令。
- TODO: 是否需要在仓库内维护 Docker Compose 或 CI/CD 配置。
