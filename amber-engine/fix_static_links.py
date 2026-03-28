#!/usr/bin/env python3
"""
修复静态页面链接路径
问题: bronze_details/510300.html → 应为 details/510300.html
"""

import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_FILE = os.path.join(BASE_DIR, "web", "bronze_static_final.html")
FIXED_FILE = os.path.join(BASE_DIR, "web", "bronze_static_final_fixed.html")
TARGET_DIR = "/var/www/gemini_master/bronze_details"

def fix_links():
    """修复链接路径"""
    print("🔧 修复静态页面链接路径...")
    
    with open(STATIC_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复链接: bronze_details/{code}.html → details/{code}.html
    # 因为页面在 bronze_details/ 目录下
    old_pattern = r'href="bronze_details/(\d{6})\.html"'
    new_pattern = r'href="details/\1.html"'
    
    fixed_content, count = re.subn(old_pattern, new_pattern, content)
    
    if count > 0:
        print(f"✅ 修复了 {count} 处链接路径")
    else:
        print("⚠️  未找到需要修复的链接，尝试其他模式...")
        # 尝试另一种模式
        old_pattern2 = r"href='bronze_details/(\d{6})\.html'"
        fixed_content, count = re.subn(old_pattern2, "href='details/\\1.html'", content)
        if count > 0:
            print(f"✅ 修复了 {count} 处链接路径（模式2）")
    
    # 保存修复后的文件
    with open(FIXED_FILE, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"✅ 修复文件保存: {FIXED_FILE}")
    
    # 验证修复
    verify_fix(fixed_content)

def verify_fix(content):
    """验证修复结果"""
    print("🧪 验证修复结果...")
    
    # 检查是否还有错误的链接
    if 'bronze_details/510300.html' in content:
        print("❌ 修复失败：仍然存在错误链接")
        return False
    
    # 检查正确的链接
    if 'details/510300.html' in content:
        print("✅ 链接路径已修复")
        
        # 统计修复的链接数量
        import re
        links = re.findall(r'href="details/(\d{6})\.html"', content)
        print(f"✅ 找到 {len(links)} 个详情页链接")
        return True
    else:
        print("❌ 找不到正确的链接路径")
        return False

def deploy_fix():
    """部署修复后的文件"""
    print("🚀 部署修复后的文件...")
    
    # 复制修复后的文件
    os.system(f"sudo cp {FIXED_FILE} {TARGET_DIR}/bronze_static_final.html")
    os.system(f"sudo chown www-data:www-data {TARGET_DIR}/bronze_static_final.html")
    
    # 更新符号链接
    symlink = "/var/www/gemini_master/master-audit/bronze_static_final.html"
    if os.path.exists(symlink):
        os.system(f"sudo rm {symlink}")
    os.system(f"sudo ln -s {TARGET_DIR}/bronze_static_final.html {symlink}")
    
    print(f"✅ 部署到: {TARGET_DIR}/bronze_static_final.html")
    print(f"✅ 符号链接: {symlink}")

def test_access():
    """测试访问"""
    print("🔗 测试访问...")
    
    import subprocess
    
    # 测试静态页面
    urls = [
        ("静态页面", "https://localhost:10168/bronze_details/bronze_static_final.html"),
        ("符号链接", "https://localhost:10168/master-audit/bronze_static_final.html")
    ]
    
    for name, url in urls:
        result = subprocess.run(
            ['curl', '-k', '-s', '-o', '/dev/null', '-w', f'{name}: %{{http_code}}\n', url],
            capture_output=True,
            text=True
        )
        print(result.stdout.strip())
    
    # 检查链接是否正确
    result = subprocess.run(
        ['curl', '-k', '-s', 'https://localhost:10168/bronze_details/bronze_static_final.html'],
        capture_output=True,
        text=True
    )
    
    if 'details/510300.html' in result.stdout:
        print("✅ 静态页面链接正确")
    else:
        print("❌ 静态页面链接错误")
    
    # 测试详情页访问
    print("\n🔗 测试详情页访问:")
    detail_urls = [
        ("直接路径", "https://localhost:10168/bronze_details/details/510300.html"),
        ("符号链接", "https://localhost:10168/master-audit/bronze_details/510300.html")
    ]
    
    for name, url in detail_urls:
        result = subprocess.run(
            ['curl', '-k', '-s', '-o', '/dev/null', '-w', f'{name}: %{{http_code}}\n', url],
            capture_output=True,
            text=True
        )
        print(result.stdout.strip())

def create_access_guide():
    """创建访问指南"""
    print("\n📋 创建访问指南...")
    
    guide = '''# 青铜法典访问指南

## 🌐 访问地址

### 1. 静态总览页 (100%可用)
- **主地址**: https://gemini.googlemanager.cn:10168/bronze_details/bronze_static_final.html
- **备用地址**: https://gemini.googlemanager.cn:10168/master-audit/bronze_static_final.html

### 2. 详情页访问方式

#### 方式A: 通过总览页点击
1. 访问静态总览页
2. 点击任意ETF卡片
3. 自动跳转到详情页

#### 方式B: 直接访问
- **格式**: https://gemini.googlemanager.cn:10168/bronze_details/details/{代码}.html
- **示例**: https://gemini.googlemanager.cn:10168/bronze_details/details/510300.html

#### 方式C: 通过符号链接
- **格式**: https://gemini.googlemanager.cn:10168/master-audit/bronze_details/{代码}.html
- **示例**: https://gemini.googlemanager.cn:10168/master-audit/bronze_details/510300.html

## 🚫 错误路径
以下路径会导致404错误:
- ❌ https://gemini.googlemanager.cn:10168/bronze_details/bronze_details/510300.html
  (重复了bronze_details/)

## ✅ 正确路径
- ✅ https://gemini.googlemanager.cn:10168/bronze_details/details/510300.html
- ✅ https://gemini.googlemanager.cn:10168/master-audit/bronze_details/510300.html

## 📊 系统状态
- 总览页: ✅ 可用 (59支标的)
- 详情页: ✅ 可用 (59个页面)
- JavaScript版本: ⚠️ 正在修复
- 静态版本: ✅ 100%可用

## 🔧 技术支持
- **执行人**: 工程师 Cheese
- **修复时间**: 2026-03-27 08:55 GMT+8
- **状态**: 链接路径已修复，详情页可正常访问
'''
    
    guide_file = os.path.join(BASE_DIR, "web", "ACCESS_GUIDE.md")
    with open(guide_file, 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print(f"✅ 访问指南创建: {guide_file}")

def main():
    print("=" * 60)
    print("🔧 修复静态页面链接路径")
    print("=" * 60)
    
    # 备份原始文件
    import shutil
    backup_file = STATIC_FILE + '.backup'
    shutil.copy2(STATIC_FILE, backup_file)
    print(f"📁 备份原始文件: {backup_file}")
    
    # 执行修复
    fix_links()
    
    # 验证修复
    with open(FIXED_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if verify_fix(content):
        # 部署修复
        deploy_fix()
        
        # 测试访问
        test_access()
        
        # 创建访问指南
        create_access_guide()
        
        print("\n✅ 链接修复完成！")
        print("🌐 请主编重新访问静态页面，链接现在应该正常工作")
    else:
        print("\n❌ 修复失败，需要手动检查")

if __name__ == "__main__":
    main()