#!/usr/bin/env python3
"""
检查博物馆页面所有链接的可访问性
"""

import subprocess
import os

BASE_URL = "https://localhost:10168/master-audit/"

# 从页面提取的链接
links = [
    "algorithm_version_history.html",
    "bronze_algorithm_dashboard.html", 
    "bronze_codex_standard.html",
    "bronze_etf_details.html",  # 这个我们知道有问题
    "dual_algorithm_comparison.html",
    "full_50_audit.html",
    "global_dragon_tiger_latest.html",
    "star_algorithm_dashboard.html",
    "star_etf_details.html",
    "star_gravity_standard.html",
    "tonight_launch_countdown.html",
    "top10_elite.html"
]

def check_link(link):
    """检查单个链接的可访问性"""
    url = BASE_URL + link
    
    result = subprocess.run(
        ['curl', '-k', '-s', '-o', '/dev/null', '-w', '%{http_code}', url],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    status = result.stdout.strip()
    
    if status == '200':
        return True, status
    else:
        # 尝试获取更多信息
        result2 = subprocess.run(
            ['curl', '-k', '-s', '-I', url],
            capture_output=True,
            text=True,
            timeout=5
        )
        return False, status

def check_file_exists(link):
    """检查文件在文件系统中是否存在"""
    file_path = f"/var/www/gemini_master/master-audit/{link}"
    
    if os.path.exists(file_path):
        # 检查是否是符号链接
        if os.path.islink(file_path):
            target = os.readlink(file_path)
            return True, f"符号链接 → {target}"
        else:
            return True, "物理文件"
    else:
        return False, "文件不存在"

def main():
    print("=" * 70)
    print("🏛️  博物馆页面链接检查报告")
    print("=" * 70)
    
    print("\n📋 检查以下链接的可访问性:")
    for link in links:
        print(f"  • {link}")
    
    print("\n🔍 开始检查...")
    
    results = []
    
    for link in links:
        # 检查HTTP访问
        accessible, status = check_link(link)
        
        # 检查文件系统
        exists, file_info = check_file_exists(link)
        
        results.append({
            'link': link,
            'accessible': accessible,
            'status': status,
            'exists': exists,
            'file_info': file_info
        })
    
    # 打印结果
    print("\n" + "=" * 70)
    print("📊 检查结果汇总")
    print("=" * 70)
    
    for result in results:
        if result['accessible']:
            print(f"✅ {result['link']:35} HTTP {result['status']} | {result['file_info']}")
        else:
            print(f"❌ {result['link']:35} HTTP {result['status']} | {result['file_info']}")
    
    # 特殊处理已知问题
    print("\n" + "=" * 70)
    print("🔧 需要修复的链接")
    print("=" * 70)
    
    need_fix = []
    for result in results:
        if not result['accessible']:
            need_fix.append(result['link'])
    
    if need_fix:
        for link in need_fix:
            print(f"⚠️  {link}")
            
            # 特殊处理 bronze_etf_details.html
            if link == "bronze_etf_details.html":
                print("    已知问题: JavaScript版本有问题")
                print("    解决方案: 已创建静态版本 bronze_static_final.html")
                print("    替代链接: bronze_static_final.html")
    else:
        print("✅ 所有链接都可访问")
    
    # 检查详情页链接
    print("\n" + "=" * 70)
    print("🔗 详情页链接验证")
    print("=" * 70)
    
    # 检查 bronze_etf_details.html 的替代方案
    static_alternatives = [
        "bronze_static_final.html",
        "bronze_details/bronze_static_final.html"
    ]
    
    for alt in static_alternatives:
        url = BASE_URL + alt
        result = subprocess.run(
            ['curl', '-k', '-s', '-o', '/dev/null', '-w', '%{http_code}', url],
            capture_output=True,
            text=True,
            timeout=5
        )
        status = result.stdout.strip()
        
        if status == '200':
            print(f"✅ 静态替代方案: {alt:30} HTTP {status}")
        else:
            print(f"❌ 静态替代方案: {alt:30} HTTP {status}")
    
    # 提供修复建议
    print("\n" + "=" * 70)
    print("💡 修复建议")
    print("=" * 70)
    
    print("1. bronze_etf_details.html 问题:")
    print("   - 当前状态: JavaScript版本有问题")
    print("   - 解决方案: 更新链接到静态版本")
    print("   - 建议: 将 bronze_etf_details.html 改为 bronze_static_final.html")
    
    print("\n2. 其他链接检查:")
    print("   - 确认所有文件都存在且权限正确")
    print("   - 确保符号链接目标有效")
    print("   - 测试所有链接在浏览器中的可点击性")
    
    # 生成修复脚本
    generate_fix_script(need_fix)

def generate_fix_script(need_fix):
    """生成修复脚本"""
    print("\n" + "=" * 70)
    print("🛠️  自动修复脚本")
    print("=" * 70)
    
    script = '''#!/bin/bash
# 博物馆页面链接修复脚本

echo "🔧 开始修复博物馆页面链接..."

# 备份原始文件
BACKUP_FILE="/var/www/gemini_master/master-audit/list.html.backup"
sudo cp /var/www/gemini_master/master-audit/list.html "$BACKUP_FILE"
echo "📁 备份创建: $BACKUP_FILE"

# 修复 bronze_etf_details.html 链接
echo "🔄 修复 bronze_etf_details.html 链接..."
sudo sed -i 's|href="bronze_etf_details.html"|href="bronze_static_final.html"|g' /var/www/gemini_master/master-audit/list.html
sudo sed -i 's|href='\\''bronze_etf_details.html'\\''|href='\\''bronze_static_final.html'\\''|g' /var/www/gemini_master/master-audit/list.html

echo "✅ 修复完成"
echo "🌐 请访问: https://gemini.googlemanager.cn:10168/master-audit/list.html"
'''
    
    script_file = "/home/luckyelite/.openclaw/workspace/amber-engine/fix_museum_links.sh"
    with open(script_file, 'w') as f:
        f.write(script)
    
    os.chmod(script_file, 0o755)
    print(f"📜 修复脚本已生成: {script_file}")
    print(f"🚀 执行命令: sudo bash {script_file}")

if __name__ == "__main__":
    main()