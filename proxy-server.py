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
            
            print(f"Received request: {json.dumps(request_data, indent=2)}")
            
            # 构建发送到NanoGPT API的请求
            api_url = f"{NANOGPT_API_BASE}/v1/images/generations"
            
            # 准备请求头
            headers = {
                'Authorization': f'Bearer {API_KEY}',
                'Content-Type': 'application/json',
                'User-Agent': 'CORS-Proxy/1.0'
            }
            
            # 准备请求数据
            api_request_data = json.dumps(request_data).encode('utf-8')
            
            # 创建请求
            req = urllib.request.Request(
                api_url,
                data=api_request_data,
                headers=headers,
                method='POST'
            )
            
            print(f"Sending request to: {api_url}")
            print(f"Request headers: {headers}")
            
            # 发送请求
            try:
                with urllib.request.urlopen(req, timeout=120) as response:
                    response_data = response.read()
                    response_json = json.loads(response_data.decode('utf-8'))
                    
                    print(f"API Response: {json.dumps(response_json, indent=2)}")
                    
                    # 发送成功响应
                    self.send_response(200)
                    self._set_cors_headers()
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    
                    self.wfile.write(response_data)
                    
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
