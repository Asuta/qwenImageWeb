#!/usr/bin/env python3
"""
启动完整的图像生成AI工具
同时启动静态文件服务器和CORS代理服务器
"""

import subprocess
import threading
import time
import webbrowser
import sys
import os
from pathlib import Path

# 获取当前目录
current_dir = Path(__file__).parent.absolute()

def start_static_server():
    """启动静态文件服务器"""
    try:
        os.chdir(current_dir)
        subprocess.run([
            sys.executable, "start-server.py"
        ], check=True)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"静态服务器错误: {e}")

def start_proxy_server():
    """启动代理服务器"""
    try:
        os.chdir(current_dir)
        subprocess.run([
            sys.executable, "proxy-server.py"
        ], check=True)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"代理服务器错误: {e}")

def main():
    """主函数"""
    print("=" * 60)
    print("🎨 图像生成 AI 工具 - 完整启动")
    print("=" * 60)
    print()
    
    try:
        # 创建线程启动两个服务器
        static_thread = threading.Thread(target=start_static_server, daemon=True)
        proxy_thread = threading.Thread(target=start_proxy_server, daemon=True)
        
        print("🚀 正在启动服务器...")
        
        # 启动静态文件服务器
        static_thread.start()
        time.sleep(2)  # 等待静态服务器启动
        
        # 启动代理服务器
        proxy_thread.start()
        time.sleep(2)  # 等待代理服务器启动
        
        print("✅ 服务器启动完成！")
        print()
        print("📱 访问地址:")
        print("   主页面: http://localhost:8000/index.html")
        print("   测试页面: http://localhost:8000/test-api.html")
        print()
        print("🔧 服务器信息:")
        print("   静态文件服务器: http://localhost:8000")
        print("   CORS代理服务器: http://localhost:8001")
        print()
        print("💡 使用说明:")
        print("   1. 打开主页面开始使用")
        print("   2. 输入图像描述")
        print("   3. 可选择上传参考图片")
        print("   4. 调整高级参数")
        print("   5. 点击生成图像")
        print()
        print("按 Ctrl+C 停止所有服务器")
        
        # 自动打开浏览器
        try:
            webbrowser.open('http://localhost:8000/index.html')
            print("✅ 已自动打开浏览器")
        except:
            print("⚠️  请手动打开浏览器访问上述地址")
        
        print()
        
        # 保持主线程运行
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 正在停止服务器...")
            
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
