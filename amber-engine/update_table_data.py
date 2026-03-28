#!/usr/bin/env python3
"""
临时更新表格数据脚本
用于更新表格形式的指数数据
"""

import os
import re
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_FILE = os.path.join(BASE_DIR, "output", "index.html")
CACHE_FILE = os.path.join(BASE_DIR, "output", "static", "data", "unified_data_cache.json")

def calculate_color_class(change_pct: float) -> str:
    """计算颜色类名 - 中国习惯：红涨绿跌"""
    return "price-up" if change_pct > 0 else "price-down"

def update_table_data():
    """更新表格数据"""
    print("📊 更新表格数据...")
    
    # 读取缓存数据
    if not os.path.exists(CACHE_FILE):
        print("❌ 缓存文件不存在")
        return False
    
    with open(CACHE_FILE, 'r') as f:
        cache_data = json.load(f)
    
    indices_data = cache_data.get('indices', {})
    if not indices_data:
        print("⚠️ 缓存中无指数数据")
        return False
    
    # 读取页面内容
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    updates_applied = 0
    
    # 更新沪深300
    hs300_data = indices_data.get("沪深300")
    if hs300_data:
        # 点位更新
        price_pattern = r'(<tr class="index-row" data-index="沪深300"[^>]*>.*?<td class="col-price">)[^<]*(</td>)'
        price = f"{hs300_data['close']:.2f}" if isinstance(hs300_data['close'], float) else str(hs300_data['close'])
        content, count1 = re.subn(price_pattern, rf'\g<1>{price}\2', content, flags=re.DOTALL)
        
        # 涨跌幅更新
        change_pct = hs300_data['pct_chg']
        change_class = calculate_color_class(change_pct)
        change_text = f"{change_pct:+.2f}%"
        
        change_pattern = r'(<tr class="index-row" data-index="沪深300"[^>]*>.*?<td class="col-change[^"]*">)[^<]*(</td>)'
        content, count2 = re.subn(change_pattern, rf'\g<1>{change_text}\2', content, flags=re.DOTALL)
        
        # 更新颜色类
        class_pattern = r'(<tr class="index-row" data-index="沪深300"[^>]*>.*?<td class="col-change )price-(?:up|down)(">)'
        content, count3 = re.subn(class_pattern, rf'\g<1>{change_class}\2', content, flags=re.DOTALL)
        
        if count1 > 0 or count2 > 0 or count3 > 0:
            updates_applied += 1
            print(f"  🔧 更新 沪深300: {price} ({change_text})")
    
    # 更新创业板指
    cyb_data = indices_data.get("创业板指")
    if cyb_data:
        # 点位更新
        price_pattern = r'(<tr class="index-row" data-index="创业板指"[^>]*>.*?<td class="col-price">)[^<]*(</td>)'
        price = f"{cyb_data['close']:.2f}" if isinstance(cyb_data['close'], float) else str(cyb_data['close'])
        content, count1 = re.subn(price_pattern, rf'\g<1>{price}\2', content, flags=re.DOTALL)
        
        # 涨跌幅更新
        change_pct = cyb_data['pct_chg']
        change_class = calculate_color_class(change_pct)
        change_text = f"{change_pct:+.2f}%"
        
        change_pattern = r'(<tr class="index-row" data-index="创业板指"[^>]*>.*?<td class="col-change[^"]*">)[^<]*(</td>)'
        content, count2 = re.subn(change_pattern, rf'\g<1>{change_text}\2', content, flags=re.DOTALL)
        
        # 更新颜色类
        class_pattern = r'(<tr class="index-row" data-index="创业板指"[^>]*>.*?<td class="col-change )price-(?:up|down)(">)'
        content, count3 = re.subn(class_pattern, rf'\g<1>{change_class}\2', content, flags=re.DOTALL)
        
        if count1 > 0 or count2 > 0 or count3 > 0:
            updates_applied += 1
            print(f"  🔧 更新 创业板指: {price} ({change_text})")
    
    # 更新表格更新时间
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    time_pattern = r'(<span class="table-update-time">更新: )[^<]*(</span>)'
    content, time_count = re.subn(time_pattern, rf'\g<1>{current_time} (北京时间)\2', content)
    
    if time_count > 0:
        print(f"  🕒 更新表格时间: {current_time}")
    
    # 写入文件
    try:
        with open(INDEX_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 表格数据更新完成: {updates_applied}处更新")
        return True
    except PermissionError:
        print("⚠️ 权限不足，使用sudo tee")
        import subprocess
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        result = subprocess.run(f'sudo tee {INDEX_FILE} < {tmp_path} > /dev/null', shell=True)
        os.unlink(tmp_path)
        
        if result.returncode != 0:
            print("❌ sudo tee写入失败")
            return False
        
        print(f"✅ 表格数据更新完成 (使用sudo): {updates_applied}处更新")
        return True

def main():
    """主函数"""
    print("=" * 70)
    print("📊 更新表格数据")
    print("=" * 70)
    
    success = update_table_data()
    
    if success:
        print("\n✅ 更新完成!")
        print("📋 更新内容:")
        print("  1. ✅ 更新表格中的指数点位数据")
        print("  2. ✅ 更新表格中的涨跌幅数据")
        print("  3. ✅ 更新颜色类名 (红涨绿跌)")
        print("  4. ✅ 更新表格时间戳")
        print(f"\n🔗 验证地址: https://amber.googlemanager.cn:10123/")
    else:
        print("\n❌ 更新失败")
    
    return success

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)