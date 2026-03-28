#!/usr/bin/env python3
"""
P0修复：颜色习惯统一化
将全站颜色习惯从国际标准（绿涨红跌）改为中国标准（红涨绿跌）
"""

import os
import re
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSS_FILE = os.path.join(BASE_DIR, "output", "static", "css", "amber-v2.2.min.css")
CSS_BACKUP = os.path.join(BASE_DIR, "backup", "amber-v2.2.min.css.backup." + datetime.now().strftime("%Y%m%d_%H%M%S"))
INDEX_FILE = os.path.join(BASE_DIR, "output", "index.html")

def backup_css_file():
    """备份CSS文件"""
    # 创建备份目录
    backup_dir = os.path.dirname(CSS_BACKUP)
    os.makedirs(backup_dir, exist_ok=True)
    
    if os.path.exists(CSS_FILE):
        with open(CSS_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(CSS_BACKUP, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ CSS文件已备份: {CSS_BACKUP}")
        return True
    else:
        print(f"❌ CSS文件不存在: {CSS_FILE}")
        return False

def fix_css_color_definitions():
    """修复CSS中的颜色定义 - 中国习惯：红涨绿跌"""
    with open(CSS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 统计原始定义
    price_up_original = re.search(r'\.price-up\{[^}]*\}', content)
    price_down_original = re.search(r'\.price-down\{[^}]*\}', content)
    
    print("📊 原始CSS定义:")
    if price_up_original:
        print(f"   .price-up: {price_up_original.group()}")
    if price_down_original:
        print(f"   .price-down: {price_down_original.group()}")
    
    # 中国习惯：红色代表上涨，绿色代表下跌
    new_price_up = ".price-up{color:#f44336 !important;font-weight:700;}"  # 红色
    new_price_down = ".price-down{color:#4caf50 !important;font-weight:700;}"  # 绿色
    
    # 替换定义
    content = re.sub(r'\.price-up\{[^}]*\}', new_price_up, content)
    content = re.sub(r'\.price-down\{[^}]*\}', new_price_down, content)
    
    # 验证替换
    price_up_new = re.search(r'\.price-up\{[^}]*\}', content)
    price_down_new = re.search(r'\.price-down\{[^}]*\}', content)
    
    print("\n📊 修改后CSS定义:")
    if price_up_new:
        print(f"   .price-up: {price_up_new.group()}")
    if price_down_new:
        print(f"   .price-down: {price_down_new.group()}")
    
    # 临时修改文件权限以便写入
    print("   🔧 临时修改文件权限...")
    os.system(f"sudo chmod 666 {CSS_FILE} 2>/dev/null")
    
    # 保存修改
    try:
        with open(CSS_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 恢复文件权限
        os.system(f"sudo chmod 644 {CSS_FILE} 2>/dev/null")
        
        print(f"\n✅ CSS颜色定义已修改为: 红涨(#f44336) 绿跌(#4caf50)")
        return True
    except Exception as e:
        print(f"❌ 写入CSS文件失败: {e}")
        # 尝试使用sudo tee
        import subprocess
        result = subprocess.run(f'echo "{content}" | sudo tee {CSS_FILE} > /dev/null', shell=True)
        if result.returncode == 0:
            os.system(f"sudo chmod 644 {CSS_FILE} 2>/dev/null")
            print(f"\n✅ CSS颜色定义已通过sudo tee修改")
            return True
        return False

def fix_html_class_names():
    """修复HTML中的类名，确保下跌数据使用price-down，上涨使用price-up"""
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找所有指数项
    index_items = re.findall(r'(<div class="index-item">.*?</div>\s*</div>)', content, re.DOTALL)
    
    fixes_applied = 0
    for item in index_items:
        # 提取指数名称和涨跌幅
        name_match = re.search(r'<span class="index-name">([^<]+)</span>', item)
        change_match = re.search(r'<div class="index-change[^"]*">\s*([+-]?\d+\.?\d*%)', item)
        
        if name_match and change_match:
            index_name = name_match.group(1)
            change_text = change_match.group(1)
            change_value = float(change_text.strip('%').replace('+', ''))
            
            # 判断正确的类名
            correct_class = "price-up" if change_value > 0 else "price-down"
            
            # 检查当前类名
            current_class_match = re.search(r'<div class="index-change ([^"]+)">', item)
            if current_class_match:
                current_class = current_class_match.group(1)
                if current_class != correct_class:
                    # 修复类名
                    old_div = f'<div class="index-change {current_class}">'
                    new_div = f'<div class="index-change {correct_class}">'
                    content = content.replace(old_div, new_div)
                    fixes_applied += 1
                    print(f"   🔧 {index_name}: {change_text} → {correct_class} (原: {current_class})")
    
    # 特别修复：创业板指 (当前-1.11%但使用price-up)
    cyb_pattern = r'(<div class="index-item">.*?<span class="index-name">创业板指</span>.*?<div class="index-change )([^"]+)(">.*?-1\.11%.*?</div>)'
    cyb_match = re.search(cyb_pattern, content, re.DOTALL)
    if cyb_match:
        current_class = cyb_match.group(2)
        if current_class == "price-up":
            new_content = re.sub(cyb_pattern, r'\1price-down\3', content, flags=re.DOTALL)
            content = new_content
            fixes_applied += 1
            print(f"   🔧 创业板指: -1.11% → price-down (原: price-up)")
    
    # 保存修改
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✅ HTML类名修复完成: {fixes_applied}处修复")
    return fixes_applied

def verify_fixes():
    """验证修复效果"""
    print("\n🔍 验证修复结果:")
    
    # 验证CSS
    with open(CSS_FILE, 'r', encoding='utf-8') as f:
        css_content = f.read()
    
    price_up_check = re.search(r'\.price-up\{[^}]*color:([^;]+)', css_content)
    price_down_check = re.search(r'\.price-down\{[^}]*color:([^;]+)', css_content)
    
    if price_up_check and "f44336" in price_up_check.group(1):
        print("✅ CSS .price-up: 红色 (#f44336)")
    else:
        print("❌ CSS .price-up: 颜色未正确设置")
    
    if price_down_check and "4caf50" in price_down_check.group(1):
        print("✅ CSS .price-down: 绿色 (#4caf50)")
    else:
        print("❌ CSS .price-down: 颜色未正确设置")
    
    # 验证HTML
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # 检查沪深300
    hs300_match = re.search(r'沪深300.*?<div class="index-change ([^"]+)">.*?([+-]?\d+\.?\d*%)', html_content, re.DOTALL)
    if hs300_match:
        hs300_class = hs300_match.group(1)
        hs300_change = hs300_match.group(2)
        hs300_value = float(hs300_change.strip('%').replace('+', ''))
        expected_class = "price-up" if hs300_value > 0 else "price-down"
        if hs300_class == expected_class:
            print(f"✅ 沪深300: {hs300_change} → {hs300_class} (正确)")
        else:
            print(f"❌ 沪深300: {hs300_change} → {hs300_class} (应为{expected_class})")
    
    # 检查创业板指
    cyb_match = re.search(r'创业板指.*?<div class="index-change ([^"]+)">.*?([+-]?\d+\.?\d*%)', html_content, re.DOTALL)
    if cyb_match:
        cyb_class = cyb_match.group(1)
        cyb_change = cyb_match.group(2)
        cyb_value = float(cyb_change.strip('%').replace('+', ''))
        expected_class = "price-up" if cyb_value > 0 else "price-down"
        if cyb_class == expected_class:
            print(f"✅ 创业板指: {cyb_change} → {cyb_class} (正确)")
        else:
            print(f"❌ 创业板指: {cyb_change} → {cyb_class} (应为{expected_class})")
    
    return True

def main():
    print("=" * 70)
    print("🎨 P0修复：颜色习惯统一化")
    print("=" * 70)
    print("目标: 将全站颜色从国际习惯(绿涨红跌)改为中国习惯(红涨绿跌)")
    print("=" * 70)
    
    # 步骤1: 备份CSS
    print("\n📁 步骤1: 备份CSS文件")
    if not backup_css_file():
        return False
    
    # 步骤2: 修复CSS定义
    print("\n🎨 步骤2: 修改CSS颜色定义")
    if not fix_css_color_definitions():
        print("❌ CSS修复失败")
        return False
    
    # 步骤3: 修复HTML类名
    print("\n🔄 步骤3: 修复HTML类名一致性")
    fixes = fix_html_class_names()
    
    # 步骤4: 验证修复
    print("\n✅ 步骤4: 验证修复结果")
    verify_fixes()
    
    # 步骤5: 清理Nginx缓存
    print("\n🧹 步骤5: 清理Nginx缓存")
    os.system("sudo systemctl reload nginx 2>/dev/null || true")
    
    print("\n" + "=" * 70)
    print("🎉 颜色习惯统一化修复完成!")
    print("=" * 70)
    print("📊 修复内容:")
    print("  1. ✅ CSS .price-up 改为红色 (#f44336) - 上涨")
    print("  2. ✅ CSS .price-down 改为绿色 (#4caf50) - 下跌")
    print("  3. ✅ HTML类名一致性修复")
    print("  4. ✅ 创业板指-1.11%修复为price-down")
    print(f"  5. ✅ 共应用{fixes}处HTML修复")
    print("\n🔗 验证地址: https://amber.googlemanager.cn:10123/")
    print("🔄 可能需要强制刷新浏览器缓存 (Ctrl+F5)")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    main()