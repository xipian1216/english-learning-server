# 日志系统方案

## 目标

基于 Python 标准库 `logging` 设计并落地项目级日志系统，为 `english-learning-server` 提供统一、可扩展、可维护的日志能力。

本方案要求从一开始就采用按职责拆分的目录结构，而不是将所有日志能力堆放在单一文件中。本文重点描述日志系统的目录设计、职责边界、规范要求和实施清单，不展开具体代码实现。

---

## 核心设计原则

### 1. 基于标准库 logging 进行轻量封装
- 底层统一使用 Python 标准库 `logging`
- 项目层只做规范化封装，不自建复杂日志框架
- 不替代 `logging`，而是统一其初始化、上下文、格式与接入方式

### 2. 从第一天开始按职责拆分
- 日志系统从第一阶段就采用目录化设计
- 不建议将初始化、上下文、格式化、中间件、过滤器全部堆在一个文件里
- 每个模块职责必须清晰，便于后续扩展和测试

### 3. 统一入口，分层实现
- 对业务代码暴露统一的日志使用入口
- 对内部实现按职责拆分模块
- 保证业务层使用简单，同时内部实现可维护、可演进

### 4. 环境可控、输出一致
- 开发环境优先可读性
- 生产环境优先结构化和可检索性
- 测试环境优先稳定、低噪音
- 所有环境下日志行为都应通过配置项控制

### 5. 安全优先
- 日志必须服务于排障、审计与监控
- 严禁记录密码、token、密钥、敏感原文和可复用凭据

---

## 目录结构要求

日志系统从一开始采用如下目录结构：

```text
app/core/logging/
  __init__.py
  setup.py
  context.py
  formatters.py
  filters.py
  middleware.py
```

如后续能力扩展，也可继续增加：

```text
app/core/logging/
  __init__.py
  setup.py
  context.py
  formatters.py
  filters.py
  middleware.py
  constants.py
  schemas.py
```

### 强制要求
- 日志能力必须放在 `app/core/logging/` 目录下统一管理
- 不再建议只保留单个 `app/core/logger.py` 文件作为全部实现
- 业务模块禁止自行定义零散日志初始化逻辑

---

## 各模块职责定义

### 1. `app/core/logging/__init__.py`
职责：
- 对外暴露统一使用入口
- 统一导出项目允许业务层直接使用的公共方法

应承担的内容：
- 导出 `get_logger`
- 导出 `setup_logging`
- 必要时导出请求上下文相关工具

规范要求：
- 业务代码只应从该统一入口或日志包公开接口获取 logger
- 不应让业务层直接依赖内部实现细节

---

### 2. `app/core/logging/setup.py`
职责：
- 负责日志系统初始化
- 负责 root logger、handler、formatter、logger level 等装配
- 负责协调项目 logger 与 uvicorn logger 行为

应承担的内容：
- 初始化日志系统的方法
- 根据配置项决定日志级别、formatter、handler
- 管理开发/测试/生产环境下的日志行为差异

规范要求：
- 全项目只允许有一个统一初始化入口
- 禁止多个模块重复调用 `basicConfig()`
- 禁止业务模块自行挂载 handler 或修改 root logger
- 初始化逻辑必须只在应用启动阶段调用一次

---

### 3. `app/core/logging/context.py`
职责：
- 管理请求级上下文信息
- 支持 request_id、user_id、path、method 等上下文注入日志
- 通过 `contextvars` 或等效方式维护上下文

建议支持的上下文字段：
- `request_id`
- `user_id`
- `path`
- `method`
- `client_ip`

规范要求：
- 请求上下文必须自动注入，不应要求业务代码手工反复拼接
- 请求结束后必须正确清理上下文，避免串请求污染
- 上下文字段应保持稳定命名，便于结构化日志和日志平台检索

---

### 4. `app/core/logging/formatters.py`
职责：
- 定义日志输出格式
- 管理文本日志 formatter 与 JSON 日志 formatter
- 统一约束输出字段

第一阶段至少包含：
- 面向开发环境的人类可读文本 formatter

后续阶段建议支持：
- 结构化 JSON formatter

文本日志至少应包含：
- 时间
- 级别
- logger 名称
- message

结构化日志后续应支持：
- timestamp
- level
- logger
- message
- request_id
- user_id
- path
- method
- status_code
- duration_ms

