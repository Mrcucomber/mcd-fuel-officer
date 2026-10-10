# MCP 使用说明 · 程序员续命燃料官

## 一、接入的 MCP Server
- **名称**：麦当劳中国 MCP Server（mcd-mcp）
- **地址**：`https://mcp.mcd.cn`
- **传输协议**：Streamable HTTP（WorkBuddy 配置中 `type: "http"`）
- **鉴权**：`Authorization: Bearer <MCP_TOKEN>`，Token 从 [open.mcd.cn/mcp](https://open.mcd.cn/mcp) 控制台获取
- **配置示例**：见同目录 `mcp-config.example.json`（仅占位符，不含真实 Token）

## 二、实际调用的 Tool 清单
| Tool | 用途 | 关键参数 |
|---|---|---|
| `now-time-info` | 取当前时间，作为补给时间轴基准 | 无 |
| `query-nearby-stores` | 查附近「得来速」门店及营业时间 | `beType=5`（得来速）, `city`, `keyword` |
| `query-meals` | 取指定门店实时菜单与现价 | `storeCode`, `beType=5`, `orderType=1` |
| `list-nutrition-foods` | 取营养成分，按目标（提神/抗饿/控热量）筛组合并标注热量 | 无 |
| `query-store-coupons` | 查指定门店可用券 | `storeCode`, `beType=5`, `orderType=1` |
| `available-coupons` | 查账户可领券，自动匹配最省方案 | 无 |
| `calculate-price` | 校验组合现价，输出原价/到手价 | `storeCode`, `beType=5`, `orderType=1`, `items:[{productCode,quantity}]` |

## 三、调用流程（与 WorkBuddy 实测一致）
1. `now-time-info` 取当前时间 → 确定时间轴起点；
2. `query-nearby-stores`（beType=5）找附近营业/得来速门店 → 选目标门店（如上海秀沿路得来速 `1450218`）；
3. `query-meals` 取该店菜单现价；
4. `list-nutrition-foods` 按目标筛组合并标注热量；
5. `query-store-coupons` + `available-coupons` 匹配最省券；
6. `calculate-price` 计算到手价；
7. 汇总输出带时间轴的「续命补给计划」（门店 / 花费 / 省了多少）。

## 四、业务价值
面向 1024 程序员节，把"今晚肝到几点 + 目标（提神/抗饿/控热量）"转化为一份带时间轴、带门店、带省钱方案的续命补给计划；真实调用麦当劳 MCP 的门店/菜单/营养/优惠券/计价能力，避免凭空编造餐品与价格。

## 五、关键约束（来自真实数据）
- 门店营业时间以 MCP 实时返回为准（如张江附近得来速最晚 23:00 打烊，无通宵店，补给须打烊前备齐）；
- 餐品、价格、优惠券、供应状态以麦当劳官方渠道实时结果为准，本 Skill 输出仅供参考。
