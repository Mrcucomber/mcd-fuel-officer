#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
程序员续命燃料官 · 麦当劳 MCP 客户端骨架 (mcd_fuel.py)

依赖:   仅用 Python 标准库 urllib（无需 pip install）
鉴权:   设置环境变量 MCD_MCP_TOKEN（从 https://open.mcd.cn/mcp 控制台获取）
运行:
    python3 mcd_fuel.py --help
    python3 mcd_fuel.py tools          # 列出麦当劳 MCP 全部工具
    python3 mcd_fuel.py demo           # 跑一次续命补给演示流程

说明:
    本脚本通过 Streamable HTTP 直连麦当劳中国 MCP Server (https://mcp.mcd.cn)，
    完成 initialize 握手后调用各 Tool。演示流程与 WorkBuddy 中实测的一致：
    now-time-info → query-nearby-stores → query-meals → list-nutrition-foods
    → query-store-coupons → available-coupons → calculate-price。
    工具名/参数以 `tools` 子命令实际返回的为准，如有出入请按真实值微调。
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.error

MCP_URL = "https://mcp.mcd.cn"
TOKEN = os.environ.get("MCD_MCP_TOKEN", "YOUR_MCP_TOKEN")


def _post(payload, session_id=None):
    """发送一次 JSON-RPC 请求，兼容普通 JSON 与 SSE(text/event-stream) 响应。"""
    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    if session_id:
        headers["Mcp-Session-Id"] = session_id
    req = urllib.request.Request(MCP_URL, data=data, headers=headers, method="POST")
    try:
        resp = urllib.request.urlopen(req, timeout=30)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "ignore")
        raise RuntimeError(f"HTTP {e.code}: {body[:500]}")
    ct = resp.headers.get("Content-Type", "")
    sid = resp.headers.get("Mcp-Session-Id")
    raw = resp.read().decode("utf-8", "ignore")

    messages = []
    if "text/event-stream" in ct:
        for block in raw.split("\n\n"):
            for line in block.splitlines():
                if line.startswith("data:"):
                    text = line[5:].strip()
                    if text:
                        messages.append(json.loads(text))
    else:
        if raw.strip():
            messages.append(json.loads(raw))
    return messages, sid


def _extract_text(msg):
    """从 tools/call 的 result.content 中抽取可读文本。"""
    res = msg.get("result") or {}
    content = res.get("content")
    if isinstance(content, list):
        out = [b.get("text", "") for b in content if b.get("type") == "text"]
        return "\n".join(out)
    return res


class McpClient:
    def __init__(self, name="mcd-fuel-officer"):
        self.session_id = None
        self._initialize(name)

    def _initialize(self, name):
        msgs, sid = _post({
            "jsonrpc": "2.0", "id": 0, "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": name, "version": "1.0.0"},
            },
        })
        self.session_id = sid
        _post({"jsonrpc": "2.0", "method": "notifications/initialized",
               "params": {}}, self.session_id)

    def _rpc(self, method, params=None, rid=1):
        msgs, _ = _post({
            "jsonrpc": "2.0", "id": rid, "method": method, "params": params or {},
        }, self.session_id)
        for m in msgs:
            if m.get("id") == rid:
                return m
        return msgs[-1] if msgs else {}

    def list_tools(self):
        return self._rpc("tools/list", {})

    def call_tool(self, name, args, rid=1):
        return self._rpc("tools/call", {"name": name, "arguments": args}, rid)


def cmd_tools():
    c = McpClient()
    r = c.list_tools()
    tools = (r.get("result") or {}).get("tools", [])
    print(f"共 {len(tools)} 个工具:")
    for t in tools:
        desc = (t.get("description") or "")[:60]
        print(f" - {t['name']}: {desc}")


def cmd_demo():
    c = McpClient()
    rid = 1

    print("== 1. now-time-info ==")
    m = c.call_tool("now-time-info", {}); rid += 1
    print(_extract_text(m))

    print("\n== 2. query-nearby-stores (上海张江, 得来速 beType=5) ==")
    m = c.call_tool("query-nearby-stores",
                    {"searchType": 2, "city": "上海", "keyword": "张江", "beType": 5}, rid); rid += 1
    print(_extract_text(m)[:600])

    print("\n== 3. query-meals (storeCode=1450218, beType=5) ==")
    m = c.call_tool("query-meals",
                    {"storeCode": "1450218", "beType": 5, "orderType": 1, "beCode": "145021841"}, rid); rid += 1
    print(_extract_text(m)[:600])

    print("\n== 4. list-nutrition-foods ==")
    m = c.call_tool("list-nutrition-foods", {}, rid); rid += 1
    print(_extract_text(m)[:600])

    print("\n== 5. query-store-coupons (storeCode=1450218, beType=5) ==")
    m = c.call_tool("query-store-coupons",
                    {"storeCode": "1450218", "beType": 5, "orderType": 1, "beCode": "145021841"}, rid); rid += 1
    print(_extract_text(m)[:600])

    print("\n== 6. available-coupons ==")
    m = c.call_tool("available-coupons", {}, rid); rid += 1
    print(_extract_text(m)[:600])

    print("\n== 7. calculate-price (演示组合) ==")
    # 演示用商品编码，请以 query-meals 返回为准微调
    m = c.call_tool("calculate-price", {
        "storeCode": "1450218", "beType": 5, "orderType": 1, "beCode": "145021841",
        "items": [
            {"productCode": "507411", "quantity": 1},
            {"productCode": "9900008751", "quantity": 1},
            {"productCode": "1100", "quantity": 1},
            {"productCode": "1401", "quantity": 1},
            {"productCode": "521741", "quantity": 1},
        ],
    }, rid); rid += 1
    print(_extract_text(m)[:600])


def main():
    p = argparse.ArgumentParser(description="程序员续命燃料官 · 麦当劳 MCP 客户端骨架")
    sub = p.add_subparsers(dest="cmd")
    sub.add_parser("tools", help="列出麦当劳 MCP 全部工具")
    sub.add_parser("demo", help="跑一次续命补给演示流程")
    args = p.parse_args()
    if args.cmd == "tools":
        cmd_tools()
    elif args.cmd == "demo":
        cmd_demo()
    else:
        p.print_help()


if __name__ == "__main__":
    main()
