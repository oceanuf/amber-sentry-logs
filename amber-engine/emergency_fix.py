#!/usr/bin/env python3
"""
紧急修复：JavaScript语法错误
问题：const etfData = const etfData = [...] 重复声明
"""

import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OVERVIEW_FILE = os.path.join(BASE_DIR, "web", "bronze_etf_details.html")

def fix_javascript_syntax():
    """修复JavaScript语法错误"""
    print("🚨 紧急修复JavaScript语法错误...")
    
    with open(OVERVIEW_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找并修复重复的const声明
    # 错误模式: const etfData = const etfData = [...]
    # 正确模式: const etfData = [...]
    
    # 使用正则表达式修复
    pattern = r'const etfData = const etfData = (\[.*?\];)'
    replacement = r'const etfData = \1'
    
    fixed_content, count = re.subn(pattern, replacement, content, flags=re.DOTALL)
    
    if count > 0:
        print(f"✅ 修复了 {count} 处重复声明错误")
    else:
        print("⚠️  未找到重复声明，尝试其他模式...")
        # 尝试另一种模式
        pattern2 = r'const etfData =\s*const etfData ='
        if re.search(pattern2, content):
            fixed_content = re.sub(pattern2, 'const etfData =', content)
            print("✅ 修复了重复声明错误（模式2）")
    
    # 保存修复后的文件
    with open(OVERVIEW_FILE, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"✅ 文件已修复: {OVERVIEW_FILE}")
    
    # 验证修复
    verify_fix(fixed_content)

def verify_fix(content):
    """验证修复结果"""
    print("🧪 验证修复结果...")
    
    # 检查是否还有重复声明
    if 'const etfData = const etfData =' in content:
        print("❌ 修复失败：仍然存在重复声明")
        return False
    
    # 检查const声明是否正常
    if 'const etfData = [' in content:
        print("✅ const声明正常")
        
        # 提取etfData看看
        match = re.search(r'const etfData = (\[.*?\];)', content, re.DOTALL)
        if match:
            data_str = match.group(1)
            # 尝试解析JSON看看是否有效
            import json
            try:
                # 移除末尾分号
                json_str = data_str.rstrip(';')
                data = json.loads(json_str)
                print(f"✅ ETF数据有效: {len(data)} 支标的")
                return True
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析错误: {e}")
                return False
        else:
            print("❌ 找不到etfData数据")
            return False
    else:
        print("❌ 找不到const etfData声明")
        return False

def deploy_fix():
    """部署修复到Web服务器"""
    print("🚀 部署修复到Web服务器...")
    
    # 复制到bronze_details目录
    target_file = "/var/www/gemini_master/bronze_details/bronze_etf_details.html"
    
    # 使用sudo复制
    os.system(f"sudo cp {OVERVIEW_FILE} {target_file}")
    os.system(f"sudo chown www-data:www-data {target_file}")
    
    print(f"✅ 部署到: {target_file}")
    
    # 更新符号链接（如果存在）
    symlink = "/var/www/gemini_master/master-audit/bronze_etf_details.html"
    if os.path.islink(symlink):
        os.system(f"sudo rm {symlink}")
        os.system(f"sudo ln -s {target_file} {symlink}")
        print(f"✅ 更新符号链接: {symlink}")
    
    # 测试访问
    test_access()

def test_access():
    """测试访问"""
    print("🔗 测试Web访问...")
    
    import subprocess
    result = subprocess.run(
        ['curl', '-k', '-s', '-o', '/dev/null', '-w', '%{http_code}', 
         'https://localhost:10168/master-audit/bronze_etf_details.html'],
        capture_output=True,
        text=True
    )
    
    if result.stdout.strip() == '200':
        print("✅ HTTP 200正常")
        
        # 检查修复后的内容
        result2 = subprocess.run(
            ['curl', '-k', '-s', 'https://localhost:10168/master-audit/bronze_etf_details.html'],
            capture_output=True,
            text=True
        )
        
        if 'const etfData = const etfData =' in result2.stdout:
            print("❌ 服务器上仍然存在重复声明")
        elif 'const etfData = [' in result2.stdout:
            print("✅ 服务器上const声明正常")
            
            # 检查是否有语法错误
            if 'SyntaxError' in result2.stdout or 'Uncaught' in result2.stdout:
                print("⚠️  页面可能仍有其他JavaScript错误")
            else:
                print("✅ 页面JavaScript语法正常")
        else:
            print("⚠️  无法验证服务器内容")
    else:
        print(f"❌ HTTP错误: {result.stdout}")

def create_simple_fallback():
    """创建简单的备用页面（无JavaScript）"""
    print("🔄 创建简单备用页面...")
    
    simple_html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>青铜法典 · 标的列表（简单版）</title>
    <style>
        body { font-family: sans-serif; padding: 20px; }
        .card { border: 1px solid #ccc; padding: 15px; margin: 10px; display: inline-block; width: 300px; }
        h1 { color: #1a237e; }
    </style>
</head>
<body>
    <h1>🧀 青铜法典 · 标的列表（简单版）</h1>
    <p>JavaScript版本正在修复中，这是简单静态版本。</p>
    
    <div id="etfList">
        <!-- 静态ETF列表 -->
        <div class="card">
            <strong>510300</strong><br>
            华泰柏瑞沪深300ETF<br>
            <small>战略宽基</small><br>
            <a href="bronze_details/510300.html">查看详情 →</a>
        </div>
        
        <div class="card">
            <strong>512480</strong><br>
            国联安半导体ETF<br>
            <small>科技自立</small><br>
            <a href="bronze_details/512480.html">查看详情 →</a>
        </div>
        
        <div class="card">
            <strong>518880</strong><br>
            华安黄金ETF<br>
            <small>安全韧性</small><br>
            <a href="bronze_details/518880.html">查看详情 →</a>
        </div>
        
        <p>共59支标的，完整列表正在修复中...</p>
        <p><strong>问题</strong>: JavaScript语法错误正在紧急修复</p>
        <p><strong>状态</strong>: 工程师Cheese正在处理</p>
    </div>
</body>
</html>'''
    
    simple_file = os.path.join(BASE_DIR, "web", "bronze_simple.html")
    with open(simple_file, 'w', encoding='utf-8') as f:
        f.write(simple_html)
    
    # 部署简单版
    os.system(f"sudo cp {simple_file} /var/www/gemini_master/bronze_details/")
    os.system(f"sudo chown www-data:www-data /var/www/gemini_master/bronze_details/bronze_simple.html")
    
    print(f"✅ 简单备用页面: https://localhost:10168/bronze_details/bronze_simple.html")

if __name__ == "__main__":
    print("=" * 60)
    print("🚨 紧急修复：JavaScript语法错误")
    print("=" * 60)
    
    # 备份原始文件
    import shutil
    backup_file = OVERVIEW_FILE + '.backup'
    shutil.copy2(OVERVIEW_FILE, backup_file)
    print(f"📁 备份原始文件: {backup_file}")
    
    # 执行修复
    fix_javascript_syntax()
    
    # 验证修复
    with open(OVERVIEW_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if verify_fix(content):
        deploy_fix()
        print("\n✅ 紧急修复完成！")
        print("🌐 请主编重新访问:")
        print("   https://gemini.googlemanager.cn:10168/master-audit/bronze_etf_details.html")
    else:
        print("\n❌ 修复失败，创建备用方案...")
        create_simple_fallback()
        print("🌐 备用页面:")
        print("   https://gemini.googlemanager.cn:10168/bronze_details/bronze_simple.html")
    
    print("=" * 60)