规范要求：
- formatter 职责只处理输出格式，不掺杂初始化逻辑
- 不允许在业务代码中手工拼装复杂日志前缀

---

### 5. `app/core/logging/filters.py`
职责：
- 为日志记录注入公共上下文字段
- 实现敏感字段过滤与脱敏逻辑
- 为 formatter 提供标准字段

建议承担的内容：
- RequestContextFilter
- SensitiveDataFilter
- 缺省字段补齐逻辑

规范要求：
- 所有记录输出前应具备稳定字段结构
- 对缺失字段要有兜底处理，避免 formatter 因字段不存在而报错
- 对敏感字段必须提供过滤或脱敏能力

---

### 6. `app/core/logging/middleware.py`
职责：
- 与 FastAPI 集成
- 为每个请求创建请求上下文
- 记录 access log
- 将 request_id 注入当前请求链路

最低要求：
- 记录 method
- 记录 path
- 记录 status_code
- 记录 duration_ms
- 记录 request_id

规范要求：
- 中间件不记录完整敏感请求体
- 不直接记录密码、Authorization、token 等敏感信息
- 请求结束后必须释放上下文
- 中间件日志应避免与 uvicorn access log 重复输出

---

## 对业务层暴露的统一使用方式

日志系统虽然目录拆分，但对业务层必须保持统一使用方式。

### 业务代码使用要求
- 统一使用项目日志包导出的 `get_logger`
- 统一按模块名获取 logger
- 禁止业务模块自行初始化 logging
- 禁止在业务代码中使用 `print()` 代替日志

推荐目标用法：
- `from app.core.logging import get_logger`
- `logger = get_logger(__name__)`

### logger name 规范
logger 名称统一使用模块路径，例如：
- `app.main`
- `app.api.v1.routes.auth`
- `app.services.translation_service`
- `app.repositories.user_repository`
- `app.ai.workflows.session_workflow`

---

## 配置项要求

日志系统相关配置应统一放在 `app/core/config.py` 中。

第一阶段建议至少支持：
- `APP_LOG_LEVEL`
- `APP_LOG_JSON`
- `APP_LOG_ACCESS_ENABLED`

可选扩展项：
- `APP_LOG_FILE_ENABLED`
- `APP_LOG_FILE_PATH`
- `APP_LOG_ROTATION_ENABLED`
- `APP_LOG_SQL_ENABLED`
- `APP_LOG_EXTERNAL_CALL_ENABLED`

规范要求：
- 所有日志行为优先通过配置项控制
- 不允许使用硬编码切换环境模式
- 默认值应兼顾本地开发体验与线上可维护性

---

## 日志级别语义规范

### DEBUG
用于开发调试信息，例如：
- 分支判断
- 外部调用中间状态
- SQL 调试信息（仅受控开启）
- 请求参数摘要（需避开敏感字段）

### INFO
用于正常业务流程中的关键节点，例如：
- 应用启动/关闭
- 用户注册成功
- 登录成功
- 查词完成
- 外部 provider 调用成功

### WARNING
用于业务可恢复异常或风险提示，例如：
- 登录失败
- 参数不合法
- provider 临时异常
- 回退策略触发

### ERROR
用于局部失败且需要关注的问题，例如：
- 外部接口失败
- 数据处理失败
- 某请求执行失败

### EXCEPTION
用于记录未预期异常，并保留 traceback。

规范要求：
- 普通业务失败不得滥用 exception
- 所有日志不得统一粗暴写成 info
- 必须体现不同级别的语义边界

---

## 必须记录的日志类型

### 1. 应用生命周期日志
必须记录：
- 应用启动
- 应用关闭
- 核心配置加载摘要（不含敏感值）

### 2. 请求访问日志
必须通过中间件统一记录：
- method
- path
- status_code
- duration_ms
- request_id

### 3. 关键业务日志
建议优先覆盖：
- 用户注册成功/失败
- 用户登录成功/失败
- 密码修改成功/失败
- 查词请求发起/完成
- 翻译请求发起/完成
- 生词本操作
- AI 会话开始/完成（后续）

### 4. 外部调用日志
对于字典、翻译、AI provider 等外部调用，必须记录：
- provider 名称
- 调用目标摘要
- 耗时
- 成功/失败
- 失败原因摘要

### 5. 系统异常日志
必须记录：
- 异常类型
- traceback
- request_id
- 基础请求上下文

---

## 严禁记录的内容

