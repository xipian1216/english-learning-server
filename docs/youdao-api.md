# Youdao API 接口文档

本文档基于 `<localFile name="README.md" path="/Users/xipian/workspace/english-learning/TranslateDemo/README.md" />`、`<localFile name="TranslateDemo.py" path="/Users/xipian/workspace/english-learning/TranslateDemo/apidemo/TranslateDemo.py" />` 与 `<localFile name="AuthV3Util.py" path="/Users/xipian/workspace/english-learning/TranslateDemo/apidemo/utils/AuthV3Util.py" />` 中的示例整理，面向 `english-learning-server` 后端集成有道智云翻译能力的场景。

说明：

- 本文档聚焦示例代码中已经明确展示的通用翻译接口。
- 本文档描述的是你后端调用有道开放平台的方式，而不是前端插件直接调用。
- 后端应统一封装有道接口，前端只调用你自己的服务接口。

## 1. 接口用途

该接口用于将输入文本从源语言翻译为目标语言，并支持携带用户词表 `vocabId`。

适合的后端场景：

- 查询单词或短句的基础翻译
- 为词条详情页补充中文释义
- 为例句生成目标语言翻译
- 在后端统一封装翻译能力，避免前端暴露第三方密钥

## 2. 上游接口信息

- Provider: Youdao 智云
- URL: `https://openapi.youdao.com/api`
- Method: `POST`
- Content-Type: `application/x-www-form-urlencoded`
- 签名版本: `v3`

## 3. 认证方式

有道接口需要使用以下凭证：

- `appKey`：应用 ID
- `appSecret`：应用密钥

凭证来源：

- 在有道智云控制台申请应用后获得

后端需要在请求参数中追加以下鉴权字段：

- `appKey`
- `salt`
- `curtime`
- `signType`
- `sign`

## 4. 请求参数

### 4.1 业务参数

根据示例代码，当前翻译接口至少包含以下业务参数：

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| q | string | 是 | 待翻译文本 |
| from | string | 是 | 源语言语种 |
| to | string | 是 | 目标语言语种 |
| vocabId | string | 否 | 用户词表 ID |

说明：

- `q` 可以是单词、短语或句子。
- `from` 与 `to` 的具体取值应以有道智云官方语言代码文档为准。
- `vocabId` 用于用户词表增强，如果当前业务不需要，可不传。

### 4.2 鉴权参数

根据示例代码中的 V3 签名逻辑，请求时还需要附加以下参数：

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| appKey | string | 是 | 应用 ID |
| salt | string | 是 | 随机字符串，示例中使用 UUID |
| curtime | string | 是 | 当前时间戳，单位秒 |
| signType | string | 是 | 固定为 `v3` |
| sign | string | 是 | 通过签名算法计算出的摘要 |

## 5. 签名算法

示例代码使用的是 V3 签名，计算方式为：

```text
sign = sha256(appKey + input(q) + salt + curtime + appSecret)
```

其中：

- `appKey`：应用 ID
- `q`：请求内容
- `salt`：随机值
- `curtime`：当前时间戳（秒）
- `appSecret`：应用密钥

### 5.1 input(q) 规则

示例代码中的 `input(q)` 规则如下：

- 当 `q` 长度小于等于 20 时：`input(q) = q`
- 当 `q` 长度大于 20 时：
  - 取前 10 个字符
  - 拼接总长度
  - 再拼接后 10 个字符

即：

```text
input(q) = q[0:10] + len(q) + q[-10:]
```

### 5.2 哈希算法

- 算法：`SHA-256`
- 输出：十六进制小写字符串

## 6. 上游请求示例

## 6.1 请求参数示例

```text
q=commit
from=en
to=zh-CHS
vocabId=your_vocab_id
appKey=your_app_key
salt=550e8400-e29b-41d4-a716-446655440000
curtime=1713000000
signType=v3
sign=calculated_sign_value
```

### 6.2 HTTP 请求示例

