#!/usr/bin/env python3
"""
更新琥珀引擎今日数据
"""

import os
import re
import sys
from datetime import datetime
import tushare as ts

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_FILE = os.path.join(BASE_DIR, "output", "index.html")
TUSHARE_TOKEN = "9e32ef28eac05c5fbb11e6f02a50da903def70f94b3018e93340568b"

def get_index_data(today):
    """获取指数数据"""
    os.environ['TUSHARE_TOKEN'] = TUSHARE_TOKEN
    pro = ts.pro_api()
    
    indices = [
        {"ts_code": "000300.SH", "name": "沪深300"},
        {"ts_code": "399006.SZ", "name": "创业板指"}
    ]
    
    data = {}
    for idx in indices:
        try:
            df = pro.index_daily(ts_code=idx["ts_code"], trade_date=today)
            if not df.empty:
                close_price = float(df.iloc[0]['close'])
                pct_chg = float(df.iloc[0]['pct_chg'])
                data[idx["name"]] = {
                    "price": close_price,
                    "change": pct_chg,
                    "ts_code": idx["ts_code"]
                }
                print(f"✅ {idx['name']}: {close_price}, {pct_chg}%")
            else:
                print(f"⚠️ {idx['name']}: 无今日数据")
        except Exception as e:
            print(f"❌ {idx['name']} 获取失败: {e}")
    
    return data

def update_html(index_data):
    """更新HTML文件"""
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 更新时间戳
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    old_time_pattern = r'数据更新: \d{4}-\d{2}-\d{2} \d{2}:\d{2} \(北京时间\)'
    new_time_text = f'数据更新: {current_time} (北京时间) | 🎯 今日数据已更新'
    content = re.sub(old_time_pattern, new_time_text, content)
    
    # 更新沪深300
    if "沪深300" in index_data:
        hs300 = index_data["沪深300"]
        # 寻找沪深300的index-item
        pattern = r'(<div class="index-item">\s*<div class="index-header">\s*<span class="index-name">沪深300</span>.*?<div class="index-value">)[^<]*(</div>.*?<div class="index-change[^"]*">)[^<]*(</div>.*?</div>)'
        
        def replace_hs300(match):
            prefix = match.group(1)
            middle = match.group(2)
            suffix = match.group(3)
            price = f"{hs300['price']:.2f}"
            change_class = "price-up" if hs300['change'] > 0 else "price-down"
            change_text = f"{hs300['change']:+.2f}%"
            return f"{prefix}{price}{middle}{change_text}{suffix}"
        
        content = re.sub(pattern, replace_hs300, content, flags=re.DOTALL)
        print("✅ 沪深300数据已更新")
    
    # 更新创业板指
    if "创业板指" in index_data:
        cyb = index_data["创业板指"]
        pattern = r'(<div class="index-item">\s*<div class="index-header">\s*<span class="index-name">创业板指</span>.*?<div class="index-value">)[^<]*(</div>.*?<div class="index-change[^"]*">)[^<]*(</div>.*?</div>)'
        
        def replace_cyb(match):
            prefix = match.group(1)
            middle = match.group(2)
            suffix = match.group(3)
            price = f"{cyb['price']:.2f}"
            change_class = "price-up" if cyb['change'] > 0 else "price-down"
            change_text = f"{cyb['change']:+.2f}%"
            return f"{prefix}{price}{middle}{change_text}{suffix}"
        
        content = re.sub(pattern, replace_cyb, content, flags=re.DOTALL)
        print("✅ 创业板指数据已更新")
    
    # 保存文件
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ HTML文件已更新: {INDEX_FILE}")
    return True

def main():
    print("=" * 70)
    print("🚀 琥珀引擎今日数据更新")
    print("=" * 70)
    
    today = datetime.now().strftime("%Y%m%d")
    print(f"📅 今日日期: {today}")
    
    # 获取数据
    index_data = get_index_data(today)
    
    if not index_data:
        print("⚠️ 未获取到任何指数数据，仅更新时间戳")
    
    # 更新HTML
    success = update_html(index_data)
    
    if success:
        print("\n" + "=" * 70)
        print("🎉 琥珀引擎数据更新完成")
        print("=" * 70)
        print(f"🔗 访问地址: https://amber.googlemanager.cn:10123/")
        print(f"📊 更新内容:")
        for name, data in index_data.items():
            print(f"   {name}: {data['price']:.2f} ({data['change']:+.2f}%)")
        print(f"🕒 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
    else:
        print("\n❌ 更新失败")

if __name__ == "__main__":
    main()