以下内容禁止进入日志：
- 用户密码
- access token
- refresh token
- 第三方 API key / secret
- 数据库密码
- 完整 Authorization 头
- 未脱敏隐私数据
- 可直接复用的敏感凭据

### 脱敏要求
如确需输出用户标识信息，应优先记录：
- user_id
- 脱敏后的 email
- provider 名称
- 状态码与错误摘要

---

## FastAPI 集成要求

### 1. 启动阶段初始化日志
- 应在应用启动早期调用日志初始化
- 确保路由层、服务层、异常处理、访问中间件都进入统一日志体系

### 2. 异常处理集成
- 全局异常处理器必须与日志系统集成
- 系统异常保留 traceback
- 业务异常记录摘要，不滥打 traceback

### 3. Uvicorn 日志协调
- 统一 `uvicorn.error`、`uvicorn.access` 与项目日志风格
- 避免重复打印同一请求和同一异常
- 保持 formatter 风格一致

---

## 数据库与外部调用日志规范

### 数据库日志
要求：
- 默认不在 info 级别打印大量 SQL 明细
- 开发环境可通过配置项临时开启 SQL 调试
- 生产环境默认关闭详细 SQL 输出
- 数据库异常必须保留足够上下文用于排障

### 外部调用日志
要求：
- 记录 provider、耗时、结果和失败摘要
- 不记录密钥
- 不默认记录完整原始响应体
- 对失败日志保留最小必要上下文

---

## 文件日志与容器日志策略

当前阶段建议：
- 默认输出到 stdout/stderr
- 优先交由 Docker、systemd、日志平台进行收集

不建议第一阶段默认启用：
- 仅写文件不输出控制台
- 无轮转策略的本地文件日志

如果后续需要文件日志，必须满足：
- 支持轮转
- 支持大小或时间策略
- 支持与控制台日志协同配置

---

## 测试要求

日志系统必须具备基础可测试性。

至少应覆盖：
- 初始化逻辑
- 配置项驱动行为
- 上下文注入行为
- formatter 输出基本稳定性
- middleware 的 request_id 与 access log 行为

规范要求：
- 测试环境不得依赖生产日志配置
- 测试不应污染全局 logging 状态且不可恢复

---

## 第一阶段实施清单

### 目录与模块建设
- 建立 `app/core/logging/` 目录
- 创建 `__init__.py`
- 创建 `setup.py`
- 创建 `context.py`
- 创建 `formatters.py`
- 创建 `filters.py`
- 创建 `middleware.py`

### 基础能力建设
- 提供统一日志初始化入口
- 提供统一 `get_logger()` 接口
- 建立基础文本 formatter
- 建立基础上下文注入能力
- 建立基础请求日志中间件
- 在应用启动时接入日志初始化

### 项目接入改造
- 替换项目中的 `print()` 调试输出
- 禁止零散 `basicConfig()`
- 统一业务模块 logger 获取方式
- 将关键模块接入 logger

优先接入模块：
- `app/main.py`
- `app/api/v1/routes/auth.py`
- `app/services/*`
- `app/repositories/*`
- 全局异常处理链路

---

## 第二阶段实施清单

- 增加 JSON formatter
- 完善 request_id / user_id 上下文体系
- 增加敏感字段过滤能力
- 统一 uvicorn access/error 日志输出
- 细化外部调用日志规范

---

## 第三阶段实施清单

- 增加文件日志与轮转能力
- 接入日志平台（如 ELK / Loki / 云日志）
- 增加错误上报平台对接
- 评估 tracing / OpenTelemetry 集成

---

## 禁止事项

- 禁止将所有日志实现长期堆在单个文件中
- 禁止业务代码直接初始化 logging
- 禁止在业务代码中随意使用 `print()` 代替日志
- 禁止记录密码、token、密钥等敏感信息
- 禁止生产环境默认输出大量调试日志
- 禁止普通业务失败一律打印 traceback

---

## 验收标准

日志系统第一阶段完成后，应满足：
- 已建立 `app/core/logging/` 目录化结构
- 已明确各模块职责边界
- 全项目有统一的日志初始化入口与使用方式
- 关键模块已接入统一 logger
- 请求日志具备标准记录能力
- 异常日志与业务日志风格统一
- 日志中不包含明显敏感信息
- 为 JSON logging、日志平台接入、上下文扩展预留清晰结构