```http
POST /api HTTP/1.1
Host: openapi.youdao.com
Content-Type: application/x-www-form-urlencoded

q=commit&from=en&to=zh-CHS&vocabId=your_vocab_id&appKey=your_app_key&salt=550e8400-e29b-41d4-a716-446655440000&curtime=1713000000&signType=v3&sign=calculated_sign_value
```

## 7. 后端集成建议

对于 `english-learning-server`，建议不要让前端直接请求有道接口，而是采用以下架构：

- 插件前端请求你自己的后端接口
- 后端读取环境变量中的 `YOUDAO_APP_KEY` 与 `YOUDAO_APP_SECRET`
- 后端按 V3 规则生成签名
- 后端请求 `https://openapi.youdao.com/api`
- 后端解析响应并转换成你自己的统一结构
- 后端按需缓存结果到数据库

## 8. 推荐的后端封装方式

建议在你自己的服务中只暴露资源化接口，例如：

- `POST /api/v1/translations`
- `GET /api/v1/dictionary-entries/{id}`

其中：

- `POST /api/v1/translations` 用于创建一次翻译查询
- 如果查询结果需要长期复用，可进一步缓存为词条资源

这样可以保持你自己的 API 规范统一，而第三方调用细节全部封装在后端内部。

## 9. 推荐的内部请求字段映射

建议你后端内部统一抽象成以下输入：

| 内部字段 | 映射到有道字段 | 说明 |
| --- | --- | --- |
| text | q | 待翻译内容 |
| source_language | from | 源语言 |
| target_language | to | 目标语言 |
| vocab_id | vocabId | 用户词表 ID |

## 10. 推荐的内部响应结构

因为有道原始响应结构可能随着接口能力变化而扩展，你自己的后端最好统一整理成固定结构，例如：

```json
{
  "text": "commit",
  "source_language": "en",
  "target_language": "zh-CHS",
  "translations": [
    "承诺",
    "投入",
    "提交"
  ],
  "provider": "youdao",
  "raw": {}
}
```

说明：

- `raw` 可选，仅用于调试或内部追溯。
- 对前端返回时，建议不要直接暴露全部上游原始字段。

## 11. 环境变量建议

建议在后端项目中配置如下环境变量：

```env
YOUDAO_APP_KEY=
YOUDAO_APP_SECRET=
YOUDAO_BASE_URL=https://openapi.youdao.com/api
```

说明：

- 不要在代码中硬编码 `appKey` 与 `appSecret`
- 不要将密钥暴露给前端插件

## 12. 错误处理建议

后端调用有道接口时，建议至少处理以下几类错误：

- 凭证缺失
- 签名错误
- 上游接口超时
- 上游返回非成功状态
- 返回字段缺失或结构变化

建议在你自己的后端中统一转换为业务错误码，例如：

| 错误码 | 含义 |
| --- | --- |
| 50010 | 第三方翻译服务调用失败 |
| 50011 | 第三方翻译服务响应异常 |
| 40001 | 翻译请求参数非法 |

## 13. 当前适用范围

基于目前示例代码，这个有道接口更适合承担以下职责：

- 单词或句子的基础翻译
- 词条中文释义补充
- 例句中文翻译

不建议直接依赖它完成：

- 完整词典结构构建
- 个性化英语教师输出
- 学习型讲解或近义词辨析

对于这些更复杂能力，建议后续由：

- 词典 API
- 自建缓存表
- LLM 教学增强层

共同完成。

## 14. 当前落地建议

如果你当前要做“划词加入生词本 + 详情页展示”，可以这样使用有道接口：

1. 前端上传用户划词文本到你的后端
2. 后端先做词形归一与缓存查询
3. 如果本地词典缓存没有命中，则请求有道翻译接口补充基础中文翻译
4. 将翻译结果与词典数据合并后写入你的词条缓存表
5. 前端详情页展示你后端整理后的统一结果

这样能保证：

- 前端接口稳定
- 第三方服务可替换
- 后端可以做缓存与限流
- 后续容易增加 Oxford、Wordnik、OpenAI 等更多能力
