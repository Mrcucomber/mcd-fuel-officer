# 程序员续命燃料官（mcd-fuel-officer）

> 麦当劳中国 MCP 创意开发大赛 · 1024 程序员节参赛项目

面向 1024 程序员节的「续命补给规划」Skill。输入今晚肝代码到几点和目标（提神 / 抗饿 / 控热量），自动调用麦当劳 MCP 查询附近还在营业的门店与得来速、按营养目标筛选组合、匹配优惠券，输出带时间轴的最省续命补给计划。

## 能力
- 调用 `query-nearby-stores` 找附近营业 / 得来速门店与营业时间
- 调用 `query-meals` + `list-nutrition-foods` 按目标（提神/抗饿/控热量）筛组合并标注热量
- 调用 `query-store-coupons` / `available-coupons` 自动匹配最省券
- 输出带时间轴的续命补给计划：门店、花费、省了多少

## 目录
| 文件 | 说明 |
|---|---|
| `续命燃料官_补给计划.md` | 基于真实 MCP 数据生成的示例方案（上海·张江） |
| `mcp-config.example.json` | 脱敏配置示例（占位符，勿放真 Token） |
| `ISSUE_报名文案.md` | GitHub Issue 报名文案（替换用户名即可用） |
| `workbuddy.md` | WorkBuddy 开发对话上下文（积分核验文件，须官方导出覆盖） |
| `CONTEST_DECLARATION.md` | 参赛声明（官方原文，从大赛页获取，禁止修改） |
| `MCP_INTEGRATION.md` | MCP 使用说明（从大赛页获取） |
| `mcd_fuel.py` | 源代码（从大赛页获取 / 自行实现） |

## 配置
1. 复制 `mcp-config.example.json` 为 `mcp.json`，将 `YOUR_MCP_TOKEN` 换成 open.mcd.cn/mcp 控制台获取的 Token；
2. 在 WorkBuddy 连接器页「自定义连接器」信任 `mcd-mcp`。

## 运行（参考）
```bash
pip install requests
export MCD_MCP_TOKEN="你的真实Token"
python3 mcd_fuel.py tools   # 列出麦当劳 MCP 全部工具
python3 mcd_fuel.py demo    # 跑一次续命补给演示流程
```
