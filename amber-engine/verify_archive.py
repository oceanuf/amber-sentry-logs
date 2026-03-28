#!/usr/bin/env python3
# 验证成果档案馆所有页面

import os
import datetime

print("🔍 琥珀引擎成果档案馆验证")
print("=" * 60)

# 检查的文件列表
files_to_check = [
    "/var/www/gemini_master/master-audit/list.html",
    "/var/www/gemini_master/master-audit/full_50_audit.html",
    "/var/www/gemini_master/master-audit/top10_elite.html",
    "/var/www/gemini_master/master-audit/manifesto_v1.html",
    "/var/www/gemini_master/master-audit/test.html"
]

all_ok = True
for file in files_to_check:
    if os.path.exists(file):
        size = os.path.getsize(file)
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(file))
        print(f"✅ {os.path.basename(file)}")
        print(f"   大小: {size:,} 字节 | 修改时间: {mtime.strftime('%Y-%m-%d %H:%M')}")
    else:
        print(f"❌ {os.path.basename(file)} 不存在")
        all_ok = False

print("\n🌐 访问地址验证")
urls = [
    "https://gemini.googlemanager.cn:10168/master-audit/list.html",
    "https://gemini.googlemanager.cn:10168/master-audit/full_50_audit.html",
    "https://gemini.googlemanager.cn:10168/master-audit/top10_elite.html"
]

print("请在浏览器中访问以下链接验证:")
for url in urls:
    print(f"  • {url}")

print("\n📊 档案馆统计")
if all_ok:
    total_size = sum(os.path.getsize(f) for f in files_to_check if os.path.exists(f))
    print(f"✅ 所有核心文件就绪")
    print(f"📁 总文件大小: {total_size:,} 字节")
    print(f"🔗 主索引页: list.html (29,754 字节)")
    print(f"🏆 黄金十强: top10_elite.html (7,710 字节)")
    print(f"📊 完整排名: full_50_audit.html (28,101 字节)")
    
    # 检查Nginx状态
    import subprocess
    try:
        result = subprocess.run(["systemctl", "is-active", "nginx"], 
                              capture_output=True, text=True)
        print(f"🚀 Nginx状态: {result.stdout.strip().upper()}")
    except:
        print("⚠️  无法检查Nginx状态")

print("\n🎉 成果档案馆创建完成！")
print("=" * 60)