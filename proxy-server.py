#!/usr/bin/env python3
"""
CORS代理服务器
用于解决前端调用NanoGPT API时的跨域问题
"""

import http.server
import socketserver
import json
import urllib.request
import urllib.parse
import urllib.error
from urllib.parse import urlparse, parse_qs
import webbrowser
import os
import sys
from pathlib import Path
import concurrent.futures

# 设置端口
PORT = 8001
STATIC_PORT = 8000

# NanoGPT API配置
NANOGPT_API_BASE = "https://nano-gpt.com"
API_KEY = "c4deaf5a-eedd-4138-94e2-e2e6e299a22d"

class CORSProxyHandler(http.server.BaseHTTPRequestHandler):
    """支持CORS的代理请求处理器"""
    
    def _set_cors_headers(self):
        """设置CORS头部"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
        self.send_header('Access-Control-Max-Age', '86400')
    
    def do_OPTIONS(self):
        """处理预检请求"""
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()
    
    def do_POST(self):
        """处理POST请求"""
        try:
            # 解析请求路径
            parsed_path = urlparse(self.path)
            
            if parsed_path.path == '/api/images/generations':
                self._handle_image_generation()
            else:
                self._send_error(404, "API endpoint not found")
                
        except Exception as e:
            print(f"Error handling POST request: {e}")
            self._send_error(500, f"Internal server error: {str(e)}")
    
    def _handle_image_generation(self):
        """处理图像生成请求"""
        try:
            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # 解析JSON数据
            try:
                request_data = json.loads(post_data.decode('utf-8'))
            except json.JSONDecodeError as e:
                self._send_error(400, f"Invalid JSON: {str(e)}")
                return
            
            # 检查是否包含图片数据
            has_image_data = False
            image_info = []

            if 'imageDataUrl' in request_data:
                has_image_data = True
                image_info.append(f"imageDataUrl: {len(request_data['imageDataUrl'])} 字符")

            if 'imageDataUrls' in request_data:
                has_image_data = True
                image_info.append(f"imageDataUrls: {len(request_data['imageDataUrls'])} 张图片")
                for i, img in enumerate(request_data['imageDataUrls']):
                    image_info.append(f"  图片{i+1}: {len(img)} 字符")

            if 'maskDataUrl' in request_data:
                has_image_data = True
                image_info.append(f"maskDataUrl: {len(request_data['maskDataUrl'])} 字符")

            print("=" * 60)
            print(f"📥 收到API请求:")
            print(f"模型: {request_data.get('model', 'N/A')}")
            print(f"提示词: {request_data.get('prompt', 'N/A')[:50]}...")
            print(f"图片数量: {request_data.get('n', 'N/A')}")
            print(f"尺寸: {request_data.get('size', 'N/A')}")

            if has_image_data:
                print("🖼️  包含图片数据:")
                for info in image_info:
                    print(f"   {info}")
            else:
                print("❌ 未包含图片数据")

            print("=" * 60)
            
            # 构建发送到NanoGPT API的请求
            api_url = f"{NANOGPT_API_BASE}/v1/images/generations"

            # 目标数量（兼容多种字段）
            desired_n = request_data.get('n') or request_data.get('num_images') or request_data.get('numImages') or 1
            try:
                desired_n = int(desired_n)
            except Exception:
                desired_n = 1

            # 准备请求头
            headers = {
                'Authorization': f'Bearer {API_KEY}',
                'Content-Type': 'application/json',
                'User-Agent': 'CORS-Proxy/1.0'
            }

            def call_upstream(single_payload):
                payload_bytes = json.dumps(single_payload).encode('utf-8')
                req = urllib.request.Request(
                    api_url,
                    data=payload_bytes,
                    headers=headers,
                    method='POST'
                )
                with urllib.request.urlopen(req, timeout=120) as resp:
                    raw = resp.read()
                    return json.loads(raw.decode('utf-8'))

            print(f"Sending request to: {api_url}")
            print(f"Request headers: {headers}")

            try:
                if desired_n <= 1:
                    # 直接转发一次
                    upstream_resp = call_upstream(request_data)
                    print(f"API Response: {json.dumps(upstream_resp, indent=2)}")

                    self.send_response(200)
                    self._set_cors_headers()
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(upstream_resp).encode('utf-8'))
                else:
                    # 上游可能不支持批量：并发 fan-out 聚合
                    print(f"Fan-out to upstream for {desired_n} images ...")
                    base_payload = dict(request_data)
                    base_payload['n'] = 1
                    base_payload['nImages'] = 1
                    base_payload['numImages'] = 1

                    tasks = [dict(base_payload) for _ in range(desired_n)]
                    results = []
                    errors = []
                    with concurrent.futures.ThreadPoolExecutor(max_workers=min(4, desired_n)) as executor:
                        futures = [executor.submit(call_upstream, t) for t in tasks]
                        for f in concurrent.futures.as_completed(futures):
                            try:
                                results.append(f.result())
                            except Exception as ex:
                                errors.append(str(ex))

                    # 聚合 data
                    combined = {
                        'data': [],
                    }
                    total_cost = 0.0
                    last_balance = None
                    for r in results:
                        if isinstance(r, dict):
                            if isinstance(r.get('data'), list):
                                combined['data'].extend(r['data'])
                            # 可选费用字段
                            if isinstance(r.get('cost'), (int, float)):
                                total_cost += float(r['cost'])
                            if r.get('remainingBalance') is not None:
                                last_balance = r.get('remainingBalance')

                    if total_cost:
                        combined['cost'] = total_cost
                    if last_balance is not None:
                        combined['remainingBalance'] = last_balance
                    if errors:
                        combined['warnings'] = {'partialErrors': errors}

                    print(f"Aggregated {len(combined['data'])} images from {len(results)} upstream calls")

                    self.send_response(200)
                    self._set_cors_headers()
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(combined).encode('utf-8'))

            except urllib.error.HTTPError as e:
                error_data = e.read().decode('utf-8')
                print(f"API Error {e.code}: {error_data}")
                
                try:
                    error_json = json.loads(error_data)
                    self._send_json_error(e.code, error_json.get('message', 'API request failed'))
                except json.JSONDecodeError:
                    self._send_error(e.code, f"API request failed: {error_data}")
                    
            except urllib.error.URLError as e:
                print(f"Network Error: {e}")
                self._send_error(503, f"Network error: {str(e)}")
                
            except Exception as e:
                print(f"Unexpected error: {e}")
                self._send_error(500, f"Unexpected error: {str(e)}")
                
        except Exception as e:
            print(f"Error in _handle_image_generation: {e}")
            self._send_error(500, f"Internal server error: {str(e)}")
    
    def _send_error(self, code, message):
        """发送错误响应"""
        self.send_response(code)
        self._set_cors_headers()
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        error_response = {
            'error': code,
            'message': message
        }
        
        self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def _send_json_error(self, code, message):
        """发送JSON格式的错误响应"""
        self.send_response(code)
        self._set_cors_headers()
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        error_response = {
            'error': code,
            'message': message
        }
        
        self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        print(f"[{self.date_time_string()}] {format % args}")

def start_proxy_server():
    """启动代理服务器"""
    try:
        with socketserver.TCPServer(("", PORT), CORSProxyHandler) as httpd:
            print(f"🚀 CORS代理服务器启动成功！")
            print(f"🌐 代理地址: http://localhost:{PORT}")
            print(f"📡 API端点: http://localhost:{PORT}/api/images/generations")
            print(f"🎯 目标API: {NANOGPT_API_BASE}")
            print(f"🔑 API密钥: {API_KEY[:20]}...")
            print(f"\n按 Ctrl+C 停止服务器")
            
            # 启动服务器
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print(f"\n🛑 代理服务器已停止")
        sys.exit(0)
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ 端口 {PORT} 已被占用，请尝试其他端口")
            print(f"💡 可以修改脚本中的 PORT 变量")
        else:
            print(f"❌ 启动代理服务器失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("=" * 60)
    print("🔄 NanoGPT API CORS 代理服务器")
    print("=" * 60)
    start_proxy_server()
