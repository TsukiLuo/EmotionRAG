"""
本地 Mock Server - 模拟 /v1/agent/analyze 接口
用途：在 Apifox 本地客户端未运行时，提供相同的 Mock 响应
运行：python3 mock_server.py
端口：4523（与 Apifox 本地 Mock 端口一致）
"""

import json
import random
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# 模拟响应数据池
MOCK_RESPONSES = [
    {
        "code": 200,
        "msg": "success",
        "data": {
            "analysis": {
                "image_emotion": {
                    "dominant_emotion": "sadness",
                    "au12_r_smile_intensity": 0.2,
                    "au04_r_brow_lower": 1.8,
                },
                "text_sentiment": "negative",
                "text_keywords": ["焦虑", "压力"],
            },
            "decision": "need_knowledge",
            "reply": "听起来你有些焦虑，这是很常见的情绪。研究表明，适度运动可以有效缓解焦虑情绪。",
            "advice_source": "从知识库检索到的心理学论文摘要",
        },
    },
    {
        "code": 200,
        "msg": "success",
        "data": {
            "analysis": {
                "image_emotion": {
                    "dominant_emotion": "happiness",
                    "au12_r_smile_intensity": 2.5,
                    "au04_r_brow_lower": 0.1,
                },
                "text_sentiment": "positive",
                "text_keywords": ["开心", "满足"],
            },
            "decision": "general_chat",
            "reply": "看到你心情不错，继续保持积极的心态！研究表明，记录每天三件感恩的事能显著提升幸福感。",
            "advice_source": "从知识库检索到的积极心理学研究",
        },
    },
    {
        "code": 200,
        "msg": "success",
        "data": {
            "analysis": {
                "image_emotion": {
                    "dominant_emotion": "neutral",
                    "au12_r_smile_intensity": 0.5,
                    "au04_r_brow_lower": 0.3,
                },
                "text_sentiment": "neutral",
                "text_keywords": ["平静", "日常"],
            },
            "decision": "no_need",
            "reply": "你的情绪看起来比较平稳，这是一种很好的状态。如果需要聊天，我随时在这里。",
            "advice_source": "",
        },
    },
]


class MockHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        parsed = urlparse(self.path)

        # 匹配 /v1/agent/analyze 或 /m1/.../v1/agent/analyze
        if "/v1/agent/analyze" in parsed.path:
            # 随机选一个响应
            response = random.choice(MOCK_RESPONSES)
            self._send_json(200, response)
        else:
            self._send_json(404, {"code": 404, "msg": "not found", "data": None})

    def do_GET(self):
        """健康检查"""
        self._send_json(200, {"status": "ok", "msg": "Mock server is running"})

    def _send_json(self, status, body):
        body_bytes = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body_bytes)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()
        self.wfile.write(body_bytes)

    def do_OPTIONS(self):
        """处理 CORS 预检请求"""
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def log_message(self, format, *args):
        print(f"[Mock] {args[0]}")


if __name__ == "__main__":
    PORT = 4523
    server = HTTPServer(("0.0.0.0", PORT), MockHandler)
    print(f"🎭 Mock Server 运行在 http://127.0.0.1:{PORT}")
    print(f"   接口地址: http://127.0.0.1:{PORT}/m1/8571821-8348753-default/v1/agent/analyze")
    print(f"   按 Ctrl+C 停止")
    server.serve_forever()
