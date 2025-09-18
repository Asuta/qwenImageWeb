#!/usr/bin/env python3
"""
简单的HTTP服务器启动脚本
用于解决CORS问题，让项目在本地HTTP服务器上运行
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path

# 设置端口
PORT = 8000

# 获取当前目录
current_dir = Path(__file__).parent.absolute()

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """支持CORS的HTTP请求处理器"""
    
    def end_headers(self):
        # 添加CORS头部
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()
    
    def do_OPTIONS(self):
        # 处理预检请求
        self.send_response(200)
        self.end_headers()

def start_server():
    """启动HTTP服务器"""
    try:
        # 切换到项目目录
        os.chdir(current_dir)
        
        # 创建服务器
        with socketserver.TCPServer(("", PORT), CORSHTTPRequestHandler) as httpd:
            print(f"🚀 服务器启动成功！")
            print(f"📁 服务目录: {current_dir}")
            print(f"🌐 访问地址: http://localhost:{PORT}")
            print(f"📱 主页面: http://localhost:{PORT}/index.html")
            print(f"🧪 测试页面: http://localhost:{PORT}/test-api.html")
            print(f"\n按 Ctrl+C 停止服务器")
            
            # 自动打开浏览器
            try:
                webbrowser.open(f'http://localhost:{PORT}/index.html')
                print(f"✅ 已自动打开浏览器")
            except:
                print(f"⚠️  请手动打开浏览器访问上述地址")
            
            # 启动服务器
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print(f"\n🛑 服务器已停止")
        sys.exit(0)
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ 端口 {PORT} 已被占用，请尝试其他端口")
            print(f"💡 可以修改脚本中的 PORT 变量")
        else:
            print(f"❌ 启动服务器失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("=" * 50)
    print("🎨 图像生成 AI 工具 - 本地服务器")
    print("=" * 50)
    start_server()
