#!/usr/bin/env python3
"""
启动图像生成AI工具
启动静态文件服务器
"""

import subprocess
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

def main():
    """主函数"""
    print("=" * 60)
    print("🎨 图像生成 AI 工具 - 简化启动")
    print("=" * 60)
    print()
    
    print("🚀 正在启动静态文件服务器...")
    
    try:
        # 启动静态文件服务器
        start_static_server()
        
        print("✅ 服务器启动完成！")
        print()
        print("📱 访问地址:")
        print("   主页面: http://localhost:8000/index.html")
        print("   测试页面: http://localhost:8000/test-api.html")
        print()
        print("💡 使用说明:")
        print("   1. 打开主页面开始使用")
        print("   2. 输入图像描述")
        print("   3. 可选择上传参考图片")
        print("   4. 调整高级参数")
        print("   5. 点击生成图像")
        print()
        print("按 Ctrl+C 停止服务器")
        
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
            print("\n🛑 服务器已停止")
            
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
