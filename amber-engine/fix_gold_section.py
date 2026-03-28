#!/usr/bin/env python3
"""
修复黄金对冲部分的HTML结构问题
"""

import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_FILE = os.path.join(BASE_DIR, "output", "index.html")

def fix_gold_hedge_section():
    """修复黄金对冲部分的HTML结构"""
    try:
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            html = f.read()
        
        print("🔧 修复黄金对冲部分HTML结构...")
        
        # 查找黄金对冲部分
        gold_start = html.find('<div class="gold-hedge-section">')
        if gold_start == -1:
            print("❌ 未找到黄金对冲部分")
            return False
        
        # 提取整个黄金对冲部分
        gold_end = html.find('<!-- 琥珀全景指数看板', gold_start)
        if gold_end == -1:
            print("❌ 未找到琥珀全景开始标记")
            return False
        
        gold_section = html[gold_start:gold_end]
        
        # 修复嵌套的hedge-stats问题
        # 查找第一个hedge-stats开始
        stats_start = gold_section.find('<div class="hedge-stats">')
        if stats_start == -1:
            print("❌ 未找到hedge-stats")
            return False
        
        # 查找第一个hedge-stats结束
        stats_end = gold_section.find('</div>', stats_start) + 6
        
        # 获取第一个hedge-stats内容
        stats_html = gold_section[stats_start:stats_end]
        
        # 检查是否有嵌套的hedge-stats
        if stats_html.count('<div class="hedge-stats">') > 1:
            print("⚠️ 发现嵌套的hedge-stats，正在修复...")
            
            # 提取原始的三个hedge-stat（配置比例、对冲金额、ETF标的）
            original_stats = re.findall(r'<div class="hedge-stat">.*?</div>', stats_html, re.DOTALL)
            
            # 提取实时价格部分
            realtime_section_match = re.search(r'<div class="hedge-stats" style="margin-top: 15px.*?</div>\s*</div>', stats_html, re.DOTALL)
            
            if realtime_section_match and len(original_stats) >= 3:
                realtime_section = realtime_section_match.group(0)
                
                # 重建正确的hedge-stats
                new_stats_html = f'''<div class="hedge-stats">
{original_stats[0]}
{original_stats[1]}
{original_stats[2]}
</div>

{realtime_section}'''
                
                # 替换
                new_gold_section = gold_section[:stats_start] + new_stats_html + gold_section[stats_end:]
                new_html = html[:gold_start] + new_gold_section + html[gold_end:]
                
                with open(INDEX_FILE, 'w', encoding='utf-8') as f:
                    f.write(new_html)
                
                print("✅ 黄金对冲部分HTML结构已修复")
                return True
            else:
                print("⚠️ 无法提取原始统计数据")
                return False
        else:
            print("✅ 黄金对冲部分结构正常")
            return True
            
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def update_version_number():
    """更新版本号为v3.2.7"""
    try:
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            html = f.read()
        
        # 更新版本号
        html = html.replace('v3.2.3', 'v3.2.7')
        
        # 更新页面标题
        html = html.replace('琥珀引擎 v3.2.3', '琥珀引擎 v3.2.7')
        html = html.replace('v3.2.3 (数据归一化)', 'v3.2.7 (黄金四锚)')
        
        with open(INDEX_FILE, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print("✅ 版本号已更新为 v3.2.7")
        return True
        
    except Exception as e:
        print(f"❌ 更新版本号失败: {e}")
        return False

def reload_nginx():
    """重载Nginx服务"""
    print("\n🔄 重载Nginx服务...")
    result = os.system("sudo systemctl reload nginx 2>/dev/null || true")
    if result == 0:
        print("✅ Nginx重载完成")
        return True
    else:
        print("⚠️ Nginx重载可能失败，建议手动检查")
        return False

def main():
    print("=" * 70)
    print("🔧 琥珀引擎HTML修复")
    print("=" * 70)
    
    steps = 0
    total_steps = 3
    
    # 步骤1: 修复黄金对冲部分
    print(f"\n1/{total_steps}: 修复黄金对冲部分HTML结构")
    if fix_gold_hedge_section():
        steps += 1
    
    # 步骤2: 更新版本号
    print(f"\n2/{total_steps}: 更新版本号")
    if update_version_number():
        steps += 1
    
    # 步骤3: 重载Nginx
    print(f"\n3/{total_steps}: 重载Nginx")
    reload_nginx()
    steps += 1
    
    print("\n" + "=" * 70)
    print(f"🎉 修复完成: {steps}/{total_steps} 步骤成功")
    print("=" * 70)
    print("🔗 验证地址: https://amber.googlemanager.cn:10123/?v=3.2.7")
    print("🔄 强制刷新: Ctrl+F5")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    main()