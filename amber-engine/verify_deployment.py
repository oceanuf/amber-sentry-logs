#!/usr/bin/env python3
# 验证Web部署

import os
import subprocess

print("🔍 验证Web部署状态")
print("=" * 50)

# 检查文件是否存在
files_to_check = [
    "/var/www/gemini_master/master-audit/full_50_audit.html",
    "/var/www/gemini_master/master-audit/top10_elite.html"
]

for file in files_to_check:
    if os.path.exists(file):
        size = os.path.getsize(file)
        lines = sum(1 for _ in open(file, 'r', encoding='utf-8'))
        print(f"✅ {file}")
        print(f"   大小: {size} 字节, 行数: {lines}")
        
        # 检查关键内容
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
            if "黄金十强" in content or "ETF综合排名" in content:
                print(f"   内容验证: 包含排名数据")
            if "V1.1.1-ELITE" in content:
                print(f"   版本验证: V1.1.1-ELITE")
    else:
        print(f"❌ {file} 不存在")

print("\n🌐 检查Web服务状态")
try:
    # 检查Nginx状态
    result = subprocess.run(["systemctl", "is-active", "nginx"], 
                          capture_output=True, text=True)
    print(f"Nginx状态: {result.stdout.strip()}")
    
    # 检查端口监听
    result = subprocess.run(["ss", "-tlnp"], capture_output=True, text=True)
    if ":10168" in result.stdout:
        print("✅ 端口10168正在监听")
    else:
        print("⚠️  端口10168未找到")
        
except Exception as e:
    print(f"检查失败: {e}")

print("\n📊 文件内容摘要:")
with open("/var/www/gemini_master/master-audit/full_50_audit.html", 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines[:30]):
        if "平安新能车ETF" in line or "排名" in line or "<tr>" in line:
            print(f"行{i+1}: {line.strip()[:80]}...")

print("\n✅ 验证完成")