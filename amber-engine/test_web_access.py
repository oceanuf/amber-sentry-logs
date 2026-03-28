#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Web访问
"""

import os
import http.server
import socketserver
import threading
import time
import urllib.request
import urllib.error

def start_test_server(port=8080):
    """启动测试HTTP服务器"""
    os.chdir("/home/luckyelite/.openclaw/workspace/amber-engine")
    
    handler = http.server.SimpleHTTPRequestHandler
    
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"✅ 测试HTTP服务器启动在端口 {port}")
        print(f"📁 服务目录: {os.getcwd()}")
        print(f"🌐 测试URL: http://localhost:{port}/master-audit/dragon_tiger_top20.html")
        
        # 在后台运行服务器
        server_thread = threading.Thread(target=httpd.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        # 等待服务器启动
        time.sleep(2)
        
        # 测试访问
        try:
            response = urllib.request.urlopen(f"http://localhost:{port}/master-audit/dragon_tiger_top20.html")
            if response.status == 200:
                print("✅ 龙虎榜页面可正常访问")
                return True
            else:
                print(f"⚠️ 页面访问返回状态码: {response.status}")
                return False
        except urllib.error.URLError as e:
            print(f"❌ 页面访问失败: {e}")
            return False
        except Exception as e:
            print(f"❌ 未知错误: {e}")
            return False

def check_existing_service():
    """检查现有服务"""
    print("🔍 检查现有Web服务...")
    
    # 检查10168端口
    try:
        response = urllib.request.urlopen("http://localhost:10168/", timeout=5)
        print(f"✅ 10168端口有服务运行，状态码: {response.status}")
        return True
    except urllib.error.URLError:
        print("❌ 10168端口无服务响应")
        return False
    except Exception as e:
        print(f"⚠️ 检查10168端口时出错: {e}")
        return False

if __name__ == "__main__":
    print("🧪 开始Web访问测试...")
    
    # 首先检查现有服务
    if not check_existing_service():
        print("📢 启动测试服务器进行验证...")
        if start_test_server(8080):
            print("\n🎉 测试完成！页面可正常访问")
            print("💡 建议：")
            print("   1. 确保10168端口有HTTP服务器运行")
            print("   2. 将master-audit目录设置为Web可访问")
            print("   3. 验证 https://gemini.googlemanager.cn:10168/master-audit/dragon_tiger_top20.html")
        else:
            print("\n❌ 测试失败，请检查文件路径和权限")
    else:
        print("\n✅ 现有服务正常，请直接访问目标URL")